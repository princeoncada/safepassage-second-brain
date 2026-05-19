"""Query/answer audit log for operational trust and compliance.

Appends one JSON Lines record per query to logs/query_audit.jsonl.
Never read by the retrieval or answer pipeline — write-only at
query time.

write_audit_entry() silently swallows all exceptions. A broken
audit log must never interrupt a VA query.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.version import VAULT_VERSION

LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"
AUDIT_LOG_PATH = LOGS_DIR / "query_audit.jsonl"


def write_audit_entry(
    *,
    query: str,
    hints: dict[str, Any],
    assessment: dict[str, Any],
    cited_chunks: list[dict[str, Any]],
    answer: str,
    used_ai: bool,
    warnings: list[str],
) -> None:
    """Append one audit record to query_audit.jsonl.

    Silently ignores all errors — audit failures must not break
    VA query responses.
    """
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "community_resolved": hints.get("community", ""),
            "community_alias": hints.get("community_alias", ""),
            "intent_category": hints.get("intent_category", ""),
            "scope": hints.get("scope", ""),
            "retrieval_confidence": assessment.get("confidence", ""),
            "confidence_reason": assessment.get("reason", ""),
            "sources_cited": list(dict.fromkeys(
                str(chunk.get("source_file", ""))
                for chunk in cited_chunks
                if chunk.get("source_file")
            )),
            "answer": answer,
            "used_ai": used_ai,
            "warnings": warnings,
            "vault_version": VAULT_VERSION,
        }
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass
