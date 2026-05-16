from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "automation" / "ingestion" / "sample_primary_workflow_input.md"
OUTPUT_DIR = REPO_ROOT / "vault" / "09_SOPs"
SOURCE_DOCUMENT = "NEW SAFEPASSAGE KIOSK TRAINING SCRIPT.pdf"
AUTHORITY_NOTE = (
    "Primary workflow is default guidance. Community post orders and announcements override this when applicable."
)


TITLE_OVERRIDES = {
    "primary-kiosk-basics": "Primary Kiosk Basics",
    "primary-call-attempts-by-community": "Primary Call Attempts By Community",
    "primary-saving-tags-procedure": "Primary Saving Tags Procedure",
    "primary-before-shift-screenshots": "Primary Before Shift Screenshots",
    "primary-community-client-codes": "Primary Community Client Codes",
    "primary-kiosk-call-flow": "Primary Kiosk Call Flow",
    "primary-calling-resident-for-access": "Primary Calling Resident For Access",
    "primary-leaving-voicemail": "Primary Leaving Voicemail",
    "primary-deny-entry": "Primary Deny Entry",
    "primary-no-physical-id": "Primary No Physical ID",
    "primary-incomplete-interaction": "Primary Incomplete Interaction",
    "primary-spanish-translation": "Primary Spanish Translation",
    "primary-ticket-format": "Primary Ticket Format",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "primary-workflow"


def parse_sections(markdown: str) -> list[dict[str, str]]:
    pattern = re.compile(r"^##\s+(primary-[a-z0-9-]+)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    sections: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        slug = slugify(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        raw_block = markdown[start:end].strip()
        if not raw_block:
            continue

        source_section = ""
        source_page = ""
        content_lines: list[str] = []
        for line in raw_block.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("source section:"):
                source_section = stripped.split(":", 1)[1].strip()
                continue
            if stripped.lower().startswith("source page:"):
                source_page = stripped.split(":", 1)[1].strip()
                continue
            content_lines.append(line)

        content = "\n".join(content_lines).strip()
        if content.lower().startswith("content:"):
            content = content.split(":", 1)[1].strip()

        sections.append(
            {
                "slug": slug,
                "title": TITLE_OVERRIDES.get(slug, slug.replace("-", " ").title()),
                "source_section": source_section or slug.replace("-", " ").title(),
                "source_page": source_page or "unknown",
                "content": content,
            }
        )
    return sections


def build_markdown(section: dict[str, str], source: str, version: str) -> str:
    today = date.today().isoformat()
    title = section["title"]
    tags = ["primary-workflow", "kiosk", section["slug"]]
    tag_lines = "\n".join(f"  - \"{tag}\"" for tag in tags)
    return f"""---
title: "{title}"
type: "workflow"
authority_level: "primary_workflow"
community: "global"
scope:
  - "kiosk"
priority: "medium"
effective_date: "{today}"
source: "{source}"
status: "active"
tags:
{tag_lines}
last_updated: "{today}"
version: "{version}"
---

# {title}

## Summary

{section["content"]}

## Source References

- Source Document: {source}
- Source Section: {section["source_section"]}
- Source Page: {section["source_page"]}
- Authority Note: {AUTHORITY_NOTE}

## Authority Note

{AUTHORITY_NOTE}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest structured primary workflow Markdown into vault/09_SOPs.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Structured primary workflow input Markdown.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing primary workflow files.")
    parser.add_argument("--version", default="1.0", help="Version string for generated Markdown.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    sections = parse_sections(input_path.read_text(encoding="utf-8"))
    if not sections:
        raise SystemExit("No primary workflow sections found. Expected headings like: ## primary-kiosk-basics")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []
    for section in sections:
        output_path = OUTPUT_DIR / f"{section['slug']}.md"
        if output_path.exists() and not args.force:
            skipped.append(output_path)
            continue
        output_path.write_text(build_markdown(section, SOURCE_DOCUMENT, args.version), encoding="utf-8")
        created.append(output_path)

    if created:
        print("Created primary workflow files:")
        for path in created:
            print(f"- {path.relative_to(REPO_ROOT).as_posix()}")
    if skipped:
        print("Skipped existing files. Re-run with --force to overwrite:")
        for path in skipped:
            print(f"- {path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
