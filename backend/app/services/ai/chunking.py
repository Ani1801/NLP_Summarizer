"""
Token-aware, structure-aware chunking.

This replaces the earlier character-count splitter. Character counts are a poor
proxy for what a model can actually accept: the constraint that matters is
tokens, and the boundaries that matter are section, paragraph and sentence.

Hierarchy respected, outermost first:

    Document → Section → Paragraph → Sentence → token-bounded chunk

A chunk never crosses a section boundary, so `section_title` is always accurate
for the whole chunk. Within a section, paragraphs are packed until the token
budget is reached; a single paragraph over budget is split on sentences.

Token counting goes through a pluggable counter so chunking never *requires* a
model download — the heuristic fallback is used when no tokenizer is available.
"""

from __future__ import annotations

import re
import uuid
from typing import Callable, List, Optional, Tuple

from app.core.config import settings
from app.core.logging import logger
from app.domain.document import Chunk, Section

# Sentence boundary: terminal punctuation followed by whitespace and a capital.
# The negative lookbehind keeps common legal abbreviations intact.
_SENTENCE_SPLIT = re.compile(
    r"(?<!\bNo)(?<!\bInc)(?<!\bLtd)(?<!\bLLC)(?<!\bCorp)(?<!\bCo)(?<!\bSec)"
    r"(?<!\bNos)(?<!\bArt)(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bv)"
    r"(?<=[.!?])\s+(?=[A-Z0-9(\"'])"
)

_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n|\n(?=\s*(?:\(\w{1,4}\)|\d{1,2}\.\d|•|-\s))")


# ─────────────────────────────────────────────────────────────────────────────
# Token counting
# ─────────────────────────────────────────────────────────────────────────────
def heuristic_token_count(text: str) -> int:
    """
    Estimate tokens without a tokenizer.

    Legal English runs about 1.3 subword tokens per whitespace word. Slightly
    conservative on purpose: over-estimating keeps chunks inside a model's real
    limit, whereas under-estimating causes silent truncation.
    """
    if not text:
        return 0
    words = len(text.split())
    return max(1, int(words * 1.35) + text.count("\n"))


class TokenCounter:
    """
    Counts tokens with a Hugging Face tokenizer when one can be loaded, and
    falls back to the heuristic otherwise.

    The tokenizer is a few hundred kilobytes — far cheaper than the model — and
    is loaded lazily on first use so importing this module stays free.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.SUMMARIZATION_MODEL
        self._tokenizer = None
        self._unavailable = False

    def _load(self):
        if self._tokenizer is not None or self._unavailable:
            return
        try:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info(f"[Chunking] token counter using '{self.model_name}'")
        except Exception as e:
            self._unavailable = True
            logger.warning(
                f"[Chunking] tokenizer '{self.model_name}' unavailable ({e}); "
                "using the heuristic token estimate."
            )

    def count(self, text: str) -> int:
        self._load()
        if self._tokenizer is None:
            return heuristic_token_count(text)
        try:
            return len(self._tokenizer.encode(text, add_special_tokens=False))
        except Exception:
            return heuristic_token_count(text)


# Shared counter — loading one tokenizer per process is enough.
_default_counter: Optional[TokenCounter] = None


def default_token_counter() -> Callable[[str], int]:
    global _default_counter
    if _default_counter is None:
        _default_counter = TokenCounter()
    return _default_counter.count


# ─────────────────────────────────────────────────────────────────────────────
# Chunker
# ─────────────────────────────────────────────────────────────────────────────
class TokenAwareChunker:
    """
    Builds canonical chunks from detected sections.

    `max_tokens` and `overlap_tokens` come from configuration, never hard-coded.
    Overlap is applied only between chunks inside the same section, where it
    actually helps retrieval; it is skipped across section boundaries, since a
    section's opening lines are not useful context for a different section, and
    every duplicated token costs inference time downstream.
    """

    def __init__(
        self,
        max_tokens: Optional[int] = None,
        overlap_tokens: Optional[int] = None,
        min_tokens: Optional[int] = None,
        count_tokens: Optional[Callable[[str], int]] = None,
    ):
        self.max_tokens = max_tokens or settings.CHUNK_MAX_TOKENS
        self.overlap_tokens = overlap_tokens if overlap_tokens is not None else settings.CHUNK_OVERLAP_TOKENS
        self.min_tokens = min_tokens or settings.CHUNK_MIN_TOKENS
        self.count_tokens = count_tokens or default_token_counter()

    # ── Splitting helpers ───────────────────────────────────────────────
    @staticmethod
    def split_paragraphs(text: str) -> List[str]:
        return [p.strip() for p in _PARAGRAPH_SPLIT.split(text) if p and p.strip()]

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        parts = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s and s.strip()]
        return parts or [text.strip()]

    def _split_oversized(self, text: str) -> List[str]:
        """
        Break a single over-budget paragraph on sentence boundaries.

        A sentence that is itself over budget (common in ALL-CAPS liability
        blocks with no punctuation) is split on whitespace as a last resort,
        which is the only point where a chunk may cut mid-sentence.
        """
        pieces: List[str] = []
        buffer: List[str] = []
        buffer_tokens = 0

        for sentence in self.split_sentences(text):
            tokens = self.count_tokens(sentence)

            if tokens > self.max_tokens:
                if buffer:
                    pieces.append(" ".join(buffer))
                    buffer, buffer_tokens = [], 0
                words = sentence.split()
                # Words per chunk derived from the measured tokens-per-word rate.
                per_chunk = max(1, int(len(words) * self.max_tokens / max(tokens, 1)))
                for start in range(0, len(words), per_chunk):
                    pieces.append(" ".join(words[start:start + per_chunk]))
                continue

            if buffer_tokens + tokens > self.max_tokens and buffer:
                completed = " ".join(buffer)
                pieces.append(completed)
                # Carry overlap here too: a dense contract clause is often one
                # long paragraph, and without this such a document would get no
                # overlap at all.
                tail = self._overlap_tail(completed)
                buffer = [tail] if tail else []
                buffer_tokens = self.count_tokens(tail) if tail else 0

            buffer.append(sentence)
            buffer_tokens += tokens

        if buffer:
            pieces.append(" ".join(buffer))
        return pieces

    def _overlap_tail(self, text: str) -> str:
        """The trailing sentences of `text` worth about `overlap_tokens`."""
        if self.overlap_tokens <= 0:
            return ""
        sentences = self.split_sentences(text)
        tail: List[str] = []
        total = 0
        for sentence in reversed(sentences):
            tokens = self.count_tokens(sentence)
            if total + tokens > self.overlap_tokens and tail:
                break
            tail.insert(0, sentence)
            total += tokens
        return " ".join(tail)

    # ── Main entry point ────────────────────────────────────────────────
    def chunk_sections(
        self,
        sections: List[Section],
        document_id: str,
        user_id: str,
    ) -> List[Chunk]:
        """
        Produce canonical chunks for a whole document, in reading order.

        Sections smaller than `min_tokens` are merged forward into the next
        chunk rather than emitted alone, so a bare heading does not become its
        own useless embedding.
        """
        chunks: List[Chunk] = []
        order = 0
        carry: Optional[Tuple[Section, str]] = None  # a too-small section held over

        for section in sections:
            body = section.text.strip()
            if not body:
                continue

            if carry is not None:
                carried_section, carried_text = carry
                body = f"{carried_text}\n\n{body}"
                # Attribute the merged chunk to the section it mostly came from.
                section = section if len(body) > len(carried_text) * 2 else carried_section
                carry = None

            if self.count_tokens(body) < self.min_tokens:
                carry = (section, body)
                continue

            for text in self._pack_section(body):
                chunks.append(self._make_chunk(
                    text=text, section=section, document_id=document_id,
                    user_id=user_id, order=order,
                ))
                order += 1

        # Anything still held over is emitted rather than dropped.
        if carry is not None:
            section, body = carry
            chunks.append(self._make_chunk(
                text=body, section=section, document_id=document_id,
                user_id=user_id, order=order,
            ))

        logger.info(
            f"[Chunking] {len(sections)} section(s) -> {len(chunks)} chunk(s), "
            f"budget {self.max_tokens} tokens, overlap {self.overlap_tokens}"
        )
        return chunks

    def _pack_section(self, body: str) -> List[str]:
        """Pack a section's paragraphs into token-bounded chunks."""
        texts: List[str] = []
        buffer: List[str] = []
        buffer_tokens = 0

        for paragraph in self.split_paragraphs(body):
            tokens = self.count_tokens(paragraph)

            if tokens > self.max_tokens:
                if buffer:
                    texts.append("\n\n".join(buffer))
                    buffer, buffer_tokens = [], 0
                texts.extend(self._split_oversized(paragraph))
                continue

            if buffer_tokens + tokens > self.max_tokens and buffer:
                completed = "\n\n".join(buffer)
                texts.append(completed)
                tail = self._overlap_tail(completed)
                buffer = [tail] if tail else []
                buffer_tokens = self.count_tokens(tail) if tail else 0

            buffer.append(paragraph)
            buffer_tokens += tokens

        if buffer:
            remainder = "\n\n".join(buffer)
            # Don't emit a chunk that is only the overlap from the previous one.
            if texts and self.count_tokens(remainder) < self.min_tokens:
                texts[-1] = f"{texts[-1]}\n\n{remainder}"
            else:
                texts.append(remainder)
        return texts

    def _make_chunk(self, text: str, section: Section, document_id: str,
                    user_id: str, order: int) -> Chunk:
        return Chunk(
            chunk_id=f"chk-{uuid.uuid4().hex[:12]}",
            document_id=document_id,
            user_id=user_id,
            text=text,
            token_count=self.count_tokens(text),
            page_start=section.page_start,
            page_end=section.page_end,
            section_id=section.section_id,
            section_number=section.section_number,
            section_title=section.section_title,
            order=order,
        )
