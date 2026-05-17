from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


START_DATE_FIELDS = ("active_from", "effective_date", "start_date")
END_DATE_FIELDS = ("active_until", "expires_at", "expiry_date", "end_date", "expires_on")
STATUS_FIELDS = ("lifecycle_status", "status")

STATIC_REVIEW_STATUSES = {"needs_review", "review", "rejected", "conflict", "draft"}
STATIC_ARCHIVED_STATUSES = {"archived", "inactive"}
STATIC_SUPERSEDED_STATUSES = {"superseded"}
PENDING_STATUSES = {"pending", "pending_review"}
ACTIVE_STATUSES = {"active"}


@dataclass(frozen=True)
class TemporalLifecycle:
    status: str
    temporal_state: str
    temporal_warning: str
    start_date: str
    start_date_field: str
    end_date: str
    end_date_field: str

    def as_metadata(self) -> dict[str, str]:
        return {
            "temporal_state": self.temporal_state,
            "temporal_warning": self.temporal_warning,
            "temporal_start_date": self.start_date,
            "temporal_start_field": self.start_date_field,
            "temporal_end_date": self.end_date,
            "temporal_end_field": self.end_date_field,
        }


def normalize_status(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def first_metadata_value(metadata: dict[str, Any], fields: tuple[str, ...]) -> tuple[str, Any]:
    for field in fields:
        value = metadata.get(field)
        if value not in (None, ""):
            return field, value
    return "", ""


def parse_iso_date(value: Any) -> tuple[date | None, str]:
    if value in (None, ""):
        return None, ""
    if isinstance(value, datetime):
        return value.date(), value.date().isoformat()
    if isinstance(value, date):
        return value, value.isoformat()

    raw = str(value).strip().strip("'\"")
    if not raw:
        return None, ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.date(), parsed.date().isoformat()
    except ValueError:
        pass
    try:
        parsed_date = date.fromisoformat(raw[:10])
        return parsed_date, parsed_date.isoformat()
    except ValueError:
        return None, ""


def today_date(today: date | datetime | str | None = None) -> date:
    if today is None:
        return date.today()
    parsed, normalized = parse_iso_date(today)
    if parsed is None:
        raise ValueError(f"Invalid today value: {today}")
    return parsed


def temporal_lifecycle(metadata: dict[str, Any], today: date | datetime | str | None = None) -> TemporalLifecycle:
    current_date = today_date(today)
    status_field, status_value = first_metadata_value(metadata, STATUS_FIELDS)
    status = normalize_status(status_value)

    start_field, raw_start = first_metadata_value(metadata, START_DATE_FIELDS)
    end_field, raw_end = first_metadata_value(metadata, END_DATE_FIELDS)
    start, normalized_start = parse_iso_date(raw_start)
    end, normalized_end = parse_iso_date(raw_end)

    warnings: list[str] = []
    if raw_start not in (None, "") and start is None:
        warnings.append(f"invalid {start_field}: {raw_start}")
        start_field = ""
    if raw_end not in (None, "") and end is None:
        warnings.append(f"invalid {end_field}: {raw_end}")
        end_field = ""

    if status in STATIC_SUPERSEDED_STATUSES or str(metadata.get("superseded_by", "")).strip():
        state = "superseded"
    elif status in STATIC_ARCHIVED_STATUSES:
        state = "archived"
    elif status in STATIC_REVIEW_STATUSES:
        state = "review"
    elif start and start > current_date:
        state = "pending" if status in PENDING_STATUSES else "not_yet_active"
    elif end and end < current_date:
        state = "expired"
    elif start or end:
        state = "active" if status not in PENDING_STATUSES else "pending"
    elif status in ACTIVE_STATUSES:
        state = "active"
        warnings.append("missing temporal metadata")
    elif status in PENDING_STATUSES:
        state = "pending"
        warnings.append("missing temporal metadata")
    else:
        state = "unknown"
        warnings.append("missing temporal metadata")

    return TemporalLifecycle(
        status=status,
        temporal_state=state,
        temporal_warning="; ".join(warnings),
        start_date=normalized_start,
        start_date_field=start_field if normalized_start else "",
        end_date=normalized_end,
        end_date_field=end_field if normalized_end else "",
    )
