"""Domain models: the canonical document representation shared by all analysis stages."""

from app.domain.summary import (
    SectionSummary,
    SourceReference,
    SummaryItem,
    SummaryResult,
)
from app.domain.document import (
    CanonicalDocument,
    Chunk,
    Page,
    ProcessingStatus,
    STAGE_PROGRESS,
    Section,
)

__all__ = [
    "CanonicalDocument", "Chunk", "Page", "Section", "ProcessingStatus", "STAGE_PROGRESS",
    "SummaryResult", "SummaryItem", "SectionSummary", "SourceReference",
]
