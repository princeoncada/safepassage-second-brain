from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rag.lifecycle import END_DATE_FIELDS, START_DATE_FIELDS, temporal_lifecycle


VAULT_DIR = REPO_ROOT / "vault"
REPORT_DIR = VAULT_DIR / "08_Reports" / "temporal-lifecycle"


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    markdown = markdown.lstrip("\ufeff")
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)
    if not match:
        return {}, markdown
    parsed = yaml.safe_load(match.group(1)) or {}
    return (parsed if isinstance(parsed, dict) else {}), markdown[match.end() :]


def iter_markdown_files(include_archive: bool) -> list[Path]:
    files = sorted(VAULT_DIR.rglob("*.md"))
    if include_archive:
        return files
    return [path for path in files if "99_Archive" not in path.relative_to(VAULT_DIR).parts]


def value(metadata: dict[str, Any], key: str) -> str:
    raw = metadata.get(key, "")
    if isinstance(raw, list):
        return ", ".join(str(item) for item in raw)
    return str(raw or "")


def date_fields(metadata: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in START_DATE_FIELDS + END_DATE_FIELDS:
        raw = value(metadata, field)
        if raw:
            parts.append(f"{field}: {raw}")
    return "; ".join(parts) if parts else "none"


def report_line(item: dict[str, Any]) -> str:
    warning = f" - warning: {item['warning']}" if item["warning"] else ""
    return (
        f"- `{item['path']}` - {item['title']} "
        f"({item['authority'] or item['type'] or 'unknown'}, community={item['community'] or 'global'}, "
        f"status={item['status'] or 'none'}, dates={item['dates']}){warning}"
    )


def group_items(items: list[dict[str, Any]], expiring_soon_days: int) -> dict[str, list[dict[str, Any]]]:
    current = date.today()
    soon_cutoff = current + timedelta(days=expiring_soon_days)
    grouped = {
        "active": [],
        "pending / not yet active": [],
        "expiring soon": [],
        "expired": [],
        "review / unknown temporal metadata": [],
        "superseded / archived": [],
    }
    for item in items:
        state = item["temporal_state"]
        end_date = item.get("temporal_end")
        if state == "active":
            grouped["active"].append(item)
            if end_date and current <= end_date <= soon_cutoff:
                grouped["expiring soon"].append(item)
        elif state in {"pending", "not_yet_active"}:
            grouped["pending / not yet active"].append(item)
        elif state == "expired":
            grouped["expired"].append(item)
        elif state in {"superseded", "archived"}:
            grouped["superseded / archived"].append(item)
        else:
            grouped["review / unknown temporal metadata"].append(item)
    return grouped


def build_report(items: list[dict[str, Any]], expiring_soon_days: int, include_archive: bool) -> str:
    grouped = group_items(items, expiring_soon_days)
    lines = [
        "# Temporal Lifecycle Report",
        "",
        f"- Generated Date: {date.today().isoformat()}",
        f"- Expiring Soon Window: {expiring_soon_days} days",
        f"- Include Archive: {str(include_archive).lower()}",
        f"- Source: `vault/` Markdown frontmatter",
        "- This report is read-only operational review output. It does not update source memory or ChromaDB.",
        "",
    ]
    for title, group in grouped.items():
        lines.extend([f"## {title.title()}", ""])
        if group:
            lines.extend(report_line(item) for item in group)
        else:
            lines.append("- none")
        lines.append("")
    return "\n".join(lines)


def build_items(include_archive: bool) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in iter_markdown_files(include_archive):
        if REPORT_DIR in path.parents:
            continue
        raw = path.read_text(encoding="utf-8")
        frontmatter, _body = split_frontmatter(raw)
        temporal = temporal_lifecycle(frontmatter)
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        items.append(
            {
                "path": relative_path,
                "title": value(frontmatter, "title") or path.stem,
                "type": value(frontmatter, "document_type") or value(frontmatter, "type"),
                "authority": value(frontmatter, "authority_level"),
                "community": value(frontmatter, "community"),
                "status": value(frontmatter, "lifecycle_status") or value(frontmatter, "status"),
                "dates": date_fields(frontmatter),
                "warning": temporal.temporal_warning,
                "temporal_state": temporal.temporal_state,
                "temporal_end": temporal.end_date and date.fromisoformat(temporal.end_date),
            }
        )
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a read-only temporal lifecycle report from vault Markdown.")
    parser.add_argument("--expiring-soon-days", type=int, default=7, help="Days ahead to flag expiring active records.")
    parser.add_argument("--include-archive", action="store_true", help="Include vault/99_Archive in the report.")
    args = parser.parse_args()

    if not VAULT_DIR.exists():
        raise SystemExit(f"Vault directory not found: {VAULT_DIR}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report(build_items(args.include_archive), args.expiring_soon_days, args.include_archive)
    output_path = REPORT_DIR / f"{date.today().isoformat()}-temporal-lifecycle-report.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written: {output_path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
