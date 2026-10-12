from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""
    audit_id: str = Field(..., description="The audit ID of the document to chat with")
    question: str = Field(..., min_length=1, max_length=2000, description="User's question about the document")


class SourceChunk(BaseModel):
    """A single source citation from the retrieved context."""
    text: str = Field(..., description="Snippet of the relevant chunk text")
    page_number: int = Field(default=1, description="Page number in the original PDF")
    file_name: str = Field(default="Unknown", description="Original filename of the document")


class ChatResponse(BaseModel):
    """Response body from the /api/chat endpoint."""
    answer: str = Field(..., description="Gemini's grounded answer based on document context")
    sources: List[SourceChunk] = Field(default_factory=list, description="Source citations")
