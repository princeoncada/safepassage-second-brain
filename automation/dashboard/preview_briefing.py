from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rag.dashboard import dashboard_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview the read-only operational shift briefing from indexed memory.")
    parser.add_argument("--community", default="", help="Optional community name or alias, such as CBK or Sierra Ridge.")
    parser.add_argument("--expiring-soon-days", type=int, default=7, help="Days ahead for expiring-soon notices.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum indexed items to consider.")
    args = parser.parse_args()

    try:
        payload = dashboard_payload(args.community, args.expiring_soon_days, args.limit)
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    print(payload["briefing_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
