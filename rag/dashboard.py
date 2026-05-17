from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from textwrap import shorten
from typing import Any

import chromadb

from rag.lifecycle import parse_iso_date
from rag.query_intent import load_community_aliases
from rag.retrieval_rerank import normalize_key


REPO_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"
COLLECTION_NAME = "safepassage_vault_chunks"

LOW_VALUE_SECTIONS = {"source", "migration notes", "operational notes", "change history", "open questions", "source input"}
PREFERRED_SECTIONS = {"announcement", "rule", "agent action", "summary", "details", "policy"}
NON_CURRENT_STATES = {"expired", "superseded", "archived", "review"}
ISSUE_TERMS = {"gate", "nvr", "kiosk", "audio", "barrier", "id viewer", "traffic", "emergency"}
DASHBOARD_SOURCE_EXCLUDE_PREFIXES = (
    "vault/08_Reports/",
    "vault/07_Visitor_Logs/",
    "vault/06_Incidents/",
    "vault/01_Daily_Briefings/",
)


@dataclass(frozen=True)
class DashboardItem:
    title: str
    category: str
    community: str
    temporal_state: str
    priority: str
    authority_level: str
    type: str
    status: str
    lifecycle_status: str
    lifecycle_generation: str
    effective_date: str
    expiry_date: str
    source_file: str
    section: str
    preview: str
    score: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "category": self.category,
            "community": self.community,
            "temporal_state": self.temporal_state,
            "priority": self.priority,
            "authority_level": self.authority_level,
            "type": self.type,
            "status": self.status,
            "lifecycle_status": self.lifecycle_status,
            "lifecycle_generation": self.lifecycle_generation,
            "effective_date": self.effective_date,
            "expiry_date": self.expiry_date,
            "source_file": self.source_file,
            "section": self.section,
            "preview": self.preview,
            "score": round(self.score, 4),
        }


def resolve_community(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    aliases = load_community_aliases()
    if raw.upper() in aliases:
        return aliases[raw.upper()]
    normalized = normalize_key(raw)
    for community in aliases.values():
        if normalize_key(community) == normalized:
            return community
    return raw


def collection_items() -> tuple[list[str], list[dict[str, Any]], list[str]]:
    if not CHROMA_DIR.exists():
        raise RuntimeError("Chroma index does not exist. Rebuild it from vault Markdown before using dashboard endpoints.")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        raise RuntimeError("Chroma collection is missing. Rebuild it from vault Markdown before using dashboard endpoints.") from error
    results = collection.get(include=["documents", "metadatas"])
    return (
        [str(item) for item in results.get("ids", [])],
        [metadata or {} for metadata in results.get("metadatas", [])],
        [str(document or "") for document in results.get("documents", [])],
    )


def first_date(*values: str) -> str:
    for value in values:
        parsed, normalized = parse_iso_date(value)
        if parsed:
            return normalized
    return ""


def is_expiring_soon(expiry_date: str, days: int) -> bool:
    parsed, _normalized = parse_iso_date(expiry_date)
    if not parsed:
        return False
    today = date.today()
    return today <= parsed <= today + timedelta(days=days)


def priority_for(metadata: dict[str, Any], expiry_date: str, expiring_soon_days: int) -> str:
    category = normalize_key(metadata.get("category", ""))
    text = normalize_key(" ".join(str(metadata.get(key, "")) for key in ["title", "category", "normalized_announcement"]))
    authority = str(metadata.get("authority_level", ""))
    if "emergency" in text or category in {"temporary_protocol", "gate_issue", "nvr_issue"}:
        return "high"
    if is_expiring_soon(expiry_date, expiring_soon_days):
        return "high"
    if "compliance" in category or "qa" in text or authority == "post_order":
        return "medium"
    return "normal"


def score_item(metadata: dict[str, Any], expiry_date: str, expiring_soon_days: int) -> float:
    score = 0.0
    authority = str(metadata.get("authority_level", ""))
    category = normalize_key(metadata.get("category", ""))
    section = normalize_key(metadata.get("section", ""))
    temporal_state = str(metadata.get("temporal_state", ""))
    community = normalize_key(metadata.get("community", ""))
    text = normalize_key(" ".join(str(metadata.get(key, "")) for key in ["title", "category", "normalized_announcement"]))

    score += {"post_order": 35, "announcement": 25, "primary_workflow": 5}.get(authority, 0)
    score += {"active": 30, "pending": 6, "not_yet_active": 4}.get(temporal_state, 0)
    score += {
        "temporary_protocol": 20,
        "gate_issue": 18,
        "nvr_issue": 18,
        "traffic_handling": 16,
        "event": 14,
        "compliance_warning": 16,
        "approved_vendor": 10,
    }.get(category, 0)
    if is_expiring_soon(expiry_date, expiring_soon_days):
        score += 18
    if community and community != "global":
        score += 4
    if section in PREFERRED_SECTIONS:
        score += 6
    if section in LOW_VALUE_SECTIONS:
        score -= 12
    if any(term in text for term in ISSUE_TERMS):
        score += 8
    return score


def include_item(metadata: dict[str, Any], community: str) -> bool:
    source_file = str(metadata.get("source_file", ""))
    if source_file.startswith(DASHBOARD_SOURCE_EXCLUDE_PREFIXES):
        return False
    section = normalize_key(metadata.get("section", ""))
    if section in LOW_VALUE_SECTIONS:
        return False
    if str(metadata.get("authority_level", "")) == "primary_workflow":
        return False
    if str(metadata.get("temporal_state", "")) in NON_CURRENT_STATES:
        return False
    status = normalize_key(metadata.get("status", ""))
    if status in {"archived", "superseded", "inactive", "rejected", "needs_review", "review"}:
        return False
    if community:
        item_community = normalize_key(metadata.get("community", ""))
        return item_community in {normalize_key(community), "global"}
    return True


def build_items(community: str = "", expiring_soon_days: int = 7, limit: int = 50) -> list[DashboardItem]:
    resolved_community = resolve_community(community)
    _ids, metadatas, documents = collection_items()
    seen_sources: set[tuple[str, str]] = set()
    items: list[DashboardItem] = []
    for metadata, document in zip(metadatas, documents):
        if not include_item(metadata, resolved_community):
            continue
        source_key = (str(metadata.get("source_file", "")), str(metadata.get("title", "")))
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        expiry_date = first_date(
            str(metadata.get("temporal_end_date", "")),
            str(metadata.get("active_until", "")),
            str(metadata.get("expires_at", "")),
            str(metadata.get("expiry_date", "")),
            str(metadata.get("end_date", "")),
            str(metadata.get("expires_on", "")),
        )
        effective_date = first_date(
            str(metadata.get("temporal_start_date", "")),
            str(metadata.get("active_from", "")),
            str(metadata.get("effective_date", "")),
            str(metadata.get("start_date", "")),
        )
        item = DashboardItem(
            title=str(metadata.get("title", "")),
            category=str(metadata.get("category", "")),
            community=str(metadata.get("community", "")) or "global",
            temporal_state=str(metadata.get("temporal_state", "")),
            priority=priority_for(metadata, expiry_date, expiring_soon_days),
            authority_level=str(metadata.get("authority_level", "")),
            type=str(metadata.get("type", "")),
            status=str(metadata.get("status", "")),
            lifecycle_status=str(metadata.get("lifecycle_status", "")),
            lifecycle_generation=str(metadata.get("lifecycle_generation", "")),
            effective_date=effective_date,
            expiry_date=expiry_date,
            source_file=str(metadata.get("source_file", "")),
            section=str(metadata.get("section", "")),
            preview=shorten(" ".join(document.split()), width=220, placeholder="..."),
            score=score_item(metadata, expiry_date, expiring_soon_days),
        )
        items.append(item)
    items.sort(key=lambda item: (-item.score, item.community, item.title, item.section))
    return items[:limit]


def text_matches(item: DashboardItem, *terms: str) -> bool:
    text = normalize_key(" ".join([item.title, item.category, item.preview, item.section]))
    return any(normalize_key(term) in text for term in terms)


def grouped_briefing(items: list[DashboardItem], expiring_soon_days: int = 7) -> dict[str, list[DashboardItem]]:
    groups = {
        "active_temporary_protocols": [],
        "gate_nvr_kiosk_issues": [],
        "active_events": [],
        "important_operational_reminders": [],
        "expiring_soon": [],
        "community_specific_alerts": [],
        "qa_compliance_warnings": [],
    }
    for item in items:
        category = normalize_key(item.category)
        if category == "temporary_protocol":
            groups["active_temporary_protocols"].append(item)
        if category in {"gate_issue", "nvr_issue", "traffic_handling"} or text_matches(
            item, "gate", "nvr", "kiosk", "audio", "barrier", "id viewer", "traffic", "emergency"
        ):
            groups["gate_nvr_kiosk_issues"].append(item)
        if category == "event":
            groups["active_events"].append(item)
        if item.type == "announcement" and category not in {"temporary_protocol", "gate_issue", "nvr_issue", "event"}:
            groups["important_operational_reminders"].append(item)
        if is_expiring_soon(item.expiry_date, expiring_soon_days):
            groups["expiring_soon"].append(item)
        if normalize_key(item.community) != "global":
            groups["community_specific_alerts"].append(item)
        if category == "compliance_warning" or text_matches(item, "qa", "compliance", "termination", "required"):
            groups["qa_compliance_warnings"].append(item)
    return {key: value[:10] for key, value in groups.items()}


def format_briefing(groups: dict[str, list[DashboardItem]]) -> str:
    labels = {
        "active_temporary_protocols": "Active Temporary Protocols",
        "gate_nvr_kiosk_issues": "Gate / NVR / Kiosk Issues",
        "active_events": "Active Events",
        "important_operational_reminders": "Important Operational Reminders",
        "expiring_soon": "Expiring Soon",
        "community_specific_alerts": "Community-Specific Alerts",
        "qa_compliance_warnings": "QA / Compliance Warnings",
    }
    lines = ["# Shift Briefing", ""]
    for key, label in labels.items():
        lines.extend([f"## {label}", ""])
        items = groups.get(key, [])
        if not items:
            lines.append("- none")
        else:
            for item in items:
                date_bits = []
                if item.effective_date:
                    date_bits.append(f"effective {item.effective_date}")
                if item.expiry_date:
                    date_bits.append(f"expires {item.expiry_date}")
                dates = f"; {', '.join(date_bits)}" if date_bits else ""
                lines.append(
                    f"- {item.title} ({item.community}; {item.authority_level}; {item.temporal_state}{dates}) "
                    f"- `{item.source_file}`"
                )
        lines.append("")
    return "\n".join(lines).strip()


def dashboard_payload(community: str = "", expiring_soon_days: int = 7, limit: int = 50) -> dict[str, Any]:
    resolved = resolve_community(community)
    items = build_items(resolved, expiring_soon_days, limit)
    groups = grouped_briefing(items, expiring_soon_days)
    return {
        "status": "ok",
        "community": resolved or "global",
        "expiring_soon_days": expiring_soon_days,
        "items": [item.as_dict() for item in items],
        "sections": {key: [item.as_dict() for item in value] for key, value in groups.items()},
        "briefing_markdown": format_briefing(groups),
        "warnings": [
            "dashboard is read-only and derived from indexed memory",
            "dashboard summaries do not override source authority",
        ],
    }


def filtered_payload(kind: str, community: str = "", expiring_soon_days: int = 7, limit: int = 50) -> dict[str, Any]:
    payload = dashboard_payload(community, expiring_soon_days, limit)
    items = [DashboardItem(**item) for item in payload["items"]]
    if kind == "announcements":
        filtered = [item for item in items if item.type == "announcement"]
    elif kind == "post_orders":
        filtered = [item for item in items if item.authority_level == "post_order" or item.type == "post_order"]
    elif kind == "issues":
        filtered = [
            item
            for item in items
            if text_matches(item, "gate", "nvr", "kiosk", "audio", "barrier", "id viewer", "traffic", "emergency")
        ]
    else:
        filtered = items
    payload["items"] = [item.as_dict() for item in filtered[:limit]]
    return payload
