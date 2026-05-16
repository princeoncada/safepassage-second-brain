from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    show_context: bool = False
    no_ai: bool = False
    include_low_value_sections: bool = False


class Source(BaseModel):
    source_id: int
    distance: float
    title: str
    type: str
    authority_level: str = ""
    scope: str = ""
    status: str = ""
    rule_id: str = ""
    rule_hash: str = ""
    source_batch: str = ""
    supersedes: str = ""
    superseded_by: str = ""
    community: str
    section: str
    source_file: str
    preview: str
    content: str | None = None


class AskResponse(BaseModel):
    status: str
    question: str
    answer: str
    retrieval_confidence: str
    confidence_reason: str
    # All retrieved sources are returned separately from answer citations so UI
    # clients can render one clean Sources section.
    sources: list[Source]
    answer_citations: list[Source]
    used_ai: bool
    warnings: list[str]
