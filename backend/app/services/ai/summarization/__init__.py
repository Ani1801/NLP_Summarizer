"""Summarisation: provider abstraction, local and Gemini engines, hierarchical service."""

from app.services.ai.summarization.base import (
    SectionSummary,
    SourceReference,
    SummarizationProvider,
    SummaryItem,
    SummaryResult,
)
from app.services.ai.summarization.registry import get_provider, reset_providers
from app.services.ai.summarization.service import SummarizationService, summarization_service

__all__ = [
    "SummarizationProvider",
    "SummaryResult",
    "SummaryItem",
    "SectionSummary",
    "SourceReference",
    "SummarizationService",
    "summarization_service",
    "get_provider",
    "reset_providers",
]
