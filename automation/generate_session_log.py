from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE_LOG_PATH = REPO_ROOT / "docs" / "PHASE_LOG.md"


def normalize_version(value: str) -> str:
    return str(value or "").strip()


def parse_phase_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            if current:
                entries.append(current)
            current = {"heading": heading.group(1).strip(), "version": ""}
            continue

        if current:
            version = re.match(r"^Version:\s*(.+?)\s*$", line)
            if version:
                current["version"] = normalize_version(version.group(1))

    if current:
        entries.append(current)

    return [entry for entry in entries if entry.get("version")]


def phases_between(entries: list[dict[str, str]], version_start: str, version_end: str) -> list[dict[str, str]]:
    start = normalize_version(version_start)
    end = normalize_version(version_end)
    start_index = next((i for i, entry in enumerate(entries) if entry["version"] == start), None)
    end_index = next((i for i, entry in enumerate(entries) if entry["version"] == end), None)

    if end_index is None:
        return []

    if start_index is None:
        selected = entries[: end_index + 1] if end_index >= 0 else []
    elif end_index < start_index:
        selected = entries[end_index:start_index]
    else:
        selected = entries[start_index + 1 : end_index + 1]

    return list(reversed(selected))


def yaml_list(values: list[str]) -> list[str]:
    if not values:
        return ["  - TODO"]
    return [f"  - {value}" for value in values]


def render_log(session_date: str, session: str, version_start: str, version_end: str, phases: list[dict[str, str]]) -> str:
    phase_versions = [phase["version"] for phase in phases]
    phase_sections: list[str] = []
    for phase in phases:
        phase_sections.extend(
            [
                f"### {phase['heading']}",
                "",
                "TODO: fill in details",
                "",
            ]
        )

    return "\n".join(
        [
            "---",
            f"date: {session_date}",
            f"session: {session}",
            f"version_start: {version_start}",
            f"version_end: {version_end}",
            "phases_completed:",
            *yaml_list(phase_versions),
            "---",
            "",
            f"# Session Log - {session_date}",
            "",
            "## Session Summary",
            "",
            "TODO: fill in summary",
            "",
            "## Phases and Patches Completed",
            "",
            *(phase_sections or ["TODO: fill in details", ""]),
            "## Key Decisions Made",
            "",
            "TODO: fill in decisions",
            "",
            "## Tracked Observations Pending Resolution",
            "",
            "TODO: fill in observations",
            "",
            "## Next Session Start",
            "",
            f"Current stable: {version_end}",
            "Next phase: TODO - fill in from FUTURE_PLANS.md",
            "",
        ]
    )


def default_output(session_date: str, session: str) -> Path:
    return REPO_ROOT / "docs" / "SESSION_LOG" / f"{session_date}-session-{session}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a draft SafePassage SESSION_LOG file.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Session date as YYYY-MM-DD.")
    parser.add_argument("--session", default="01", help="Session number, default: 01.")
    parser.add_argument("--version-start", required=True, help="Starting version, e.g. 4.19.0-stable.")
    parser.add_argument("--version-end", required=True, help="Ending version, e.g. 4.20.0-stable.")
    parser.add_argument("--output", default="", help="Output path. Defaults to docs/SESSION_LOG/{date}-session-{session}.md.")
    args = parser.parse_args()

    try:
        phase_log = PHASE_LOG_PATH.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Error: could not read {PHASE_LOG_PATH}: {error}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else default_output(args.date, args.session)
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    if output_path.exists():
        print(f"Warning: output file already exists, not overwriting: {output_path}")
        return 0

    phases = phases_between(parse_phase_entries(phase_log), args.version_start, args.version_end)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_log(args.date, args.session, args.version_start, args.version_end, phases),
        encoding="utf-8",
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
