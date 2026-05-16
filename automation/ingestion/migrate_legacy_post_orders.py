from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from refresh_post_orders import (
    POST_ORDER_DIR,
    REPO_ROOT,
    build_rule_id,
    metadata_scope_key,
    normalize_rule_text,
    rule_hash,
    slugify,
    topic_key,
)


REPORT_DIR = REPO_ROOT / "vault" / "08_Reports" / "post-order-migration"


@dataclass
class LegacyPostOrder:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    rule_text: str
    normalized_text: str
    rule_hash: str
    topic_key: str
    rule_id: str
    community: str
    community_code: str
    scope: list[str]
    scope_key: str
    review_required: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    markdown = markdown.lstrip("\ufeff")
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)
    if not match:
        return {}, markdown
    parsed = yaml.safe_load(match.group(1)) or {}
    return (parsed if isinstance(parsed, dict) else {}), markdown[match.end() :]


def section_text(body: str, section_name: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(section_name)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def metadata_value(frontmatter: dict[str, Any], key: str) -> str:
    value = frontmatter.get(key)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "").strip()


def community_code_for(community: str) -> str:
    known = {
        "sierra-ridge": "SR",
        "clearbrook-main": "CBK",
        "monterey": "MON",
    }
    return known.get(slugify(community), "")


def infer_scope(frontmatter: dict[str, Any], body: str) -> tuple[list[str], str, bool]:
    existing_scope = frontmatter.get("scope")
    if existing_scope:
        scope_key = metadata_scope_key(existing_scope)
        if scope_key == "k":
            return ["kiosk"], "k", False
        if scope_key == "c":
            return ["concierge"], "c", False
        if scope_key == "kc":
            return ["kiosk", "concierge"], "kc", False

    text = normalize_rule_text(body)
    if any(term in text for term in ["visitor", "overnight visitor", "before access", "granting access", "entry"]):
        return ["kiosk"], "k", False
    return [], "", True


def extract_rule_text(frontmatter: dict[str, Any], body: str) -> str:
    source_input = section_text(body, "Source Input")
    if source_input:
        return source_input
    details = section_text(body, "Details")
    if details:
        return details
    summary = section_text(body, "Summary")
    if summary:
        return summary
    title = metadata_value(frontmatter, "title")
    return title or body.strip()


def is_legacy_post_order(frontmatter: dict[str, Any]) -> bool:
    if str(frontmatter.get("type", "")) != "post_order":
        return False
    return (
        str(frontmatter.get("lifecycle_generation", "")) != "managed"
        or not str(frontmatter.get("rule_id", ""))
        or not str(frontmatter.get("rule_hash", ""))
    )


def read_legacy_post_orders() -> tuple[int, list[LegacyPostOrder], list[tuple[Path, str]]]:
    scanned = 0
    eligible: list[LegacyPostOrder] = []
    skipped: list[tuple[Path, str]] = []
    for path in sorted(POST_ORDER_DIR.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(raw)
        if str(frontmatter.get("type", "")) != "post_order":
            continue
        scanned += 1
        if not is_legacy_post_order(frontmatter):
            skipped.append((path, "already managed"))
            continue

        community = metadata_value(frontmatter, "community")
        if not community:
            skipped.append((path, "missing community"))
            continue

        rule_text = extract_rule_text(frontmatter, body)
        normalized = normalize_rule_text(rule_text)
        if not normalized:
            skipped.append((path, "empty rule text"))
            continue

        scope, scope_key, review_required = infer_scope(frontmatter, body)
        if review_required:
            skipped.append((path, "scope needs review"))
            continue

        hash_value = rule_hash(normalized)
        topic = topic_key(normalized)
        eligible.append(
            LegacyPostOrder(
                path=path,
                frontmatter=frontmatter,
                body=body,
                rule_text=rule_text,
                normalized_text=normalized,
                rule_hash=hash_value,
                topic_key=topic,
                rule_id=build_rule_id(community, scope_key, topic, hash_value),
                community=community,
                community_code=metadata_value(frontmatter, "community_code") or community_code_for(community),
                scope=scope,
                scope_key=scope_key,
                review_required=review_required,
            )
        )
    return scanned, eligible, skipped


def managed_hashes() -> set[str]:
    hashes: set[str] = set()
    for path in sorted(POST_ORDER_DIR.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        frontmatter, _body = split_frontmatter(raw)
        if str(frontmatter.get("type", "")) != "post_order":
            continue
        if str(frontmatter.get("lifecycle_generation", "")) == "managed":
            hash_value = str(frontmatter.get("rule_hash", ""))
            if hash_value:
                hashes.add(hash_value)
    return hashes


def yaml_frontmatter(metadata: dict[str, Any]) -> str:
    return yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()


def managed_output_path(rule: LegacyPostOrder) -> Path:
    filename = f"{slugify(rule.community, 36)}-managed-post-order-{rule.scope_key}-{rule.topic_key}-{rule.rule_hash[:10]}.md"
    return POST_ORDER_DIR / filename


def build_managed_markdown(rule: LegacyPostOrder) -> str:
    created = now_iso()
    title = metadata_value(rule.frontmatter, "title") or f"{rule.community} Post Order - {rule.topic_key.replace('-', ' ').title()}"
    source_file = rule.path.relative_to(REPO_ROOT).as_posix()
    metadata = {
        "title": title,
        "type": "post_order",
        "authority_level": "post_order",
        "lifecycle_generation": "managed",
        "status": "active",
        "community": rule.community,
        "community_code": rule.community_code,
        "scope": rule.scope,
        "scope_key": rule.scope_key,
        "rule_id": rule.rule_id,
        "rule_hash": rule.rule_hash,
        "topic_key": rule.topic_key,
        "source_legacy_file": source_file,
        "source_migration": "legacy_post_order",
        "migration_date": today(),
        "effective_date": metadata_value(rule.frontmatter, "effective_date"),
        "created_at": created,
        "last_updated": created,
        "tags": [
            "post_order",
            slugify(rule.community),
            rule.community_code.lower() if rule.community_code else slugify(rule.community),
            f"scope-{rule.scope_key}",
            "phase-4c2",
        ],
        "normalized_rule": rule.normalized_text,
    }
    return "\n".join(
        [
            "---",
            yaml_frontmatter(metadata),
            "---",
            "",
            f"# {title}",
            "",
            "## Rule",
            "",
            rule.rule_text,
            "",
            "## Scope",
            "",
            "- Marker: inferred legacy migration",
            *(f"- {item}" for item in rule.scope),
            "",
            "## Source",
            "",
            f"- Legacy File: {source_file}",
            "- Migration: legacy_post_order",
            "",
            "## Migration Notes",
            "",
            "- Original legacy file was preserved.",
            "- Migration used deterministic parsing only; no AI was used.",
            "",
        ]
    )


def build_report(
    scanned: int,
    converted: list[tuple[LegacyPostOrder, Path]],
    duplicates: list[tuple[LegacyPostOrder, str]],
    skipped: list[tuple[Path, str]],
    dry_run: bool,
) -> str:
    lines = [
        "# Legacy Post Order Migration Report",
        "",
        f"- Migration Date: {today()}",
        f"- Mode: {'dry-run' if dry_run else 'write'}",
        f"- Scanned Post Order Files: {scanned}",
        f"- Converted Files: {len(converted)}",
        f"- Duplicate Managed Rules: {len(duplicates)}",
        f"- Skipped / Needs Review: {len(skipped)}",
        "- Old legacy files were preserved.",
        "",
        "## Converted",
        "",
    ]
    if converted:
        for rule, output_path in converted:
            lines.append(
                f"- `{rule.path.relative_to(REPO_ROOT).as_posix()}` -> `{output_path.relative_to(REPO_ROOT).as_posix()}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Duplicate Managed Rules", ""])
    if duplicates:
        for rule, reason in duplicates:
            lines.append(f"- `{rule.path.relative_to(REPO_ROOT).as_posix()}` skipped: {reason}")
    else:
        lines.append("- none")

    lines.extend(["", "## Skipped / Needs Review", ""])
    if skipped:
        for path, reason in skipped:
            lines.append(f"- `{path.relative_to(REPO_ROOT).as_posix()}` skipped: {reason}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Reminder",
            "",
            "- Rebuild ChromaDB after accepting migration output.",
            "- Confirm migrated managed rules before operational reliance.",
            "",
        ]
    )
    return "\n".join(lines)


def report_path() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    return REPORT_DIR / f"{timestamp}-legacy-post-order-migration.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert eligible legacy post orders into managed lifecycle post orders.")
    parser.add_argument("--dry-run", action="store_true", help="Report migration actions without writing files.")
    args = parser.parse_args()

    scanned, eligible, skipped = read_legacy_post_orders()
    existing_hashes = managed_hashes()
    converted: list[tuple[LegacyPostOrder, Path]] = []
    duplicates: list[tuple[LegacyPostOrder, str]] = []

    if not args.dry_run:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for rule in eligible:
        if rule.rule_hash in existing_hashes:
            duplicates.append((rule, "same rule_hash already exists on a managed post order"))
            continue

        output_path = managed_output_path(rule)
        if output_path.exists():
            duplicates.append((rule, f"output already exists at {output_path.relative_to(REPO_ROOT).as_posix()}"))
            continue

        converted.append((rule, output_path))
        existing_hashes.add(rule.rule_hash)
        if not args.dry_run:
            output_path.write_text(build_managed_markdown(rule), encoding="utf-8")

    report = build_report(scanned, converted, duplicates, skipped, args.dry_run)
    print(report)

    if not args.dry_run:
        path = report_path()
        path.write_text(report, encoding="utf-8")
        print(f"Report written: {path.relative_to(REPO_ROOT).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
