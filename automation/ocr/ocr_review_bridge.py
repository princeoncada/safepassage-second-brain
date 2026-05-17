from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = REPO_ROOT / "automation" / "ingestion" / "reviewed_ocr_inputs"
DEFAULT_OUTPUTS = {
    "announcement": STAGING_DIR / "reviewed_ocr_announcements.md",
    "post_order": STAGING_DIR / "reviewed_ocr_post_orders.md",
}

ALLOWED_REVIEW_STATUSES = {"pending_review", "approved", "rejected"}
ALLOWED_TARGET_TYPES = {"announcement", "post_order", "none"}
TRUE_VALUES = {"true", "yes", "1"}
FALSE_VALUES = {"false", "no", "0", ""}


def parse_metadata(markdown: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## "):
            break
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", stripped)
        if match:
            metadata[match.group(1).lower()] = match.group(2).strip()
    return metadata


def parse_bool(value: str) -> bool | None:
    normalized = str(value or "").strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return None


def extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    return match.group(1) if match else ""


def reviewed_text_from(markdown: str) -> str:
    text = extract_section(markdown, "Extracted Text")
    if text.strip() == "[no text extracted]":
        return ""
    return text


def require_approved(metadata: dict[str, str]) -> str:
    review_status = metadata.get("review_status", "").strip().lower()
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise SystemExit(
            "Refusing OCR bridge: review_status must be one of "
            "pending_review, approved, or rejected."
        )
    if review_status != "approved":
        raise SystemExit("Refusing OCR bridge: review_status must be approved.")

    approved = parse_bool(metadata.get("approved_for_ingestion", "false"))
    if approved is not True:
        raise SystemExit("Refusing OCR bridge: approved_for_ingestion must be true.")

    target_type = metadata.get("target_ingestion_type", "none").strip().lower()
    if target_type not in ALLOWED_TARGET_TYPES:
        raise SystemExit(
            "Refusing OCR bridge: target_ingestion_type must be announcement, post_order, or none."
        )
    if target_type not in {"announcement", "post_order"}:
        raise SystemExit("Refusing OCR bridge: target_ingestion_type must be announcement or post_order.")
    return target_type


def bridge_block(source_path: Path, reviewed_text: str) -> str:
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return "\n".join(
        [
            "",
            "---",
            f"source_review_file: {source_path.name}",
            f"bridged_at: {created_at}",
            "---",
            "",
            reviewed_text,
            "",
        ]
    )


def write_output(output_path: Path, content: str, mode: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "write":
        output_path.write_text(content.lstrip(), encoding="utf-8")
        return
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(content)


def require_staging_output(output_path: Path) -> Path:
    resolved_output = output_path.resolve()
    resolved_staging = STAGING_DIR.resolve()
    if resolved_output != resolved_staging and resolved_staging not in resolved_output.parents:
        raise SystemExit(
            "Refusing OCR bridge: output must stay under automation/ingestion/reviewed_ocr_inputs/."
        )
    return resolved_output


def bridge_review(input_path: Path, mode: str, output_path: Path | None = None) -> Path:
    if not input_path.exists() or not input_path.is_file():
        raise SystemExit(f"Refusing OCR bridge: input review file does not exist: {input_path}")

    markdown = input_path.read_text(encoding="utf-8")
    metadata = parse_metadata(markdown)
    target_type = require_approved(metadata)
    reviewed_text = reviewed_text_from(markdown)
    if not reviewed_text.strip():
        raise SystemExit("Refusing OCR bridge: reviewed text under ## Extracted Text is missing.")

    destination = require_staging_output(output_path or DEFAULT_OUTPUTS[target_type])
    write_output(destination, bridge_block(input_path, reviewed_text), mode)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bridge a human-approved OCR review Markdown file into reviewed OCR ingestion staging input."
    )
    parser.add_argument("--input", required=True, type=Path, help="Reviewed OCR Markdown file.")
    parser.add_argument("--mode", choices=["append", "write"], default="append", help="Write mode for staging output.")
    parser.add_argument("--output", type=Path, help="Optional custom staging output path.")
    args = parser.parse_args()

    output_path = bridge_review(args.input, args.mode, args.output)
    print(f"Reviewed OCR text staged at: {output_path}")
    print("This only writes a staging input. It does not write to vault, run ingestion, or update ChromaDB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
