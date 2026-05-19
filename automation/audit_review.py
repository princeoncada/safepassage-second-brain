"""Audit log review tool for operational trust and compliance.

Usage examples:
  python automation/audit_review.py
  python automation/audit_review.py --tail 50
  python automation/audit_review.py --community "Sierra Ridge"
  python automation/audit_review.py --date 2026-05-19
  python automation/audit_review.py --confidence weak
  python automation/audit_review.py --warnings
  python automation/audit_review.py --community "Sierra Ridge" --date 2026-05-19
  python automation/audit_review.py --entry 42
  python automation/audit_review.py --community "Sierra Ridge" --full
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

AUDIT_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "query_audit.jsonl"
DEFAULT_TAIL = 20


def load_entries() -> list[dict]:
    if not AUDIT_LOG_PATH.exists():
        return []
    entries = []
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def print_entry_summary(index: int, entry: dict, full: bool = False) -> None:
    ts = entry.get("timestamp", "")[:19].replace("T", " ")
    community = entry.get("community_resolved", "(none)") or "(none)"
    intent = entry.get("intent_category", "") or ""
    confidence = entry.get("confidence", "") or entry.get("retrieval_confidence", "")
    warnings = entry.get("warnings", [])
    query = entry.get("query", "")
    sources = entry.get("sources_cited", [])
    used_ai = entry.get("used_ai", False)
    vault_ver = entry.get("vault_version", "")

    warn_flag = " ⚠" if warnings else ""
    ai_flag = "[AI]" if used_ai else "[no-AI]"

    print(f"\n[{index}] {ts}  {ai_flag}  confidence={confidence}{warn_flag}")
    print(f"     Community : {community}")
    print(f"     Intent    : {intent}")
    print(f"     Query     : {query}")
    print(f"     Sources   : {len(sources)} cited")
    print(f"     Vault ver : {vault_ver}")

    if warnings:
        for w in warnings:
            print(f"     ⚠ Warning : {w}")

    if full:
        print(f"\n     --- Answer ---")
        print(entry.get("answer", ""))
        print(f"     --- Sources cited ---")
        for s in sources:
            print(f"       {s}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review the SafePassage query/answer audit log."
    )
    parser.add_argument("--tail", type=int, default=DEFAULT_TAIL,
                        help=f"Show last N entries (default: {DEFAULT_TAIL})")
    parser.add_argument("--community", type=str, default=None,
                        help="Filter by community name (case-insensitive substring)")
    parser.add_argument("--date", type=str, default=None,
                        help="Filter by date prefix e.g. 2026-05-19")
    parser.add_argument("--confidence", type=str, default=None,
                        choices=["strong", "moderate", "weak", "none"],
                        help="Filter by retrieval confidence level")
    parser.add_argument("--warnings", action="store_true",
                        help="Show only entries that have warnings")
    parser.add_argument("--entry", type=int, default=None,
                        help="Show full details for entry number N")
    parser.add_argument("--full", action="store_true",
                        help="Show full answer text and all source paths for all matching entries")
    args = parser.parse_args()

    entries = load_entries()

    if not entries:
        print("No audit log entries found. Log file may be empty or not yet created.")
        print(f"Expected path: {AUDIT_LOG_PATH}")
        return

    # --entry: show one specific entry by index
    if args.entry is not None:
        if args.entry < 0 or args.entry >= len(entries):
            print(f"Entry {args.entry} out of range (0–{len(entries) - 1})")
            return
        print_entry_summary(args.entry, entries[args.entry], full=True)
        return

    # Apply filters
    filtered = list(enumerate(entries))

    if args.date:
        filtered = [(i, e) for i, e in filtered
                    if e.get("timestamp", "").startswith(args.date)]

    if args.community:
        term = args.community.lower()
        filtered = [(i, e) for i, e in filtered
                    if term in (e.get("community_resolved", "") or "").lower()]

    if args.confidence:
        filtered = [(i, e) for i, e in filtered
                    if e.get("retrieval_confidence", "") == args.confidence]

    if args.warnings:
        filtered = [(i, e) for i, e in filtered if e.get("warnings")]

    # Apply tail
    filtered = filtered[-args.tail:]

    if not filtered:
        print("No entries match the given filters.")
        return

    print(f"\nShowing {len(filtered)} entr{'y' if len(filtered) == 1 else 'ies'} "
          f"(total in log: {len(entries)})")

    for i, entry in filtered:
        print_entry_summary(i, entry, full=args.full)

    print()


if __name__ == "__main__":
    main()
