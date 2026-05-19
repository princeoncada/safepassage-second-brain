from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


DocumentType = Literal[
    "post_order",
    "announcement",
    "qa_rule",
    "workflow",
    "incident",
    "visitor_log",
    "unknown",
    "briefing",
    "community_profile",
    "script",
    "training",
    "sop",
    "automation",
    "code_snippet",
    "archived",
]
AuthorityLevel = Literal["post_order", "announcement", "primary_workflow", "qa_rule"]
Status = Literal["active", "pending", "superseded", "archived", "conflict", "review", "needs_review", "expired"]
LifecycleGeneration = Literal["managed", "legacy", "archived"]
TemporalState = Literal["active", "pending", "not_yet_active", "expired", "superseded", "archived", "review", "unknown"]
ReviewStatus = Literal["pending_review", "approved", "rejected"]
TargetIngestionType = Literal["announcement", "post_order", "none"]


class VaultDocument(BaseModel):
    title: Optional[str] = None
    type: Optional[DocumentType] = None
    community: Optional[str] = None
    scope: Optional[str | list[str]] = None
    scope_key: Optional[str] = None
    authority_level: Optional[AuthorityLevel] = None
    status: Optional[Status] = None
    lifecycle_generation: Optional[LifecycleGeneration] = None
    rule_id: Optional[str] = None
    rule_hash: Optional[str] = None
    topic_key: Optional[str] = None
    source_batch: Optional[str] = None
    batch_date: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    source_legacy_file: Optional[str] = None
    source_migration: Optional[str] = None
    migration_date: Optional[str] = None
    temporal_state: Optional[TemporalState] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    temporal_warning: Optional[str] = None
    category: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    version: Optional[str] = None
    source_file: Optional[str] = None
    approved_for_ingestion: Optional[bool] = None
    review_status: Optional[ReviewStatus] = None
    target_ingestion_type: Optional[TargetIngestionType] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_notes: Optional[str] = None
    tags: Optional[list[str]] = None

    class Config:
        extra = "allow"


def validate_frontmatter(meta: dict) -> list[str]:
    """
    Validate a frontmatter dict against VaultDocument.
    Returns a list of warning strings (empty = valid).
    Never raises. Used for soft validation only.
    """
    try:
        VaultDocument(**meta)
        return []
    except Exception as error:  # noqa: BLE001
        return [str(error)]
