from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def normalize_ocr_lines(text: str) -> str:
    """Conservative OCR cleanup that preserves wording and community aliases."""
    lines: list[str] = []
    previous_blank = False
    for raw_line in str(text or "").splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        lines.append(line)
        previous_blank = False
    return "\n".join(lines).strip()


def confidence_label(confidence: float | None) -> str:
    if confidence is None:
        return "not reported"
    return f"{confidence:.2f}"


def confidence_warning(confidence: float | None) -> str:
    if confidence is None:
        return "- OCR confidence was not reported by the selected engine."
    if confidence < 0.75:
        return "- OCR confidence is low. Manual review is strongly recommended."
    if confidence < 0.9:
        return "- OCR confidence is moderate. Manual review is required before ingestion."
    return "- OCR confidence is high, but manual review is still required before ingestion."


def extraction_warning(cleaned_text: str) -> str:
    if cleaned_text.strip():
        return "- Extracted text is present, but still requires human review."
    return "- No OCR text was extracted. Check image quality, crop, orientation, or OCR engine setup."


def build_review_markdown(
    *,
    source_image: Path,
    raw_text: str,
    cleaned_text: str,
    ocr_engine: str,
    average_confidence: float | None,
) -> str:
    created_at = datetime.now().isoformat(timespec="seconds")
    return "\n".join(
        [
            "# OCR Review",
            f"source_image: {source_image.name}",
            f"created_at: {created_at}",
            f"ocr_engine: {ocr_engine}",
            f"ocr_confidence: {confidence_label(average_confidence)}",
            "review_status: pending_review",
            "approved_for_ingestion: false",
            "target_ingestion_type: none",
            "reviewed_by:",
            "reviewed_at:",
            "review_notes:",
            "",
            "## Extracted Text",
            "",
            cleaned_text or "[no text extracted]",
            "",
            "## Review Notes",
            "",
            "- OCR may contain formatting issues.",
            "- Verify community aliases exactly as shown, such as CBK, PBP, SR, SSR, and OPB.",
            "- Verify dates, times, emergency codes, and gate names manually.",
            "- Do not ingest this text until a human has reviewed and corrected it.",
            "- OCR output must be copied into the appropriate ingestion input only after review.",
            extraction_warning(cleaned_text),
            confidence_warning(average_confidence),
            "",
            "## Raw OCR Text",
            "",
            "```text",
            raw_text.strip() or "[no text extracted]",
            "```",
            "",
        ]
    )
