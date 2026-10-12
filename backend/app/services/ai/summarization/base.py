"""
Summarization provider contract.

The rest of the application depends on `SummarizationProvider`, never on
Transformers or on Gemini directly. Swapping the engine is a configuration
change (`SUMMARY_PROVIDER`), not a code change.

`LocalTransformerSummarizer` is the default because the platform must be able to
summarise documents with no API key, no quota and no external dependency.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# Re-exported so existing imports from this module keep working.
from app.domain.summary import (
    SectionSummary,
    SourceReference,
    SummaryItem,
    SummaryResult,
)

__all__ = [
    "SummarizationProvider",
    "SummaryResult",
    "SummaryItem",
    "SectionSummary",
    "SourceReference",
    "CHUNK_INSTRUCTION",
    "GROUP_INSTRUCTION",
    "FINAL_INSTRUCTION",
]


class SummarizationProvider(ABC):
    """
    Engine that turns text into a shorter, factual summary.

    Implementations must not invent facts. The instruction given to the model
    emphasises preserving parties, dates, amounts, conditions, obligations,
    rights, restrictions and termination requirements verbatim.
    """

    name: str = "base"

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the underlying model, recorded with every summary."""

    @property
    def model_version(self) -> str:
        return "unknown"

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this provider can actually run right now."""

    @abstractmethod
    def summarize(
        self,
        text: str,
        max_output_tokens: Optional[int] = None,
        instruction: Optional[str] = None,
    ) -> str:
        """Summarise one piece of text. Returns "" when it cannot."""

    def summarize_batch(
        self,
        texts: List[str],
        max_output_tokens: Optional[int] = None,
        instruction: Optional[str] = None,
    ) -> List[str]:
        """
        Summarise several texts. The default is sequential; providers that can
        batch on an accelerator override this.
        """
        return [self.summarize(text, max_output_tokens, instruction) for text in texts]

    def describe(self) -> Dict[str, str]:
        return {
            "provider": self.name,
            "model_name": self.model_name,
            "model_version": self.model_version,
        }


# ── Instructions, versioned so a stored summary can be traced to its prompt ──
CHUNK_INSTRUCTION = (
    "Summarise this contract excerpt factually and concisely. Preserve exactly, "
    "without rewording or rounding: party names, dates, time periods, monetary "
    "amounts, percentages, notice periods, and conditional terms such as "
    "'unless', 'provided that', 'subject to' and 'except'. State who is "
    "obligated to do what, who holds which rights, and what each party is "
    "prohibited from doing. Do not add information that is not in the text."
)

GROUP_INSTRUCTION = (
    "Combine these contract summaries into one coherent summary. Keep every "
    "party name, date, amount, percentage and notice period exactly as given. "
    "Do not introduce any fact that is not present."
)

FINAL_INSTRUCTION = (
    "Write an executive summary of this contract from the section summaries "
    "below. Cover the purpose of the agreement, the parties, the core "
    "obligations of each side, the commercial terms, and how the agreement "
    "ends. Keep all figures and dates exactly as stated. Add nothing new."
)
