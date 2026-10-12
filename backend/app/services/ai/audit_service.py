"""
AuditService — multi-stage legal risk analysis over extracted PDF chunks.

A single mega-prompt produces shallow results and frequently truncates, so the
audit runs as four focused LLM stages that execute concurrently:

  1. Overview   — contract type, executive summary, key takeaways, top risks,
                  and standard protections that are missing.
  2. Clauses    — classification of every detected clause into one of the seven
                  core legal categories, with a severity tag, the verbatim
                  snippet, a plain-English explanation and a recommendation.
  3. Entities   — parties, key dates, financial values and jurisdiction.
  4. Sections   — a section-by-section breakdown for the accordion UI.

Each stage retries across a fallback chain of Gemini models, so a 429/503 on
one model does not fail the audit. A stage that ultimately fails degrades to an
empty result rather than taking the whole upload down with it.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import logger

# Fallback chain: try each model in order. The `-latest` alias leads so the
# chain keeps working when a pinned generation is retired by Google.
GEMINI_MODELS = [
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-pro-latest",
]
MAX_RETRIES = 2
RETRY_DELAY = 3  # seconds
# Hard ceiling per LLM call. Without this a stalled request would hang the
# upload request forever, since the SDK has no default timeout.
STAGE_TIMEOUT = float(os.getenv("AUDIT_STAGE_TIMEOUT", "90"))

# How many stages may call the API at once. The Gemini free tier is metered per
# day *and* per minute, and firing all four stages simultaneously trips the
# per-minute limit immediately — which then costs retries, which cost more
# quota. Two at a time is the sweet spot; raise it on a paid tier.
STAGE_CONCURRENCY = max(1, int(os.getenv("AUDIT_STAGE_CONCURRENCY", "2")))

# Transient failures worth retrying on the same model. Matched as whole words so
# that, for example, "generateContent" does not match "rate".
_RETRYABLE = re.compile(
    r"\b(?:429|500|502|503|504|unavailable|overloaded|rate limit|"
    r"rate_limit|ratelimit|timeout|timed out|deadline)\b",
    re.IGNORECASE,
)

# A *daily* quota exhaustion is not worth retrying: every retry consumes another
# request from the same exhausted bucket and cannot possibly succeed until the
# quota window rolls over. Google signals this with a PerDay quota id.
_DAILY_QUOTA = re.compile(
    r"(?:PerDay|per day|requests per day|GenerateRequestsPerDay)", re.IGNORECASE
)

# Google returns "Please retry in 38.86s" / RetryInfo on a per-minute throttle.
_RETRY_AFTER = re.compile(r"retry in (\d+(?:\.\d+)?)s", re.IGNORECASE)

# Permanent failures: retrying or waiting cannot help, so move on immediately.
_NON_RETRYABLE = re.compile(
    r"\b(?:400|401|403|404|not found|not_found|permission denied|"
    r"permission_denied|invalid[ _]api[ _]key|unauthenticated)\b",
    re.IGNORECASE,
)

# The seven core clause categories the auditor classifies into. These strings
# are the contract with the frontend's category filter chips and colour map.
CLAUSE_CATEGORIES = [
    "Termination",
    "Payment",
    "Liability",
    "Indemnification",
    "Confidentiality",
    "Governing Law",
    "IP Rights",
]

# Loose synonyms → canonical category, for when the model improvises.
_CATEGORY_ALIASES = {
    "termination": "Termination",
    "termination & renewal": "Termination",
    "renewal": "Termination",
    "payment": "Payment",
    "payment & financial terms": "Payment",
    "financial": "Payment",
    "fees": "Payment",
    "liability": "Liability",
    "limitation of liability": "Liability",
    "indemnification": "Indemnification",
    "indemnity": "Indemnification",
    "hold harmless": "Indemnification",
    "confidentiality": "Confidentiality",
    "non-disclosure": "Confidentiality",
    "nda": "Confidentiality",
    "data privacy": "Confidentiality",
    "governing law": "Governing Law",
    "dispute resolution": "Governing Law",
    "jurisdiction": "Governing Law",
    "arbitration": "Governing Law",
    "ip rights": "IP Rights",
    "intellectual property": "IP Rights",
    "intellectual property rights": "IP Rights",
    "ip": "IP Rights",
}

SEVERITIES = ["Low", "Medium", "High", "Critical"]

# Points deducted from a perfect 100 for each finding, by severity.
_SEVERITY_WEIGHT = {"Critical": 25, "High": 15, "Medium": 8, "Low": 3}
_MISSING_CLAUSE_WEIGHT = 4


# ─────────────────────────────────────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────────────────────────────────────
_JSON_RULES = (
    "Respond with valid JSON only — no markdown fences, no commentary before or "
    "after the JSON. Use double quotes for all keys and string values."
)

OVERVIEW_PROMPT = """You are a senior contracts attorney reviewing a legal document.

DOCUMENT EXCERPTS:
{context}

---
TASK
1. Identify the contract type (e.g. "Master Services Agreement", "Non-Disclosure Agreement", "Employment Agreement", "Lease", "SaaS Subscription Agreement").
2. Write a 3-5 sentence executive summary covering the document's purpose, the parties' core obligations, and its overall risk profile.
3. List 4-6 key takeaways — the concrete commercial facts a busy executive must know (notice periods, payment terms, liability caps, renewal mechanics). Each takeaway is one sentence stating the actual value found in the text.
4. List the top risks, ambiguities and unfavourable terms. For each: a short title, a severity of "Critical", "High", "Medium" or "Low", a 1-2 sentence description of the risk and its business impact, the page number it appears on, and a short verbatim quote from the excerpts that evidences it.
5. List standard legal protections that appear to be MISSING from this document (e.g. limitation of liability, indemnification, dispute resolution, governing law, data-protection terms, force majeure, assignment restrictions).

{json_rules}

SCHEMA
{{
  "contract_type": "string",
  "executive_summary": "string",
  "key_takeaways": ["string"],
  "risks": [
    {{"title": "string", "severity": "Critical|High|Medium|Low", "description": "string", "page_number": 1, "snippet": "string"}}
  ],
  "missing_clauses": ["string"]
}}
"""

CLAUSES_PROMPT = """You are a legal clause classification engine.

DOCUMENT EXCERPTS (each excerpt is tagged with its page and section):
{context}

---
TASK
Identify every distinct clause present in the excerpts and classify it into exactly one of these categories:
{categories}

For each clause return:
- "category": one of the categories above, verbatim.
- "title": a short descriptive name for the clause (e.g. "Termination for Convenience").
- "page_number": the page the clause appears on, taken from the excerpt tag.
- "section": the section reference from the excerpt tag (e.g. "Sec 5.4"), or "" if unknown.
- "risk_level": "Critical", "High", "Medium" or "Low" — how unfavourable or dangerous this clause is as drafted.
- "snippet": a verbatim quote of the operative clause language, max 320 characters, copied exactly from the excerpts.
- "explanation": plain English, no legalese, 1-2 sentences explaining what this clause actually means for the party reviewing it.
- "recommendation": one sentence of concrete advice — what to negotiate, clarify or accept.

Only report clauses that genuinely appear in the excerpts. Do not invent clauses. Return at most 12 clauses, prioritising the highest-risk ones.

{json_rules}

SCHEMA
{{
  "clauses": [
    {{"category": "string", "title": "string", "page_number": 1, "section": "string",
      "risk_level": "Critical|High|Medium|Low", "snippet": "string",
      "explanation": "string", "recommendation": "string"}}
  ]
}}
"""

ENTITIES_PROMPT = """You are a legal data extraction engine.

DOCUMENT EXCERPTS:
{context}

---
TASK
Extract the structured key entities below. Use only values that actually appear in the excerpts. If a value is not present, omit that item entirely rather than guessing.

- "parties": every contracting organisation or individual, with "name", "role" (e.g. "Provider", "Client", "Disclosing Party", "Employer"), "address" if stated, and "signatory" (person and title) if stated.
- "dates": key dates and timelines, each with "label" (e.g. "Effective Date", "Expiration Date", "Notice Period", "Auto-Renewal", "Payment Due"), "value" as written in the document, "page_number", "section", and a short "note" explaining its significance.
- "financials": monetary values and financial terms, each with "label" (e.g. "Contract Value", "Late Interest Penalty", "Liability Cap", "Payment Terms"), "amount" as written, "page_number", "section", and a short "detail".
- "jurisdiction": an object with "governing_law", "venue", "dispute_resolution", "page_number" and "section". Use "Not specified" for any of the three text fields absent from the document.

{json_rules}

SCHEMA
{{
  "parties": [{{"name": "string", "role": "string", "address": "string", "signatory": "string"}}],
  "dates": [{{"label": "string", "value": "string", "page_number": 1, "section": "string", "note": "string"}}],
  "financials": [{{"label": "string", "amount": "string", "page_number": 1, "section": "string", "detail": "string"}}],
  "jurisdiction": {{"governing_law": "string", "venue": "string", "dispute_resolution": "string", "page_number": 1, "section": "string"}}
}}
"""

SECTIONS_PROMPT = """You are summarising a legal document section by section.

DOCUMENT EXCERPTS (each excerpt is tagged with its page and section):
{context}

---
TASK
Produce a section-by-section breakdown of the document, in document order, covering the 4-8 most substantive sections. For each section return:
- "title": the section heading as written, prefixed with its number if it has one (e.g. "3. Payment Terms & Invoicing").
- "page_number": the page the section starts on.
- "section": the short section reference (e.g. "Sec 3.1"), or "" if unknown.
- "text_snippet": a verbatim quote of the section's most important sentence, max 240 characters.
- "key_points": 2-3 short bullet strings stating the concrete obligations or values in that section.

{json_rules}

SCHEMA
{{
  "section_summaries": [
    {{"title": "string", "page_number": 1, "section": "string",
      "text_snippet": "string", "key_points": ["string"]}}
  ]
}}
"""


class AuditService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Set when a stage hits the per-day free-tier cap, so the remaining
        # stages can stop early instead of each burning through the model chain.
        self._quota_exhausted = False

    # ────────────────────────────────────────────────────────────────────
    # LLM plumbing
    # ────────────────────────────────────────────────────────────────────
    def _get_llm(self, model_name: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=0.2,
        )

    async def _invoke_json(self, prompt: str, stage: str) -> Optional[dict]:
        """
        Send `prompt` to Gemini and parse the reply as JSON.

        Walks the model fallback chain, retrying retryable errors (429/503).
        Returns None when every model and retry has been exhausted, so the
        caller can degrade that stage instead of failing the whole audit.
        """
        if not self.api_key:
            logger.error(f"[AuditService:{stage}] GOOGLE_API_KEY is not configured.")
            return None

        last_error: Optional[Exception] = None

        for model_name in GEMINI_MODELS:
            for attempt in range(MAX_RETRIES):
                try:
                    logger.info(f"[AuditService:{stage}] {model_name} attempt {attempt + 1}")
                    response = await asyncio.wait_for(
                        self._get_llm(model_name).ainvoke(prompt), timeout=STAGE_TIMEOUT
                    )
                    parsed = self._parse_json(response.content)
                    if parsed is not None:
                        logger.info(f"[AuditService:{stage}] ✅ parsed via {model_name}")
                        return parsed
                    logger.warning(f"[AuditService:{stage}] {model_name} returned unparseable JSON")
                except asyncio.TimeoutError:
                    last_error = TimeoutError(
                        f"{model_name} did not respond within {STAGE_TIMEOUT:.0f}s"
                    )
                    logger.warning(f"[AuditService:{stage}] {last_error}")
                    continue
                except Exception as e:
                    last_error = e
                    if self._is_daily_quota_exhausted(e):
                        # Every further attempt spends another request from an
                        # already-empty daily bucket. Stop the whole chain.
                        logger.error(
                            f"[AuditService:{stage}] daily free-tier quota exhausted "
                            f"on {model_name}; abandoning remaining models."
                        )
                        self._quota_exhausted = True
                        return None
                    if self._is_retryable(e):
                        logger.warning(f"[AuditService:{stage}] {model_name} retryable error: {e}")
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(self._retry_after(e, RETRY_DELAY))
                        continue
                    logger.warning(f"[AuditService:{stage}] {model_name} failed: {e}")
                    break  # non-retryable on this model — move to the next model

        logger.error(f"[AuditService:{stage}] all models failed. Last error: {last_error}")
        return None

    @staticmethod
    def _is_retryable(error: Exception) -> bool:
        """
        True only for transient failures.

        A retired or misspelled model returns 404, which no amount of retrying
        will fix. A *daily* quota exhaustion is worse than useless to retry:
        each attempt spends another request from the bucket that is already
        empty. Both move straight on instead.
        """
        text = str(error)
        if _NON_RETRYABLE.search(text):
            return False
        if _DAILY_QUOTA.search(text):
            return False
        return bool(_RETRYABLE.search(text))

    @staticmethod
    def _is_daily_quota_exhausted(error: Optional[Exception]) -> bool:
        """Whether this failure is the per-day free-tier cap, not a transient blip."""
        return bool(error) and bool(_DAILY_QUOTA.search(str(error)))

    @staticmethod
    def _retry_after(error: Exception, default: float) -> float:
        """
        Honour the server's own retry hint when it gives one, so a per-minute
        throttle waits exactly as long as required instead of guessing.
        """
        match = _RETRY_AFTER.search(str(error))
        if match:
            # Cap the wait so one throttled stage cannot stall the whole upload.
            return min(float(match.group(1)) + 1, 45.0)
        return default

    @staticmethod
    def _parse_json(content: Any) -> Optional[dict]:
        """Extract a JSON object from a model reply, tolerating fences and prose."""
        if not isinstance(content, str):
            content = str(content or "")
        text = content.strip()
        if not text:
            return None

        # Strip markdown fences.
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

        # Isolate the outermost JSON object.
        if not text.startswith("{"):
            start, end = text.find("{"), text.rfind("}")
            if start == -1 or end <= start:
                return None
            text = text[start:end + 1]

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Trailing commas are the most common model slip — try once more.
            repaired = re.sub(r",\s*([}\]])", r"\1", text)
            try:
                parsed = json.loads(repaired)
            except json.JSONDecodeError:
                return None
        return parsed if isinstance(parsed, dict) else None

    # ────────────────────────────────────────────────────────────────────
    # Context building
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def build_context(chunks: List[Document], limit: Optional[int] = None) -> str:
        """
        Render chunks into a tagged context block.

        Every excerpt carries its page and section so the model can cite them
        back accurately instead of inventing page numbers.
        """
        limit = limit or settings.AUDIT_CONTEXT_CHUNKS
        selected = AuditService._select_chunks(chunks, limit)

        parts = []
        for index, chunk in enumerate(selected, start=1):
            meta = chunk.metadata or {}
            page = meta.get("page_number", "?")
            section = meta.get("section_label") or meta.get("section_title") or "Unlabelled"
            parts.append(
                f"[Excerpt {index} | Page {page} | Section: {section}]\n{chunk.page_content}"
            )
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _select_chunks(chunks: List[Document], limit: int) -> List[Document]:
        """
        Pick a representative subset when a document exceeds the context budget.

        The opening pages (parties, term, payment) and the closing pages
        (liability, governing law, signatures) carry most of the legal weight,
        so take a weighted head and tail plus an even sample of the middle
        rather than truncating at the first N chunks.
        """
        if len(chunks) <= limit:
            return chunks

        head = max(1, int(limit * 0.4))
        tail = max(1, int(limit * 0.3))
        middle_budget = limit - head - tail

        middle_pool = chunks[head:len(chunks) - tail]
        if middle_budget > 0 and middle_pool:
            step = max(1, len(middle_pool) // middle_budget)
            middle = middle_pool[::step][:middle_budget]
        else:
            middle = []

        return chunks[:head] + middle + chunks[len(chunks) - tail:]

    # ────────────────────────────────────────────────────────────────────
    # Stages
    # ────────────────────────────────────────────────────────────────────
    async def _stage_overview(self, context: str) -> dict:
        result = await self._invoke_json(
            OVERVIEW_PROMPT.format(context=context, json_rules=_JSON_RULES), "overview"
        )
        return result or {}

    async def _stage_clauses(self, context: str) -> dict:
        prompt = CLAUSES_PROMPT.format(
            context=context,
            categories="\n".join(f"- {c}" for c in CLAUSE_CATEGORIES),
            json_rules=_JSON_RULES,
        )
        result = await self._invoke_json(prompt, "clauses")
        return result or {}

    async def _stage_entities(self, context: str) -> dict:
        result = await self._invoke_json(
            ENTITIES_PROMPT.format(context=context, json_rules=_JSON_RULES), "entities"
        )
        return result or {}

    async def _stage_sections(self, context: str) -> dict:
        result = await self._invoke_json(
            SECTIONS_PROMPT.format(context=context, json_rules=_JSON_RULES), "sections"
        )
        return result or {}

    # ────────────────────────────────────────────────────────────────────
    # Normalisation
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_severity(value: Any, default: str = "Medium") -> str:
        text = str(value or "").strip().lower().replace(" risk", "")
        for severity in SEVERITIES:
            if text == severity.lower():
                return severity
        if text in {"severe", "very high", "urgent"}:
            return "Critical"
        if text in {"moderate", "med"}:
            return "Medium"
        if text in {"minor", "negligible", "informational", "info"}:
            return "Low"
        return default

    @staticmethod
    def normalize_category(value: Any) -> str:
        text = str(value or "").strip()
        for category in CLAUSE_CATEGORIES:
            if text.lower() == category.lower():
                return category
        alias = _CATEGORY_ALIASES.get(text.lower())
        if alias:
            return alias
        # Substring match as a last resort: "Termination & Renewal Rights".
        for key, category in _CATEGORY_ALIASES.items():
            if key in text.lower():
                return category
        return "Other"

    @staticmethod
    def _as_page(value: Any, default: int = 1) -> int:
        try:
            page = int(str(value).strip())
            return page if page > 0 else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _as_text(value: Any, limit: int = 1200) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, tuple)):
            value = " ".join(str(v) for v in value)
        return str(value).strip()[:limit]

    @staticmethod
    def _as_str_list(value: Any, limit: int = 12) -> List[str]:
        if not isinstance(value, list):
            return []
        items = []
        for entry in value:
            if isinstance(entry, dict):
                entry = entry.get("text") or entry.get("title") or entry.get("name") or ""
            text = str(entry).strip()
            if text:
                items.append(text[:400])
        return items[:limit]

    def _normalize_risks(self, raw: Any) -> List[dict]:
        if not isinstance(raw, list):
            return []
        risks = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            title = self._as_text(entry.get("title"), 160)
            if not title:
                continue
            risks.append({
                "title": title,
                "severity": self.normalize_severity(entry.get("severity")),
                "description": self._as_text(entry.get("description"), 800)
                               or "No description provided.",
                "page_number": self._as_page(entry.get("page_number")),
                "snippet": self._as_text(entry.get("snippet"), 400),
                "section": self._as_text(entry.get("section"), 60),
            })
        return risks[:15]

    def _normalize_clauses(self, raw: Any) -> List[dict]:
        if not isinstance(raw, list):
            return []
        clauses = []
        for index, entry in enumerate(raw, start=1):
            if not isinstance(entry, dict):
                continue
            snippet = self._as_text(entry.get("snippet"), 400)
            title = self._as_text(entry.get("title"), 160)
            if not (snippet or title):
                continue
            clauses.append({
                "id": f"c{index}",
                "category": self.normalize_category(entry.get("category")),
                "title": title or "Untitled Clause",
                "page_number": self._as_page(entry.get("page_number")),
                "section": self._as_text(entry.get("section"), 60),
                "risk_level": self.normalize_severity(entry.get("risk_level"), default="Low"),
                "snippet": snippet,
                "explanation": self._as_text(entry.get("explanation"), 600),
                "recommendation": self._as_text(entry.get("recommendation"), 400),
            })
        return clauses[:14]

    def _normalize_entities(self, raw: Any) -> dict:
        raw = raw if isinstance(raw, dict) else {}

        parties = []
        for entry in raw.get("parties") or []:
            if not isinstance(entry, dict):
                continue
            name = self._as_text(entry.get("name"), 160)
            if not name:
                continue
            parties.append({
                "name": name,
                "role": self._as_text(entry.get("role"), 80) or "Party",
                "address": self._as_text(entry.get("address"), 240),
                "signatory": self._as_text(entry.get("signatory"), 120),
            })

        dates = []
        for entry in raw.get("dates") or []:
            if not isinstance(entry, dict):
                continue
            label = self._as_text(entry.get("label"), 80)
            value = self._as_text(entry.get("value"), 160)
            if not (label and value):
                continue
            dates.append({
                "label": label,
                "value": value,
                "page_number": self._as_page(entry.get("page_number")),
                "section": self._as_text(entry.get("section"), 60),
                "note": self._as_text(entry.get("note"), 240),
            })

        financials = []
        for entry in raw.get("financials") or []:
            if not isinstance(entry, dict):
                continue
            label = self._as_text(entry.get("label"), 80)
            amount = self._as_text(entry.get("amount"), 120)
            if not (label and amount):
                continue
            financials.append({
                "label": label,
                "amount": amount,
                "page_number": self._as_page(entry.get("page_number")),
                "section": self._as_text(entry.get("section"), 60),
                "detail": self._as_text(entry.get("detail"), 240),
            })

        juris_raw = raw.get("jurisdiction")
        juris_raw = juris_raw if isinstance(juris_raw, dict) else {}
        jurisdiction = {
            "governing_law": self._as_text(juris_raw.get("governing_law"), 160) or "Not specified",
            "venue": self._as_text(juris_raw.get("venue"), 160) or "Not specified",
            "dispute_resolution": self._as_text(juris_raw.get("dispute_resolution"), 160)
                                  or "Not specified",
            "page_number": self._as_page(juris_raw.get("page_number")),
            "section": self._as_text(juris_raw.get("section"), 60),
        }

        return {
            "parties": parties[:8],
            "dates": dates[:10],
            "financials": financials[:10],
            "jurisdiction": jurisdiction,
        }

    def _normalize_sections(self, raw: Any) -> List[dict]:
        if not isinstance(raw, list):
            return []
        sections = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            title = self._as_text(entry.get("title"), 160)
            if not title:
                continue
            sections.append({
                "title": title,
                "page_number": self._as_page(entry.get("page_number")),
                "section": self._as_text(entry.get("section"), 60),
                "text_snippet": self._as_text(entry.get("text_snippet"), 320),
                "key_points": self._as_str_list(entry.get("key_points"), 5),
            })
        return sections[:10]

    # ────────────────────────────────────────────────────────────────────
    # Scoring
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_risk_score(risks: List[dict], clauses: List[dict],
                           missing_clauses: List[str]) -> int:
        """
        Document health score from 0 (critical) to 100 (safe).

        Deductions are severity-weighted. Clause-level findings count at half
        weight because a high-risk clause is usually also reported as a risk,
        and double-counting would drive every contract to zero.
        """
        deduction = 0.0
        for risk in risks:
            deduction += _SEVERITY_WEIGHT.get(risk.get("severity", "Medium"), 8)
        for clause in clauses:
            deduction += _SEVERITY_WEIGHT.get(clause.get("risk_level", "Low"), 3) * 0.5
        deduction += _MISSING_CLAUSE_WEIGHT * len(missing_clauses)

        return max(0, min(100, round(100 - deduction)))

    @staticmethod
    def summarize_risk_counts(risks: List[dict], clauses: List[dict]) -> Dict[str, int]:
        """Severity histogram across both risks and clauses, for dashboards."""
        counts = {severity: 0 for severity in SEVERITIES}
        for risk in risks:
            counts[risk.get("severity", "Medium")] = counts.get(risk.get("severity", "Medium"), 0) + 1
        for clause in clauses:
            level = clause.get("risk_level", "Low")
            counts[level] = counts.get(level, 0) + 1
        return counts

    # ────────────────────────────────────────────────────────────────────
    # Public entry point
    # ────────────────────────────────────────────────────────────────────
    async def generate_analysis(self, chunks: List[Document]) -> dict:
        """
        Run the full four-stage audit and return a normalised report.

        The returned dict is the canonical audit shape consumed by the API,
        MongoDB and the frontend:

            contract_type, executive_summary, summary, key_takeaways,
            section_summaries, clauses, entities, risks, missing_clauses,
            suggestions, risk_score, risk_counts
        """
        if not chunks:
            return self.empty_report(
                "No readable text could be extracted from this document."
            )

        context = self.build_context(chunks)
        self._quota_exhausted = False

        # The four stages are independent, but the API is rate limited, so they
        # run through a semaphore rather than all at once. The overview stage
        # goes first: if the quota is already gone, the rest bail out early
        # instead of each grinding through the full model chain.
        gate = asyncio.Semaphore(STAGE_CONCURRENCY)

        async def run_stage(coro_factory, stage_name: str) -> dict:
            if self._quota_exhausted:
                logger.warning(
                    f"[AuditService] skipping '{stage_name}' — quota already exhausted."
                )
                return {}
            async with gate:
                return await coro_factory(context)

        overview, clause_stage, entity_stage, section_stage = await asyncio.gather(
            run_stage(self._stage_overview, "overview"),
            run_stage(self._stage_clauses, "clauses"),
            run_stage(self._stage_entities, "entities"),
            run_stage(self._stage_sections, "sections"),
            return_exceptions=True,
        )

        def unwrap(stage_result: Any, stage_name: str) -> dict:
            if isinstance(stage_result, Exception):
                logger.error(f"[AuditService] stage '{stage_name}' raised: {stage_result}")
                return {}
            return stage_result if isinstance(stage_result, dict) else {}

        overview = unwrap(overview, "overview")
        clause_stage = unwrap(clause_stage, "clauses")
        entity_stage = unwrap(entity_stage, "entities")
        section_stage = unwrap(section_stage, "sections")

        if not any([overview, clause_stage, entity_stage, section_stage]):
            if self._quota_exhausted:
                raise RuntimeError(
                    "The Gemini API daily free-tier quota for this key is exhausted. "
                    "The document was uploaded and indexed successfully — retry the "
                    "analysis after the quota resets, or switch to a billed API key."
                )
            raise RuntimeError(
                "The AI analysis service is unavailable. Please check the "
                "GOOGLE_API_KEY configuration and try again."
            )

        risks = self._normalize_risks(overview.get("risks"))
        clauses = self._normalize_clauses(clause_stage.get("clauses"))
        entities = self._normalize_entities(entity_stage)
        section_summaries = self._normalize_sections(section_stage.get("section_summaries"))
        missing_clauses = self._as_str_list(overview.get("missing_clauses"), 10)

        executive_summary = self._as_text(overview.get("executive_summary"), 2000)
        if not executive_summary:
            executive_summary = (
                "The document was processed and indexed, but the AI summary stage did not "
                "return a result. Clause, entity and risk findings below are still valid."
            )

        return {
            "contract_type": self._as_text(overview.get("contract_type"), 120) or "Legal Document",
            "executive_summary": executive_summary,
            # `summary` is kept as an alias so the dashboard, library and export
            # modules continue to read a single summary field.
            "summary": executive_summary,
            "key_takeaways": self._as_str_list(overview.get("key_takeaways"), 8),
            "section_summaries": section_summaries,
            "clauses": clauses,
            "entities": entities,
            "risks": risks,
            "missing_clauses": missing_clauses,
            "suggestions": self._build_suggestions(missing_clauses, clauses),
            "risk_score": self.compute_risk_score(risks, clauses, missing_clauses),
            "risk_counts": self.summarize_risk_counts(risks, clauses),
        }

    @staticmethod
    def _build_suggestions(missing_clauses: List[str], clauses: List[dict]) -> List[str]:
        """
        Remediation list for the Suggestions tab: missing protections first,
        then per-clause recommendations for the clauses that carry real risk.
        """
        suggestions = [
            f"Add a {name} clause — this standard protection is absent from the document."
            for name in missing_clauses
        ]
        for clause in clauses:
            recommendation = clause.get("recommendation")
            if recommendation and clause.get("risk_level") in {"Critical", "High", "Medium"}:
                suggestions.append(f"{clause['title']}: {recommendation}")
        return suggestions[:15]

    @staticmethod
    def empty_report(reason: str) -> dict:
        """A well-formed report for documents that yielded no analysable text."""
        return {
            "contract_type": "Unknown",
            "executive_summary": reason,
            "summary": reason,
            "key_takeaways": [],
            "section_summaries": [],
            "clauses": [],
            "entities": {
                "parties": [],
                "dates": [],
                "financials": [],
                "jurisdiction": {
                    "governing_law": "Not specified",
                    "venue": "Not specified",
                    "dispute_resolution": "Not specified",
                    "page_number": 1,
                    "section": "",
                },
            },
            "risks": [],
            "missing_clauses": [],
            "suggestions": [],
            "risk_score": 0,
            "risk_counts": {severity: 0 for severity in SEVERITIES},
        }
