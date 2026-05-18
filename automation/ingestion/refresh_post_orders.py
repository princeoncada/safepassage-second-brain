from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
POST_ORDER_DIR = REPO_ROOT / "vault" / "03_Post_Orders"
REPORT_DIR = REPO_ROOT / "vault" / "08_Reports" / "post-order-refresh"

DECORATIVE_LINE = re.compile(r"^\s*[-=_*]{3,}\s*$")
POST_ORDER_PATTERN = re.compile(
    r"(?:^\s*\d{1,2}/\d{1,2}/\d{4}\s*\n)?\s*POST\s+ORDERS?\s*\((K\s*(?:&|AND)\s*C|K&C|K|C)\)\s*:\s*(.*?)(?=\n\s*(?:\d{1,2}/\d{1,2}/\d{4}\s*\n)?\s*POST\s+ORDERS?\s*\(|\Z)",
    re.IGNORECASE | re.DOTALL,
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "before",
    "by",
    "for",
    "from",
    "if",
    "in",
    "is",
    "must",
    "of",
    "or",
    "the",
    "to",
    "when",
    "with",
}
REVIEW_TOPIC_SIMILARITY_THRESHOLD = 0.55
NUMBER_WORDS = {
    "one": 1,
    "once": 1,
    "two": 2,
    "twice": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


@dataclass
class IncomingRule:
    community: str
    community_code: str
    batch_date: str
    update_type: str
    supersede_mode: str
    scope_marker: str
    scope: list[str]
    scope_key: str
    original_text: str
    normalized_text: str
    rule_hash: str
    topic_key: str
    rule_id: str


@dataclass
class ExistingRule:
    path: Path
    frontmatter: dict[str, Any]
    body: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return (slug[:max_length].strip("-") or "rule")


def scope_from_marker(marker: str) -> tuple[list[str], str]:
    normalized = re.sub(r"\s+", "", marker.upper())
    if normalized == "K":
        return ["kiosk"], "k"
    if normalized == "C":
        return ["concierge"], "c"
    return ["kiosk", "concierge"], "kc"


def normalize_scope_marker(marker: str) -> str:
    normalized = re.sub(r"\s+", "", marker.upper()).replace("AND", "&")
    if normalized == "K&C":
        return "K&C"
    return normalized


def normalize_rule_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if not DECORATIVE_LINE.match(line)]
    return re.sub(r"\s+", " ", " ".join(lines).lower()).strip()


def rule_hash(normalized_text: str) -> str:
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def topic_key(normalized_text: str) -> str:
    words = [word for word in re.findall(r"[a-z0-9]+", normalized_text) if word not in STOPWORDS]
    return slugify("-".join(words[:6]), max_length=48)


def build_rule_id(community: str, scope_key: str, topic: str, hash_value: str) -> str:
    return f"{slugify(community, 36)}-{scope_key}-{topic}-{hash_value[:10]}"


def metadata_value(raw: str, key: str, default: str = "") -> str:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", raw, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def parse_batch(input_path: Path) -> tuple[str, str, str, str, str, list[IncomingRule]]:
    raw = input_path.read_text(encoding="utf-8")
    community = metadata_value(raw, "community")
    batch_date = metadata_value(raw, "batch_date")
    community_code = metadata_value(raw, "community_code")
    update_type = metadata_value(raw, "update_type", "full")
    supersede_mode = metadata_value(raw, "supersede_mode", "conservative")
    if not community:
        raise SystemExit("Batch input is missing required field: community")
    if not batch_date:
        raise SystemExit("Batch input is missing required field: batch_date")

    rules: list[IncomingRule] = []
    for match in POST_ORDER_PATTERN.finditer(raw):
        marker = normalize_scope_marker(match.group(1))
        original_text = match.group(2).strip()
        normalized_text = normalize_rule_text(original_text)
        if not normalized_text:
            continue
        hash_value = rule_hash(normalized_text)
        scope, scope_key = scope_from_marker(marker)
        topic = topic_key(normalized_text)
        rules.append(
            IncomingRule(
                community=community,
                community_code=community_code,
                batch_date=batch_date,
                update_type=update_type,
                supersede_mode=supersede_mode,
                scope_marker=marker,
                scope=scope,
                scope_key=scope_key,
                original_text=original_text,
                normalized_text=normalized_text,
                rule_hash=hash_value,
                topic_key=topic,
                rule_id=build_rule_id(community, scope_key, topic, hash_value),
            )
        )

    rules.reverse()

    if not rules:
        raise SystemExit("No post order entries found. Expected lines like: POST ORDER (K): text")
    return community, community_code, batch_date, update_type, supersede_mode, rules


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)
    if not match:
        return {}, markdown
    parsed = yaml.safe_load(match.group(1)) or {}
    return (parsed if isinstance(parsed, dict) else {}), markdown[match.end() :]


def read_existing_rules() -> list[ExistingRule]:
    rules: list[ExistingRule] = []
    if not POST_ORDER_DIR.exists():
        return rules
    for path in sorted(POST_ORDER_DIR.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(raw)
        if str(frontmatter.get("type", "")) == "post_order":
            rules.append(ExistingRule(path=path, frontmatter=frontmatter, body=body))
    return rules


def metadata_scope_key(value: Any) -> str:
    if isinstance(value, list):
        values = {str(item) for item in value}
    else:
        values = {part.strip() for part in str(value or "").split(",") if part.strip()}
    if {"kiosk", "concierge"} <= values:
        return "kc"
    if "kiosk" in values:
        return "k"
    if "concierge" in values:
        return "c"
    return slugify(",".join(sorted(values)), 12)


def same_community_scope(existing: ExistingRule, incoming: IncomingRule) -> bool:
    community = str(existing.frontmatter.get("community", ""))
    scope_key = str(existing.frontmatter.get("scope_key") or metadata_scope_key(existing.frontmatter.get("scope")))
    return slugify(community) == slugify(incoming.community) and scope_key == incoming.scope_key


def active_managed_rules(existing_rules: list[ExistingRule], community: str) -> list[ExistingRule]:
    return [
        rule
        for rule in existing_rules
        if slugify(str(rule.frontmatter.get("community", ""))) == slugify(community)
        and str(rule.frontmatter.get("status", "active")) == "active"
        and str(rule.frontmatter.get("rule_hash", ""))
    ]


def extract_call_count(text: str) -> int | None:
    match = re.search(r"call\s+(?:the\s+)?resident\s+(\d+|one|once|two|twice|three|four|five)\s+times?", text)
    if not match:
        return None
    value = match.group(1)
    if value.isdigit():
        return int(value)
    return NUMBER_WORDS.get(value)


def conflict_reasons(left: str, right: str) -> list[str]:
    reasons: list[str] = []
    left_count = extract_call_count(left)
    right_count = extract_call_count(right)
    if left_count is not None and right_count is not None and left_count != right_count:
        reasons.append(f"resident call count differs ({left_count} vs {right_count})")

    if ("do not save tag" in left and "save tag" in right) or ("save tag" in left and "do not save tag" in right):
        reasons.append("save tag instruction may conflict")

    left_requires_physical = "physical id" in left and any(term in left for term in ["required", "must present", "before access"])
    right_requires_physical = "physical id" in right and any(term in right for term in ["required", "must present", "before access"])
    left_accepts_digital = "digital id" in left and any(term in left for term in ["accepted", "accept digital", "allow digital"])
    right_accepts_digital = "digital id" in right and any(term in right for term in ["accepted", "accept digital", "allow digital"])
    if (left_requires_physical and right_accepts_digital) or (right_requires_physical and left_accepts_digital):
        reasons.append("physical ID requirement may conflict with digital ID acceptance")

    return reasons


def find_duplicate(incoming: IncomingRule, active_rules: list[ExistingRule]) -> ExistingRule | None:
    for existing in active_rules:
        if same_community_scope(existing, incoming) and str(existing.frontmatter.get("rule_hash", "")) == incoming.rule_hash:
            return existing
    return None


def find_same_topic(incoming: IncomingRule, active_rules: list[ExistingRule]) -> ExistingRule | None:
    for existing in active_rules:
        if not same_community_scope(existing, incoming):
            continue
        if str(existing.frontmatter.get("topic_key", "")) == incoming.topic_key:
            return existing
    return None


def token_similarity(left: str, right: str) -> float:
    left_tokens = {token for token in left.split("-") if token}
    right_tokens = {token for token in right.split("-") if token}
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def find_possible_change(incoming: IncomingRule, active_rules: list[ExistingRule]) -> ExistingRule | None:
    best_rule: ExistingRule | None = None
    best_score = 0.0
    for existing in active_rules:
        if not same_community_scope(existing, incoming):
            continue
        existing_topic = str(existing.frontmatter.get("topic_key", ""))
        if not existing_topic or existing_topic == incoming.topic_key:
            continue
        score = token_similarity(existing_topic, incoming.topic_key)
        if score > best_score:
            best_score = score
            best_rule = existing
    if best_score >= REVIEW_TOPIC_SIMILARITY_THRESHOLD:
        return best_rule
    return None


def find_conflicts(incoming: IncomingRule, active_rules: list[ExistingRule]) -> list[tuple[ExistingRule, list[str]]]:
    conflicts: list[tuple[ExistingRule, list[str]]] = []
    for existing in active_rules:
        if not same_community_scope(existing, incoming):
            continue
        existing_text = normalize_rule_text(str(existing.frontmatter.get("normalized_rule") or existing.body))
        reasons = conflict_reasons(existing_text, incoming.normalized_text)
        if reasons:
            conflicts.append((existing, reasons))
    return conflicts


def yaml_frontmatter(metadata: dict[str, Any]) -> str:
    return yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()


def build_rule_markdown(incoming: IncomingRule, status: str, input_file: Path, supersedes: str = "") -> str:
    created = now_iso()
    title = f"{incoming.community} Post Order - {incoming.topic_key.replace('-', ' ').title()}"
    effective_status = (
        "pending"
        if status == "active" and re.search(r"\(Pending\)\s*$", incoming.original_text, re.IGNORECASE)
        else status
    )
    metadata = {
        "title": title,
        "type": "post_order",
        "authority_level": "post_order",
        "community": incoming.community,
        "community_code": incoming.community_code,
        "scope": incoming.scope,
        "scope_key": incoming.scope_key,
        "status": effective_status,
        "lifecycle_generation": "managed",
        "rule_id": incoming.rule_id,
        "rule_hash": incoming.rule_hash,
        "topic_key": incoming.topic_key,
        "source_batch": input_file.relative_to(REPO_ROOT).as_posix(),
        "batch_date": incoming.batch_date,
        "update_type": incoming.update_type,
        "supersede_mode": incoming.supersede_mode,
        "effective_date": incoming.batch_date,
        "supersedes": supersedes,
        "superseded_by": "",
        "created_at": created,
        "last_updated": created,
        "tags": [
            "post_order",
            slugify(incoming.community),
            incoming.community_code.lower() if incoming.community_code else slugify(incoming.community),
            f"scope-{incoming.scope_key}",
            "phase-4c",
        ],
        "normalized_rule": incoming.normalized_text,
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
            incoming.original_text,
            "",
            "## Scope",
            "",
            f"- Marker: {incoming.scope_marker}",
            *(f"- {item}" for item in incoming.scope),
            "",
            "## Source",
            "",
            f"- Batch: {input_file.relative_to(REPO_ROOT).as_posix()}",
            f"- Batch Date: {incoming.batch_date}",
            "",
            "## Change History",
            "",
            f"- {created}: Created by Phase 4C post order refresh.",
            "",
        ]
    )


def write_rule(incoming: IncomingRule, status: str, input_file: Path, supersedes: str = "") -> Path:
    filename = f"{slugify(incoming.community, 36)}-post-order-{incoming.scope_key}-{incoming.topic_key}-{incoming.rule_hash[:10]}.md"
    if status == "conflict":
        filename = f"{slugify(incoming.community, 36)}-post-order-conflict-{incoming.scope_key}-{incoming.topic_key}-{incoming.rule_hash[:10]}.md"
    if status == "review":
        filename = f"{slugify(incoming.community, 36)}-post-order-review-{incoming.scope_key}-{incoming.topic_key}-{incoming.rule_hash[:10]}.md"
    output_path = POST_ORDER_DIR / filename
    output_path.write_text(build_rule_markdown(incoming, status, input_file, supersedes), encoding="utf-8")
    return output_path


def update_existing_frontmatter(rule: ExistingRule, updates: dict[str, Any]) -> None:
    raw = rule.path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)
    frontmatter.update(updates)
    rule.path.write_text(f"---\n{yaml_frontmatter(frontmatter)}\n---\n{body}", encoding="utf-8")


def build_report(
    community: str,
    community_code: str,
    batch_date: str,
    update_type: str,
    supersede_mode: str,
    input_path: Path,
    dry_run: bool,
    added: list[tuple[IncomingRule, Path | None]],
    duplicates: list[tuple[IncomingRule, ExistingRule]],
    superseded: list[tuple[ExistingRule, IncomingRule, Path | None]],
    conflicts: list[tuple[IncomingRule, list[tuple[ExistingRule, list[str]]], Path | None]],
    possible_changes: list[tuple[IncomingRule, ExistingRule, Path | None]],
    missing: list[ExistingRule],
) -> str:
    def rule_line(rule: IncomingRule, path: Path | None = None) -> str:
        suffix = f" -> `{path.relative_to(REPO_ROOT).as_posix()}`" if path else ""
        return f"- `{rule.rule_id}` ({rule.scope_key}) {rule.original_text}{suffix}"

    lines = [
        "# Post Order Refresh Report",
        "",
        f"- Community: {community}",
        f"- Community Code: {community_code or 'not provided'}",
        f"- Batch Date: {batch_date}",
        f"- Update Type: {update_type}",
        f"- Supersede Mode: {supersede_mode}",
        f"- Input File: {input_path.relative_to(REPO_ROOT).as_posix()}",
        f"- Mode: {'dry-run' if dry_run else 'write'}",
        "",
        "## Added Rules",
        "",
    ]
    lines.extend(rule_line(rule, path) for rule, path in added)
    if not added:
        lines.append("- none")

    lines.extend(["", "## Unchanged / Duplicate Rules", ""])
    lines.extend(
        f"- `{rule.rule_id}` duplicates `{existing.path.relative_to(REPO_ROOT).as_posix()}`"
        for rule, existing in duplicates
    )
    if not duplicates:
        lines.append("- none")

    lines.extend(["", "## Superseded Rules", ""])
    lines.extend(
        f"- `{old.frontmatter.get('rule_id')}` superseded by `{new.rule_id}`"
        + (f" -> `{path.relative_to(REPO_ROOT).as_posix()}`" if path else "")
        for old, new, path in superseded
    )
    if not superseded:
        lines.append("- none")

    lines.extend(["", "## Possible Conflicts", ""])
    for rule, conflict_items, path in conflicts:
        lines.append(rule_line(rule, path))
        for existing, reasons in conflict_items:
            lines.append(f"  - Existing: `{existing.path.relative_to(REPO_ROOT).as_posix()}`")
            for reason in reasons:
                lines.append(f"  - Warning: {reason}")
    if not conflicts:
        lines.append("- none")

    lines.extend(["", "## Possible Changes / Review", ""])
    lines.extend(
        f"- `{rule.rule_id}` may relate to `{existing.frontmatter.get('rule_id')}`; written as review"
        + (f" -> `{path.relative_to(REPO_ROOT).as_posix()}`" if path else "")
        for rule, existing, path in possible_changes
    )
    if not possible_changes:
        lines.append("- none")

    lines.extend(["", "## Missing From Latest Batch", ""])
    if update_type.lower() == "partial":
        lines.append("- skipped because update_type is partial")
    else:
        lines.extend(
            f"- `{rule.frontmatter.get('rule_id')}` at `{rule.path.relative_to(REPO_ROOT).as_posix()}` needs manual review"
            for rule in missing
        )
        if not missing:
            lines.append("- none")

    lines.extend(
        [
            "",
            "## Manual Review Required",
            "",
            "- Review possible conflicts before relying on them operationally.",
            "- Review missing active rules before marking anything inactive.",
            "- Rebuild ChromaDB after accepting a refresh:",
            "",
            "```powershell",
            "python rag/scripts/reset_chroma.py --yes",
            "python rag/scripts/index_vault.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def report_path(community: str, batch_date: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    return REPORT_DIR / f"{batch_date}-{slugify(community)}-post-order-refresh-{timestamp}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh post orders from a deterministic batch input.")
    parser.add_argument("--input", required=True, help="Markdown or TXT post order batch input.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing vault files.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    community, community_code, batch_date, update_type, supersede_mode, incoming_rules = parse_batch(input_path)
    active_rules = active_managed_rules(read_existing_rules(), community)
    incoming_hashes = {rule.rule_hash for rule in incoming_rules}

    added: list[tuple[IncomingRule, Path | None]] = []
    duplicates: list[tuple[IncomingRule, ExistingRule]] = []
    superseded: list[tuple[ExistingRule, IncomingRule, Path | None]] = []
    conflicts: list[tuple[IncomingRule, list[tuple[ExistingRule, list[str]]], Path | None]] = []
    possible_changes: list[tuple[IncomingRule, ExistingRule, Path | None]] = []

    POST_ORDER_DIR.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for incoming in incoming_rules:
        duplicate = find_duplicate(incoming, active_rules)
        if duplicate:
            duplicates.append((incoming, duplicate))
            continue

        conflict_items = find_conflicts(incoming, active_rules)
        if conflict_items:
            path = None if args.dry_run else write_rule(incoming, "conflict", input_path)
            conflicts.append((incoming, conflict_items, path))
            continue

        same_topic = find_same_topic(incoming, active_rules)
        if same_topic:
            path = None if args.dry_run else write_rule(
                incoming,
                "active",
                input_path,
                supersedes=str(same_topic.frontmatter.get("rule_id", "")),
            )
            if not args.dry_run:
                update_existing_frontmatter(
                    same_topic,
                    {
                        "status": "superseded",
                        "superseded_by": incoming.rule_id,
                        "last_updated": now_iso(),
                    },
                )
            superseded.append((same_topic, incoming, path))
            continue

        if incoming.supersede_mode.lower() == "conservative":
            possible_change = find_possible_change(incoming, active_rules)
            if possible_change:
                path = None if args.dry_run else write_rule(incoming, "review", input_path)
                possible_changes.append((incoming, possible_change, path))
                continue

        path = None if args.dry_run else write_rule(incoming, "active", input_path)
        added.append((incoming, path))

    missing = [
        rule
        for rule in active_rules
        if str(rule.frontmatter.get("rule_hash", "")) not in incoming_hashes
        and not any(rule is old for old, _new, _path in superseded)
    ]

    report = build_report(
        community,
        community_code,
        batch_date,
        update_type,
        supersede_mode,
        input_path,
        args.dry_run,
        added,
        duplicates,
        superseded,
        conflicts,
        possible_changes,
        missing,
    )
    print(report)

    if not args.dry_run:
        path = report_path(community, batch_date)
        path.write_text(report, encoding="utf-8")
        print(f"Report written: {path.relative_to(REPO_ROOT).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
