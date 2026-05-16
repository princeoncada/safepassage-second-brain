# OCR Workflow

## Purpose

Phase 4E adds a local OCR intake layer for screenshots and images. OCR is only used to convert images into reviewable text artifacts.

OCR does not write to the operational vault.

## Architecture

```text
image
-> local OCR extraction
-> raw text artifact
-> review Markdown artifact
-> human review/edit
-> existing ingestion script
-> vault Markdown
-> ChromaDB reindex
```

Markdown in `vault/` remains the source of truth. OCR output is temporary intake material until a human reviews it and passes corrected text into the appropriate ingestion workflow.

## Supported Inputs

The OCR script accepts:

- `png`
- `jpg`
- `jpeg`
- `webp`

It supports one image or a folder of images.

## Engines

Preferred engine:

- PaddleOCR

Fallback engine:

- pytesseract

Both options are local/offline capable. The OCR layer does not use cloud OCR, OpenAI OCR, or external APIs.

## Output Artifacts

OCR output is written to:

```text
automation/ocr/output/
```

For each image, the script writes:

- `<image>_ocr_raw.txt`
- `<image>_ocr_review.md`

The review file includes:

- source image name
- created timestamp
- OCR engine
- confidence when available
- extracted text
- review notes
- raw OCR text

## Human Review Requirement

Every OCR result must be reviewed before ingestion.

Reviewers must verify:

- community abbreviations such as `CBK`, `PBP`, `SR`, `SSR`, and `OPB`
- dates and expiration dates
- emergency codes
- gate names and issue descriptions
- event dates and times
- whether the text belongs in announcements, post orders, or another intake path

OCR cleanup intentionally does not expand community aliases. Alias expansion belongs to ingestion and retrieval layers.

## Safety Boundaries

The OCR layer must never:

- write directly into `vault/`
- call `refresh_announcements.py`
- call `refresh_post_orders.py`
- classify lifecycle state as operational truth
- delete files
- update ChromaDB
- bypass human review

This boundary exists because OCR can misread operational text. A wrong emergency code, date, or community name can create unsafe guidance if it enters the vault unchecked.

## Using OCR Output

After review, copy corrected text into the appropriate input file:

- announcements and reminders: `automation/ingestion/sample_announcement_batch.md` or a new reviewed announcement batch file
- post orders: `automation/ingestion/sample_post_order_batch.md` or a new reviewed post-order batch file

Then run the existing deterministic ingestion script for that document type and rebuild ChromaDB from Markdown.

## Known Limitations

- OCR accuracy depends on screenshot quality.
- Table-like layouts may lose structure.
- Bullets and indentation may need manual cleanup.
- PaddleOCR and pytesseract return confidence differently.
- Tesseract requires a local binary in addition to the Python package.
- OCR output is not operational memory until reviewed and ingested.
