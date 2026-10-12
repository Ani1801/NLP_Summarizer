"""
Audit document model — the MongoDB `audits` collection shape.

The canonical API-facing schema lives in `app/schemas/audit.py`; this model
describes what is persisted.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.audit import Clause, Entities, Risk, SectionSummary


class Audit(BaseModel):
    user_id: str
    file_name: str
    storage_key: Optional[str] = None
    status: str = "Pending"

    contract_type: str = "Legal Document"
    executive_summary: str = ""
    summary: str = ""
    key_takeaways: List[str] = Field(default_factory=list)
    section_summaries: List[SectionSummary] = Field(default_factory=list)

    clauses: List[Clause] = Field(default_factory=list)
    entities: Entities = Field(default_factory=Entities)
    risks: List[Risk] = Field(default_factory=list)
    missing_clauses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    risk_score: int = Field(default=0, ge=0, le=100)
    risk_counts: Dict[str, int] = Field(default_factory=dict)

    file_size: int = 0
    page_count: int = 0
    chunk_count: int = 0
    vector_backend: str = "local"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
