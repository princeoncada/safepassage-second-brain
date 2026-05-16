from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ANNOUNCEMENT_DIR = REPO_ROOT / "vault" / "05_Announcements"
REPORT_DIR = REPO_ROOT / "vault" / "08_Reports" / "announcement-refresh"
ALIASES_PATH = REPO_ROOT / "rag" / "config" / "community_aliases.json"

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

COMMUNITY_PHRASE_ALIASES = {
    "gateway": ("Gateway Towers", "GWT"),
    "somerset run": ("Somerset", "SSR"),
    "clearbrook main": ("Clearbrook Main", "CBK"),
    "sierra ridge": ("Sierra Ridge", "SR"),
    "palm beach main": ("Palm Beach Main", "PBP"),
}


@dataclass
class AnnouncementItem:
    text: str
    normalized_text: str
    announcement_hash: str
    announcement_id: str
    title: str
    community: str
    community_code: str
    category: str
    status: str
    effective_date: str
    expires_on: str
    event_dates: list[str]
    review_required: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return (slug[:max_length].strip("-") or "announcement")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def announcement_hash(normalized_text: str) -> str:
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def load_aliases() -> dict[str, str]:
    if not ALIASES_PATH.exists():
        return {}
    parsed = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    return {str(key).upper(): str(value) for key, value in parsed.items()}


def alias_codes_by_community() -> dict[str, str]:
    aliases = load_aliases()
    return {slugify(community): code for code, community in aliases.items()}


def metadata_value(raw: str, key: str, default: str = "") -> str:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", raw, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def parse_header(raw: str) -> dict[str, str]:
    return {
        "batch_date": metadata_value(raw, "batch_date"),
        "source_name": metadata_value(raw, "source_name", "announcement_batch"),
        "update_type": metadata_value(raw, "update_type", "partial"),
        "default_status": metadata_value(raw, "default_status", "active"),
    }


def body_after_header(raw: str) -> str:
    lines = raw.splitlines()
    start = 0
    for index, line in enumerate(lines):
        if index == 0 and line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*[a-z_]+\s*:", line, re.IGNORECASE):
            continue
        if not line.strip():
            continue
        start = index
        break
    return "\n".join(lines[start:])


def parse_items(raw_body: str) -> list[str]:
    items: list[str] = []
    for raw_line in raw_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^[A-Za-z]+\s+\d{1,2},\s+\d{4}$", line):
            continue
        if line.endswith(":") and not line.startswith("-"):
            continue
        line = re.sub(r"^[-*]\s+", "", line).strip()
        if line:
            items.append(line)
    return items


def extract_date_after_phrase(text: str, phrase: str) -> str:
    pattern = re.compile(
        rf"{phrase}\s+([A-Za-z]+)\s+(\d{{1,2}}),\s+(\d{{4}})",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    month = MONTHS.get(match.group(1).lower())
    if not month:
        return ""
    return date(int(match.group(3)), month, int(match.group(2))).isoformat()


def extract_event_dates(text: str, batch_date: str) -> list[str]:
    year = int((batch_date or str(date.today()))[:4])
    dates: list[str] = []
    current_month = ""
    tokens = re.findall(r"\b(?:May|June|July|August|September|October|November|December|January|February|March|April)\b|\b\d{1,2}\b", text)
    for token in tokens:
        lower = token.lower()
        if lower in MONTHS:
            current_month = lower
            continue
        if current_month and token.isdigit():
            try:
                dates.append(date(year, MONTHS[current_month], int(token)).isoformat())
            except ValueError:
                continue
    return dates


def classify_item(text: str) -> str:
    normalized = normalize_text(text)
    if any(term in normalized for term in ["nvr", "id viewer"]):
        return "nvr_issue"
    if any(term in normalized for term in ["gate", "barrier arm", "kiosk audio"]):
        return "gate_issue"
    if any(term in normalized for term in ["pre-authorized", "preauthorized", "community approved list", "approved vendor", "gofo"]):
        return "approved_vendor"
    if any(term in normalized for term in ["tournament", "event", "games"]):
        return "event"
    if any(term in normalized for term in ["protocol", "extended to"]):
        return "temporary_protocol"
    if any(term in normalized for term in ["3cp", "traffic", "4-minute", "support room", "floater", "runners"]):
        return "traffic_handling"
    if any(term in normalized for term in ["termination", "required", "read your post orders", "watch community videos"]):
        return "compliance_warning"
    return "community_announcement" if extract_communities(text)[0] != "global" else "global_reminder"


def extract_communities(text: str) -> tuple[str, str, bool]:
    aliases = load_aliases()
    normalized = normalize_text(text)
    found: list[tuple[str, str]] = []

    for phrase, community_info in COMMUNITY_PHRASE_ALIASES.items():
        if phrase in normalized:
            found.append(community_info)

    for code, community in aliases.items():
        if re.search(rf"\b{re.escape(code)}\b", text, re.IGNORECASE):
            found.append((community, code))

    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for community, code in found:
        key = slugify(community)
        if key not in seen:
            deduped.append((community, code))
            seen.add(key)

    if not deduped:
        return "global", "", False
    if len(deduped) == 1:
        return deduped[0][0], deduped[0][1], False
    return "multiple", ",".join(code for _community, code in deduped if code), True


def status_for(text: str, default_status: str, batch_date: str) -> tuple[str, str, list[str]]:
    normalized = normalize_text(text)
    expires_on = extract_date_after_phrase(text, "extended to") or extract_date_after_phrase(text, "expires on")
    event_dates = extract_event_dates(text, batch_date)
    if "pending" in normalized:
        return "pending", expires_on, event_dates
    if expires_on and batch_date and expires_on < batch_date:
        return "expired", expires_on, event_dates
    return default_status or "active", expires_on, event_dates


def title_for(text: str, community: str, category: str) -> str:
    clean = re.sub(r"[:]+", " ", text).strip()
    title = clean[:90].strip()
    prefix = "" if community == "global" else f"{community} "
    return f"{prefix}{category.replace('_', ' ').title()} - {title}".strip()


def build_announcement_id(community: str, category: str, hash_value: str) -> str:
    return f"{slugify(community, 36)}-{slugify(category, 28)}-{hash_value[:10]}"


def build_items(raw: str) -> tuple[dict[str, str], list[AnnouncementItem]]:
    header = parse_header(raw)
    if not header["batch_date"]:
        raise SystemExit("Announcement batch is missing required field: batch_date")
    parsed_items = parse_items(body_after_header(raw))
    items: list[AnnouncementItem] = []
    for text in parsed_items:
        normalized = normalize_text(text)
        if not normalized:
            continue
        community, community_code, multi_review = extract_communities(text)
        category = classify_item(text)
        status, expires_on, event_dates = status_for(text, header["default_status"], header["batch_date"])
        if multi_review:
            status = "review"
        hash_value = announcement_hash(normalized)
        items.append(
            AnnouncementItem(
                text=text,
                normalized_text=normalized,
                announcement_hash=hash_value,
                announcement_id=build_announcement_id(community, category, hash_value),
                title=title_for(text, community, category),
                community=community,
                community_code=community_code,
                category=category,
                status=status,
                effective_date=header["batch_date"],
                expires_on=expires_on,
                event_dates=event_dates,
                review_required=multi_review or status == "review",
            )
        )
    return header, items


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    markdown = markdown.lstrip("\ufeff")
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)
    if not match:
        return {}, markdown
    parsed = yaml.safe_load(match.group(1)) or {}
    return (parsed if isinstance(parsed, dict) else {}), markdown[match.end() :]


def existing_hashes() -> set[str]:
    hashes: set[str] = set()
    if not ANNOUNCEMENT_DIR.exists():
        return hashes
    for path in sorted(ANNOUNCEMENT_DIR.rglob("*.md")):
        frontmatter, _body = split_frontmatter(path.read_text(encoding="utf-8"))
        if str(frontmatter.get("type", "")) == "announcement":
            hash_value = str(frontmatter.get("announcement_hash", ""))
            if hash_value:
                hashes.add(hash_value)
    return hashes


def yaml_frontmatter(metadata: dict[str, Any]) -> str:
    return yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()


def output_path(item: AnnouncementItem) -> Path:
    filename = f"{slugify(item.community, 36)}-{slugify(item.category, 32)}-{item.announcement_hash[:10]}.md"
    return ANNOUNCEMENT_DIR / filename


def build_markdown(item: AnnouncementItem, header: dict[str, str], input_path: Path) -> str:
    created = now_iso()
    metadata = {
        "title": item.title,
        "type": "announcement",
        "authority_level": "announcement",
        "lifecycle_generation": "managed",
        "status": item.status,
        "announcement_id": item.announcement_id,
        "announcement_hash": item.announcement_hash,
        "community": item.community,
        "community_code": item.community_code,
        "category": item.category,
        "batch_date": header["batch_date"],
        "effective_date": item.effective_date,
        "expires_on": item.expires_on,
        "event_dates": item.event_dates,
        "source_batch": input_path.relative_to(REPO_ROOT).as_posix(),
        "source_name": header["source_name"],
        "update_type": header["update_type"],
        "created_at": created,
        "last_updated": created,
        "tags": [
            "announcement",
            item.category,
            slugify(item.community),
            item.community_code.lower() if item.community_code else "global",
            "phase-4c3",
        ],
        "normalized_announcement": item.normalized_text,
    }
    return "\n".join(
        [
            "---",
            yaml_frontmatter(metadata),
            "---",
            "",
            f"# {item.title}",
            "",
            "## Announcement",
            "",
            item.text,
            "",
            "## Operational Notes",
            "",
            f"- Category: {item.category}",
            f"- Status: {item.status}",
            f"- Community: {item.community}",
            "- Announcements do not override active post orders.",
            "",
            "## Source",
            "",
            f"- Batch: {input_path.relative_to(REPO_ROOT).as_posix()}",
            f"- Source Name: {header['source_name']}",
            f"- Batch Date: {header['batch_date']}",
            "",
        ]
    )


def build_report(
    header: dict[str, str],
    input_path: Path,
    added: list[tuple[AnnouncementItem, Path | None]],
    duplicates: list[AnnouncementItem],
    review_items: list[AnnouncementItem],
    advisory_items: list[AnnouncementItem],
    dry_run: bool,
) -> str:
    communities = sorted({item.community for item, _path in added} | {item.community for item in duplicates + review_items})
    categories = sorted({item.category for item, _path in added} | {item.category for item in duplicates + review_items})
    lines = [
        "# Announcement Refresh Report",
        "",
        f"- Batch Date: {header['batch_date']}",
        f"- Source Name: {header['source_name']}",
        f"- Update Type: {header['update_type']}",
        f"- Input File: {input_path.relative_to(REPO_ROOT).as_posix()}",
        f"- Mode: {'dry-run' if dry_run else 'write'}",
        f"- Communities Detected: {', '.join(communities) if communities else 'none'}",
        f"- Categories Detected: {', '.join(categories) if categories else 'none'}",
        "",
        "## Added Announcements",
        "",
    ]
    if added:
        for item, path in added:
            suffix = f" -> `{path.relative_to(REPO_ROOT).as_posix()}`" if path else ""
            lines.append(f"- `{item.announcement_id}` ({item.community}, {item.category}, {item.status}){suffix}")
    else:
        lines.append("- none")

    lines.extend(["", "## Unchanged / Duplicate Announcements", ""])
    if duplicates:
        lines.extend(f"- `{item.announcement_id}` duplicate hash" for item in duplicates)
    else:
        lines.append("- none")

    lines.extend(["", "## Review Needed", ""])
    if review_items:
        lines.extend(f"- `{item.announcement_id}` ({item.community}): {item.text}" for item in review_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Pending / Expired Advisory Items", ""])
    if advisory_items:
        lines.extend(f"- `{item.announcement_id}` status={item.status}: {item.text}" for item in advisory_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Reminder",
            "",
            "- Rebuild ChromaDB after accepting announcement refresh output.",
            "- Announcements are lower authority than post orders and higher authority than primary workflow.",
            "- OCR is deferred; this script expects cleaned pasted text.",
            "",
        ]
    )
    return "\n".join(lines)


def report_path(header: dict[str, str]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    return REPORT_DIR / f"{header['batch_date']}-announcement-refresh-{timestamp}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh managed announcements from cleaned pasted text.")
    parser.add_argument("--input", required=True, help="Markdown or TXT announcement batch input.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing vault files.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    header, items = build_items(input_path.read_text(encoding="utf-8"))
    hashes = existing_hashes()
    added: list[tuple[AnnouncementItem, Path | None]] = []
    duplicates: list[AnnouncementItem] = []
    review_items: list[AnnouncementItem] = []
    advisory_items: list[AnnouncementItem] = []

    if not args.dry_run:
        ANNOUNCEMENT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for item in items:
        if item.announcement_hash in hashes:
            duplicates.append(item)
            continue
        if item.review_required:
            review_items.append(item)
        if item.status in {"pending", "expired"}:
            advisory_items.append(item)
        path = None if args.dry_run else output_path(item)
        added.append((item, path))
        hashes.add(item.announcement_hash)
        if path:
            path.write_text(build_markdown(item, header, input_path), encoding="utf-8")

    report = build_report(header, input_path, added, duplicates, review_items, advisory_items, args.dry_run)
    print(report)

    if not args.dry_run:
        path = report_path(header)
        path.write_text(report, encoding="utf-8")
        print(f"Report written: {path.relative_to(REPO_ROOT).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
