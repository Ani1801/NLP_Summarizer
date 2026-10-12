"""
Provider selection — the one place that decides which engine summarises.

Reads `SUMMARY_PROVIDER` from configuration. "local" is the default so the
platform works with no API key; "gemini" is available for deployments that have
an API budget. Providers are cached per name because loading a local model is
expensive and must happen once per process.
"""

from __future__ import annotations

from typing import Dict, Optional

from app.core.config import settings
from app.core.logging import logger
from app.services.ai.summarization.base import SummarizationProvider

_cache: Dict[str, SummarizationProvider] = {}


def build_provider(name: str) -> SummarizationProvider:
    """Construct a provider by name, without caching."""
    key = (name or "local").strip().lower()

    if key == "gemini":
        from app.services.ai.summarization.gemini_provider import GeminiSummarizer

        return GeminiSummarizer()

    if key != "local":
        logger.warning(
            f"[Summarization] unknown SUMMARY_PROVIDER '{name}' — using 'local'."
        )

    from app.services.ai.summarization.local_provider import LocalTransformerSummarizer

    return LocalTransformerSummarizer()


def get_provider(name: Optional[str] = None) -> SummarizationProvider:
    """
    The active provider, cached per name.

    Caching matters: the local provider holds a multi-hundred-megabyte model, and
    building a second instance would load it twice.
    """
    key = (name or settings.SUMMARY_PROVIDER or "local").strip().lower()
    if key not in _cache:
        _cache[key] = build_provider(key)
        logger.info(
            f"[Summarization] provider '{key}' -> {_cache[key].model_name}"
        )
    return _cache[key]


def reset_providers() -> None:
    """Drop cached providers. Used by tests to swap engines."""
    _cache.clear()
