from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import yaml
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any

from rag.vault_schema import validate_frontmatter


REPO_ROOT = Path(__file__).resolve().parents[1]
INGESTION_DIR = REPO_ROOT / "automation" / "ingestion"
ALIAS_PATH = REPO_ROOT / "rag" / "config" / "community_aliases.json"
VAULT_POST_ORDER_DIR = REPO_ROOT / "vault" / "03_Post_Orders"
PENDING_KEY = "pending_ingest"
WIZARD_KEY = "wizard_ingest"
PENDING_TTL_MINUTES = 5

pending_state: dict[str, dict[str, Any]] = {}

DATE_PATTERN = re.compile(r"(?<!\d)\d{1,2}/\d{1,2}/\d{4}(?!\d)")
POST_ORDER_LABEL_PATTERN = re.compile(
    r"POST\s+ORDERS?\s*\(\s*(K\s*(?:&|AND)\s*C|K\s*&\s*C|KC|K|C)\s*\)\s*:\s*(.*)",
    re.IGNORECASE | re.DOTALL,
)
NUMBERED_ITEM_PATTERN = re.compile(r"(?:^|\n)\s*\d+[\.)]\s+")

CATEGORY_KEYWORDS = [
    ("gate_issue", ["gate", "barrier", "arm", "open"]),
    ("nvr_issue", ["nvr", "camera", "feed", "delayed", "viewer"]),
    ("event", ["tournament", "event", "scheduled", "contest", "pickleball"]),
    ("approved_vendor", ["vendor", "approved", "pre-authorized", "preauthorized", "gofo"]),
    ("temporary_protocol", ["protocol", "red zone", "emergency", "code"]),
    ("compliance_warning", ["compliance", "termination", "required", "policy", "unauthorized"]),
    ("traffic_handling", ["traffic", "support room", "4-minute", "floater"]),
]

TOPIC_STOPWORDS = {
    "a", "an", "and", "are", "before", "by", "for", "from",
    "if", "in", "is", "must", "of", "or", "the", "to", "when", "with",
}

ANCHOR_STOPWORDS = {
    "required", "at", "all", "times", "not", "with", "for", "the",
    "and", "or", "a", "an", "is", "are", "must", "before", "after",
}


def load_community_aliases() -> dict[str, str]:
    with ALIAS_PATH.open("r", encoding="utf-8") as handle:
        return {str(key).upper(): str(value) for key, value in json.load(handle).items()}


def valid_alias_text(limit: int = 12) -> str:
    aliases = sorted(load_community_aliases())
    suffix = " ..." if len(aliases) > limit else ""
    return ", ".join(aliases[:limit]) + suffix


def resolve_community_token(raw: str) -> tuple[str, str, str]:
    text = raw.strip()
    if not text:
        return "", "", ""
    aliases = load_community_aliases()
    lowered = re.sub(r"\s+", " ", text).lower()
    for code, community in sorted(aliases.items(), key=lambda item: len(item[1]), reverse=True):
        name = community.lower()
        if lowered == name or lowered.startswith(f"{name} "):
            return community, code, text[len(community) :].strip()
    token, _, remainder = text.partition(" ")
    community = aliases.get(token.upper(), "")
    if not community:
        return "", token, remainder.strip()
    return community, token.upper(), remainder.strip()


def normalize_post_order_type(value: str) -> str:
    normalized = re.sub(r"\s+", "", value.upper()).replace("AND", "&")
    if "K" in normalized and "C" in normalized:
        return "KC"
    if "K" in normalized:
        return "K"
    if "C" in normalized:
        return "C"
    return normalized


def post_order_output_type(value: str) -> str:
    return "K&C" if value == "KC" else value


def parse_post_orders(community: str, code: str, text: str) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    matches = list(DATE_PATTERN.finditer(text))
    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        raw_date = match.group(0)
        segment = text[match.end() : next_start].strip()
        label = POST_ORDER_LABEL_PATTERN.search(segment)
        if not label:
            continue
        normalized_type = normalize_post_order_type(label.group(1))
        rule_text = label.group(2).strip()
        if not rule_text:
            continue
        hash_input = f"{community.lower()}|{normalized_type}|{rule_text}"
        rules.append(
            {
                "date": raw_date,
                "type": normalized_type,
                "rule_text": rule_text,
                "rule_hash": sha256(hash_input.encode("utf-8")).hexdigest(),
            }
        )
    return rules


def _topic_key_from_text(text: str) -> str:
    """Compute topic_key from normalized rule text - same logic as refresh_post_orders.py."""
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    words = [w for w in re.findall(r"[a-z0-9]+", normalized) if w not in TOPIC_STOPWORDS]
    slug = "-".join(words[:6])
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return (slug[:48].strip("-") or "rule")


def _token_similarity(a: str, b: str) -> float:
    """Jaccard similarity over hyphen-split tokens."""
    left = {t for t in a.split("-") if t}
    right = {t for t in b.split("-") if t}
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _anchor_conflict(existing_topic_key: str, incoming_rule_text: str) -> bool:
    """
    Check if the incoming rule text matches the existing topic key by anchor tokens.
    Extracts meaningful tokens from the existing topic_key and checks whether they
    appear in the incoming rule text.
    """
    tokens = {
        t for t in existing_topic_key.split("-")
        if t and len(t) > 2 and t not in ANCHOR_STOPWORDS
    }
    if not tokens:
        return False
    incoming_normalized = re.sub(r"[^a-z0-9]+", " ", incoming_rule_text.lower())
    incoming_words = set(incoming_normalized.split())
    matches = tokens & incoming_words
    if len(tokens) == 1:
        token = next(iter(tokens))
        return token in incoming_words and len(token) > 5
    ratio = len(matches) / len(tokens)
    return ratio >= 0.5 and len(matches) >= 1


def scan_topic_conflicts(community: str, rules: list[dict[str, str]]) -> list[dict]:
    """
    Scan existing active vault post_order files for the community.
    Return one conflict dict per incoming rule that has a near-topic match.
    Exact hash duplicates are excluded because ingestion handles them as duplicates.
    """
    conflicts: list[dict] = []
    if not VAULT_POST_ORDER_DIR.exists():
        return conflicts

    existing: list[dict] = []
    community_slug = re.sub(r"[^a-z0-9]+", "-", community.lower()).strip("-")
    for path in sorted(VAULT_POST_ORDER_DIR.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", raw.lstrip("\ufeff"))
        if not match:
            continue
        try:
            fm = yaml.safe_load(match.group(1)) or {}
        except Exception:
            continue
        if not isinstance(fm, dict):
            continue
        if str(fm.get("type", "")) != "post_order":
            continue
        if str(fm.get("status", "")) != "active":
            continue
        fm_community = re.sub(r"[^a-z0-9]+", "-", str(fm.get("community", "")).lower()).strip("-")
        if fm_community != community_slug:
            continue
        rule_hash = str(fm.get("rule_hash", ""))
        topic_key = str(fm.get("topic_key", ""))
        normalized_rule = str(fm.get("normalized_rule", "")).strip()
        if not rule_hash or not topic_key:
            continue
        existing.append(
            {
                "rule_hash": rule_hash,
                "topic_key": topic_key,
                "normalized_rule": normalized_rule,
                "source_file": path.name,
            }
        )

    for idx, rule in enumerate(rules):
        incoming_hash = rule.get("rule_hash", "")
        best_match: dict | None = None
        best_score = 0.0
        for ex in existing:
            if ex["rule_hash"] == incoming_hash:
                best_match = None
                best_score = 0.0
                break
            if _anchor_conflict(ex["topic_key"], rule.get("rule_text", "")):
                best_match = ex
                best_score = 1.0
                break
        if best_match:
            existing_text = best_match["normalized_rule"] or "(rule text unavailable)"
            conflicts.append(
                {
                    "incoming_index": idx,
                    "incoming_type": rule.get("type", ""),
                    "incoming_text": rule.get("rule_text", ""),
                    "existing_topic_key": best_match["topic_key"],
                    "existing_rule_text": existing_text[:120],
                    "existing_source_file": best_match["source_file"],
                    "similarity": round(best_score, 2),
                }
            )
    return conflicts


def infer_category(text: str) -> str:
    normalized = text.lower()
    for category, terms in CATEGORY_KEYWORDS:
        if any(term in normalized for term in terms):
            return category
    return "general_reminder"


def split_announcement_blocks(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    if "\n\n" in stripped:
        return [block.strip() for block in re.split(r"\n\s*\n", stripped) if block.strip()]
    if NUMBERED_ITEM_PATTERN.search(stripped):
        parts = NUMBERED_ITEM_PATTERN.split("\n" + stripped)
        return [part.strip() for part in parts if part.strip()]
    return [stripped]


def parse_announcements(community: str, code: str, text: str) -> list[dict[str, str]]:
    announcements: list[dict[str, str]] = []
    for block in split_announcement_blocks(text):
        clean = re.sub(r"\s+", " ", block).strip()
        if not clean:
            continue
        announcements.append(
            {
                "category": infer_category(clean),
                "text": clean,
            }
        )
    return announcements


def write_temp_post_order_batch(community: str, code: str, rules: list[dict[str, str]], batch_date: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_path = INGESTION_DIR / f"temp_{code}_{timestamp}.md"
    lines = [
        "# Post Order Batch",
        "",
        f"community: {community}",
        f"community_code: {code}",
        f"batch_date: {batch_date}",
        "update_type: partial",
        "supersede_mode: conservative",
        "",
    ]
    for rule in rules:
        frontmatter_dict = {
            "type": "post_order",
            "authority_level": "post_order",
            "community": community,
            "community_code": code,
            "scope_key": rule["type"].lower(),
            "status": "active",
            "batch_date": batch_date,
            "effective_date": batch_date,
            "rule_hash": rule.get("rule_hash", ""),
        }
        warnings = validate_frontmatter(frontmatter_dict)
        if warnings:
            print(f"[SCHEMA WARNING] {warnings}", file=sys.stderr)
        lines.extend(
            [
                rule["date"],
                f"Post Order ({post_order_output_type(rule['type'])}): {rule['rule_text']}",
                "",
            ]
        )
    temp_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return temp_path


def write_temp_announcement_batch(community: str, code: str, announcements: list[dict[str, str]]) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_path = INGESTION_DIR / f"temp_{code}_ann_{timestamp}.md"
    today = date.today().isoformat()
    lines = [
        "# Announcement Batch",
        "",
        f"batch_date: {today}",
        f"source_name: Open WebUI Slash Command - {community} ({code})",
        "update_type: partial",
        "default_status: active",
        "",
        today,
        "",
        "IMPORTANT REMINDERS:",
    ]
    for item in announcements:
        frontmatter_dict = {
            "type": "announcement",
            "authority_level": "announcement",
            "community": community,
            "community_code": code,
            "status": "active",
            "category": item.get("category", ""),
            "batch_date": today,
            "effective_date": today,
        }
        warnings = validate_frontmatter(frontmatter_dict)
        if warnings:
            print(f"[SCHEMA WARNING] {warnings}", file=sys.stderr)
        lines.append(f"- {code} {item['text']}")
    temp_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return temp_path


def clear_pending(delete_temp: bool = False) -> None:
    state = pending_state.pop(PENDING_KEY, None)
    if not delete_temp or not state:
        return
    temp_file = Path(str(state.get("temp_file", "")))
    try:
        resolved = temp_file.resolve()
        if resolved.parent == INGESTION_DIR and resolved.name.startswith("temp_"):
            resolved.unlink(missing_ok=True)
    except OSError:
        pass


def handle_wizard_start() -> str:
    """Operator typed /post-orders with no payload. Start the wizard."""
    clear_pending(delete_temp=True)
    pending_state[WIZARD_KEY] = {
        "step": "awaiting_community",
        "expires_at": datetime.now() + timedelta(minutes=PENDING_TTL_MINUTES),
    }
    return (
        "Which community? Reply with your community alias.\n"
        "Examples: SR, CBK, MON, GWT, PBM\n\n"
        "Or cancel anytime by typing CANCEL."
    )


def has_pending_wizard() -> bool:
    return WIZARD_KEY in pending_state


def get_wizard_step() -> str:
    state = pending_state.get(WIZARD_KEY, {})
    return str(state.get("step", ""))


def clear_wizard() -> None:
    pending_state.pop(WIZARD_KEY, None)


def has_pending_ingest() -> bool:
    return PENDING_KEY in pending_state


def set_pending(kind: str, community: str, code: str, temp_file: Path, preview: str) -> None:
    pending_state[PENDING_KEY] = {
        "pending_type": kind,
        "community": community,
        "community_code": code,
        "temp_file": str(temp_file.resolve()),
        "preview": preview,
        "expires_at": datetime.now() + timedelta(minutes=PENDING_TTL_MINUTES),
    }


def _build_post_order_preview(community: str, code: str, raw_text: str) -> str:
    """
    Parse rules from raw_text, run conflict scan, and return preview string.
    Sets pending state as post_order or post_order_conflict.
    """
    rules = parse_post_orders(community, code, raw_text)
    if not rules:
        return (
            f"No post order rules were parsed for {community} ({code}).\n"
            "Use dated entries such as: 5/17/2026 Post Order (K): Rule text."
        )

    conflicts = scan_topic_conflicts(community, rules)
    if conflicts:
        lines = [
            f"Conflict detected for {community} ({code}) - "
            f"{len(conflicts)} rule(s) overlap with existing active rules:",
            "",
        ]
        for c in conflicts:
            lines.extend(
                [
                    f"Rule {c['incoming_index'] + 1}: [{c['incoming_type']}] {c['incoming_text']}",
                    "",
                    "  Conflicts with existing active rule:",
                    f"  File: {c['existing_source_file']}",
                    f"  Rule: {c['existing_rule_text']}",
                    f"  Topic similarity: {c['similarity']}",
                    "",
                ]
            )
        lines.extend(
            [
                "How would you like to proceed?",
                "Reply KEEP NEW to write the new rule(s) and supersede the conflicting existing rules.",
                "Reply KEEP OLD to cancel and keep the existing rules unchanged.",
            ]
        )
        preview = "\n".join(lines)
        pending_state[PENDING_KEY] = {
            "pending_type": "post_order_conflict",
            "community": community,
            "community_code": code,
            "pending_rules": rules,
            "raw_text": raw_text,
            "preview": preview,
            "expires_at": datetime.now() + timedelta(minutes=PENDING_TTL_MINUTES),
        }
        return preview

    batch_date = date.today().isoformat()
    temp_file = write_temp_post_order_batch(community, code, rules, batch_date)
    lines = [f"Post order preview for {community} ({code}) - {len(rules)} rule(s) parsed:", ""]
    for index, rule in enumerate(rules, start=1):
        lines.append(f"{index}. [{rule['type']}] {rule['rule_text']}")
    lines.extend(["", "Confirm ingestion? Reply YES to write to vault or NO to cancel."])
    preview = "\n".join(lines)
    set_pending("post_order", community, code, temp_file, preview)
    return preview


def handle_wizard_community(reply: str) -> str:
    """Operator replied with a community alias during wizard step 1."""
    state = pending_state.get(WIZARD_KEY)
    if not state:
        return "No active wizard session. Type /post-orders to start."
    if datetime.now() > state["expires_at"]:
        clear_wizard()
        return "Wizard session expired. Type /post-orders to start again."
    if reply.strip().upper() in {"NO", "CANCEL"}:
        clear_wizard()
        return "Ingestion cancelled. Nothing was written to vault."
    community, code, _ = resolve_community_token(reply.strip())
    if not community:
        return (
            f'Community "{reply.strip().upper()}" not recognized.\n'
            f"Valid aliases include: {valid_alias_text()}\n"
            "Reply with a valid alias or CANCEL to cancel."
        )
    pending_state[WIZARD_KEY] = {
        "step": "awaiting_text",
        "community": community,
        "community_code": code,
        "expires_at": datetime.now() + timedelta(minutes=PENDING_TTL_MINUTES),
    }
    return (
        f"Community: {community} ({code})\n\n"
        f"Paste the post order text for {community}.\n"
        "Use dated entries, e.g.:\n"
        "5/18/2026 Post Order (K): Residents must present a valid physical ID.\n\n"
        "Or type CANCEL to cancel."
    )


def handle_wizard_text(reply: str) -> str:
    """Operator pasted post order text during wizard step 2."""
    state = pending_state.get(WIZARD_KEY)
    if not state:
        return "No active wizard session. Type /post-orders to start."
    if datetime.now() > state["expires_at"]:
        clear_wizard()
        return "Wizard session expired. Type /post-orders to start again."
    if reply.strip().upper() in {"NO", "CANCEL"}:
        clear_wizard()
        return "Ingestion cancelled. Nothing was written to vault."
    community = str(state.get("community", ""))
    code = str(state.get("community_code", ""))
    clear_wizard()
    return _build_post_order_preview(community, code, reply.strip())


def handle_post_orders_command(question: str) -> str:
    clear_pending(delete_temp=True)
    clear_wizard()
    payload = question.strip()[len("/post-orders") :].strip()
    if not payload:
        return handle_wizard_start()
    community, code, raw_text = resolve_community_token(payload)
    if not community:
        return (
            f'Community "{code.upper()}" not recognized.\n'
            f"Valid aliases include: {valid_alias_text()}\n"
            "Use the alias from rag/config/community_aliases.json."
        )
    if not raw_text:
        return (
            "Usage: /post-orders [community alias] [pasted post order text]\n\n"
            f"Community resolved as {community} ({code}), but no post order text was provided."
        )
    return _build_post_order_preview(community, code, raw_text)


def handle_keep_new() -> str:
    state = pending_state.get(PENDING_KEY)
    if not state or state.get("pending_type") != "post_order_conflict":
        return "No active conflict resolution pending."
    if datetime.now() > state["expires_at"]:
        clear_pending(delete_temp=True)
        return "Session expired. Please resubmit your /post-orders command."
    community = str(state["community"])
    code = str(state["community_code"])
    rules: list[dict[str, str]] = list(state["pending_rules"])
    clear_pending()
    batch_date = date.today().isoformat()
    temp_file = write_temp_post_order_batch(community, code, rules, batch_date)
    count = len(rules)
    confirmation = (
        f"Conflict override confirmed for {community} ({code}).\n"
        f"{count} rule(s) will supersede existing conflicting rules.\n\n"
        "Reply YES to confirm ingestion or NO to cancel."
    )
    set_pending("post_order", community, code, temp_file, confirmation)
    return confirmation


def handle_keep_old() -> str:
    clear_pending(delete_temp=True)
    clear_wizard()
    return "Ingestion cancelled. Existing rules kept unchanged."


def handle_announcements_command(question: str) -> str:
    clear_pending(delete_temp=True)
    payload = question.strip()[len("/announcements") :].strip()
    if not payload:
        return (
            "Usage: /announcements [community alias] [pasted announcement text]\n\n"
            "Example: /announcements CBK CBK Pickleball Tournament May 13. Visitors should say the event name."
        )
    community, code, raw_text = resolve_community_token(payload)
    if not community:
        return (
            f'Community "{code.upper()}" not recognized.\n'
            f"Valid aliases include: {valid_alias_text()}\n"
            "Use the alias from rag/config/community_aliases.json."
        )
    if not raw_text:
        return (
            "Usage: /announcements [community alias] [pasted announcement text]\n\n"
            f"Community resolved as {community} ({code}), but no announcement text was provided."
        )
    announcements = parse_announcements(community, code, raw_text)
    if not announcements:
        return f"No announcements were parsed for {community} ({code}). Paste announcement text after the alias."
    temp_file = write_temp_announcement_batch(community, code, announcements)
    lines = [f"Announcement preview for {community} ({code}) - {len(announcements)} announcement(s) parsed:", ""]
    for index, item in enumerate(announcements, start=1):
        lines.append(f"{index}. [{item['category']}] {item['text']}")
    lines.extend(["", "Confirm ingestion? Reply YES to write to vault or NO to cancel."])
    preview = "\n".join(lines)
    set_pending("announcement", community, code, temp_file, preview)
    return preview


def recently_modified_vault_files(kind: str, since_seconds: int = 60) -> list[str]:
    """Return vault files of the given kind modified within the last N seconds."""
    if kind == "post_order":
        vault_dir = REPO_ROOT / "vault" / "03_Post_Orders"
    elif kind == "announcement":
        vault_dir = REPO_ROOT / "vault" / "05_Announcements"
    else:
        return []
    cutoff = time.time() - since_seconds
    return [
        str(path)
        for path in sorted(vault_dir.rglob("*.md"))
        if path.stat().st_mtime >= cutoff
    ]


def run_ingestion(temp_file: Path, kind: str) -> tuple[bool, str]:
    if kind == "post_order":
        command = [sys.executable, "automation/ingestion/refresh_post_orders.py", "--input", str(temp_file)]
    elif kind == "announcement":
        command = [sys.executable, "automation/ingestion/refresh_announcements.py", "--input", str(temp_file)]
    else:
        return False, f"Unknown ingestion type: {kind}"

    ingest_result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    if ingest_result.returncode != 0:
        error = ingest_result.stderr.strip() or ingest_result.stdout.strip() or "ingestion script failed"
        return False, f"Ingestion failed. Nothing was indexed.\n\n{error}"

    new_files = recently_modified_vault_files(kind)
    if new_files:
        index_command = [
            sys.executable,
            "rag/scripts/index_vault.py",
            "--files",
            *new_files,
        ]
    else:
        index_command = [sys.executable, "rag/scripts/index_vault.py"]

    index_result = subprocess.run(
        index_command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if index_result.returncode != 0:
        error = index_result.stderr.strip() or index_result.stdout.strip() or "index rebuild failed"
        return False, (
            "Ingestion wrote to vault, but ChromaDB rebuild failed.\n"
            "Manually run: python rag/scripts/index_vault.py\n\n"
            f"{error}"
        )

    try:
        temp_file.unlink()
    except OSError as error:
        return True, f"ChromaDB rebuilt. Temp file cleanup warning: {error}"
    return True, "ChromaDB rebuilt."


def handle_confirm_yes() -> str:
    state = pending_state.get(PENDING_KEY)
    if not state:
        return "There is nothing pending to confirm."
    if datetime.now() > state["expires_at"]:
        clear_pending(delete_temp=True)
        return "Session expired. Please resubmit your /post-orders or /announcements command."
    if state.get("pending_type") == "post_order_conflict":
        return "Conflict resolution pending. Reply KEEP NEW or KEEP OLD."

    clear_pending()
    temp_file = Path(str(state["temp_file"]))
    success, message = run_ingestion(temp_file, str(state["pending_type"]))
    if not success:
        return message

    label = "rule(s)" if state["pending_type"] == "post_order" else "announcement(s)"
    count = max(0, len([line for line in str(state["preview"]).splitlines() if re.match(r"^\d+\.", line)]))
    kind_name = "post orders" if state["pending_type"] == "post_order" else "announcements"
    return (
        f"Ingestion complete for {state['community']} ({state['community_code']}).\n"
        f"{count} {label} written to vault.\n"
        f"{message} System is live with updated {kind_name}."
    )


def handle_confirm_no() -> str:
    clear_pending(delete_temp=True)
    clear_wizard()
    return "Ingestion cancelled. Nothing was written to vault."


def handle_unrecognized_confirmation() -> str:
    clear_pending(delete_temp=True)
    clear_wizard()
    return "Ingestion cancelled. Nothing was written to vault."
