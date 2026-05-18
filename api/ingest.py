from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INGESTION_DIR = REPO_ROOT / "automation" / "ingestion"
ALIAS_PATH = REPO_ROOT / "rag" / "config" / "community_aliases.json"
PENDING_KEY = "pending_ingest"
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


def handle_post_orders_command(question: str) -> str:
    clear_pending(delete_temp=True)
    payload = question.strip()[len("/post-orders") :].strip()
    if not payload:
        return (
            "Usage: /post-orders [community alias] [pasted post order text]\n\n"
            "Example: /post-orders CBK 5/17/2026 Post Order (K): Only contact the resident twice."
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
            "Usage: /post-orders [community alias] [pasted post order text]\n\n"
            f"Community resolved as {community} ({code}), but no post order text was provided."
        )
    rules = parse_post_orders(community, code, raw_text)
    if not rules:
        return (
            f"No post order rules were parsed for {community} ({code}).\n"
            "Use dated entries such as: 5/17/2026 Post Order (K): Rule text."
        )
    batch_date = date.today().isoformat()
    temp_file = write_temp_post_order_batch(community, code, rules, batch_date)
    lines = [f"Post order preview for {community} ({code}) - {len(rules)} rule(s) parsed:", ""]
    for index, rule in enumerate(rules, start=1):
        lines.append(f"{index}. [{rule['type']}] {rule['rule_text']}")
    lines.extend(["", "Confirm ingestion? Reply YES to write to vault or NO to cancel."])
    preview = "\n".join(lines)
    set_pending("post_order", community, code, temp_file, preview)
    return preview


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
    return "Ingestion cancelled. Nothing was written to vault."


def handle_unrecognized_confirmation() -> str:
    clear_pending(delete_temp=True)
    return "Ingestion cancelled. Nothing was written to vault."
