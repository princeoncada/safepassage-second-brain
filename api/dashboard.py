from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from rag.dashboard import dashboard_payload, filtered_payload


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def safe_payload(builder, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        return builder(*args, **kwargs)
    except RuntimeError as error:
        return {
            "status": "error",
            "community": kwargs.get("community") or "global",
            "items": [],
            "sections": {},
            "briefing_markdown": "",
            "warnings": [str(error)],
        }


@router.get("/summary")
def dashboard_summary(
    community: str = "",
    expiring_soon_days: int = Query(default=7, ge=1, le=60),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return safe_payload(dashboard_payload, community=community, expiring_soon_days=expiring_soon_days, limit=limit)


@router.get("/briefing")
def dashboard_briefing(
    community: str = "",
    expiring_soon_days: int = Query(default=7, ge=1, le=60),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return safe_payload(dashboard_payload, community=community, expiring_soon_days=expiring_soon_days, limit=limit)


@router.get("/announcements")
def dashboard_announcements(
    community: str = "",
    expiring_soon_days: int = Query(default=7, ge=1, le=60),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return safe_payload(filtered_payload, "announcements", community=community, expiring_soon_days=expiring_soon_days, limit=limit)


@router.get("/post-orders")
def dashboard_post_orders(
    community: str = "",
    expiring_soon_days: int = Query(default=7, ge=1, le=60),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return safe_payload(filtered_payload, "post_orders", community=community, expiring_soon_days=expiring_soon_days, limit=limit)


@router.get("/issues")
def dashboard_issues(
    community: str = "",
    expiring_soon_days: int = Query(default=7, ge=1, le=60),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    return safe_payload(filtered_payload, "issues", community=community, expiring_soon_days=expiring_soon_days, limit=limit)


@router.get("/status")
def dashboard_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "read_only",
        "source": "indexed ChromaDB metadata derived from vault Markdown",
        "safety": [
            "does not write to vault",
            "does not run ingestion",
            "does not update ChromaDB",
            "does not override authority hierarchy",
        ],
    }
