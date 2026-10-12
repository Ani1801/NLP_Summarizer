from pydantic import BaseModel, Field
from typing import List, Optional


class CompareRequest(BaseModel):
    """Request body for POST /api/compare."""
    audit_id_a: str = Field(..., description="First audit ID (e.g., the 'old' contract)")
    audit_id_b: str = Field(..., description="Second audit ID (e.g., the 'new' contract)")


class ClauseMatch(BaseModel):
    """A matched or differing clause pair between two documents."""
    topic: str = Field(..., description="The clause topic, e.g., 'Termination', 'Liability'")
    doc_a_text: str = Field(default="", description="Relevant text from Document A")
    doc_b_text: str = Field(default="", description="Relevant text from Document B")
    status: str = Field(default="matched", description="'matched', 'modified', 'missing_in_a', 'missing_in_b'")
    risk_note: str = Field(default="", description="Any risk implication of this difference")


class CompareResponse(BaseModel):
    """Response body from the /api/compare endpoint."""
    difference_summary: str = Field(..., description="Natural language summary of key differences")
    risk_shift_score: int = Field(default=0, ge=-100, le=100, description="Score from -100 (worse) to +100 (better)")
    clauses: List[ClauseMatch] = Field(default_factory=list, description="Detailed clause-by-clause comparison")
    missing_in_a: List[str] = Field(default_factory=list, description="Protections missing in Document A")
    missing_in_b: List[str] = Field(default_factory=list, description="Protections missing in Document B")
    doc_a_name: str = ""
    doc_b_name: str = ""
