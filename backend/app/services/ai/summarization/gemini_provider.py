"""
GeminiSummarizer — optional provider, not the default.

Kept behind the same interface as the local engine so a deployment with an API
budget can switch to it with `SUMMARY_PROVIDER=gemini`. It is not the default
because it needs a key, is rate limited (the free tier allows 20 requests per day
per model), and a long contract needs one request per chunk.

`is_available()` only reports whether a key is configured — it does not spend a
request probing the API.
"""

from __future__ import annotations

import os
from typing import List, Optional

from app.core.logging import logger
from app.services.ai.summarization.base import (
    CHUNK_INSTRUCTION,
    SummarizationProvider,
)

GEMINI_MODELS = [
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
]


class GeminiSummarizer(SummarizationProvider):
    name = "gemini"

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self._model_name = model_name or GEMINI_MODELS[0]

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return "google-generativeai"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def summarize(
        self,
        text: str,
        max_output_tokens: Optional[int] = None,
        instruction: Optional[str] = None,
    ) -> str:
        if not text or not text.strip() or not self.api_key:
            return ""

        prompt = f"{instruction or CHUNK_INSTRUCTION}\n\n---\n\n{text}"

        for model in GEMINI_MODELS:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                llm = ChatGoogleGenerativeAI(
                    model=model, google_api_key=self.api_key, temperature=0.1,
                )
                response = llm.invoke(prompt)
                content = response.content
                if isinstance(content, list):
                    content = " ".join(str(part) for part in content)
                if content and str(content).strip():
                    self._model_name = model
                    return str(content).strip()
            except Exception as e:
                message = str(e)
                # A per-day quota exhaustion cannot be fixed by trying another
                # model in the same project — stop rather than burn more calls.
                if "PerDay" in message or "per day" in message.lower():
                    logger.error(
                        "[GeminiSummarizer] daily quota exhausted; giving up."
                    )
                    return ""
                logger.warning(f"[GeminiSummarizer] {model} failed: {e}")

        return ""
