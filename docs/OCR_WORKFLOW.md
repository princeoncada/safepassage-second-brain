# OCR Workflow

## Purpose

Phase 4E adds a local OCR intake layer for screenshots and images. OCR is only used to convert images into reviewable text artifacts.

OCR does not write to the operational vault.

Phase 4F adds a deterministic review bridge that can stage human-approved reviewed OCR text for existing ingestion inputs. This is still not ingestion.

## Architecture

```text
image
-> local OCR extraction
-> raw text artifact
-> review Markdown artifact
-> human review/edit
-> approved review bridge
-> reviewed OCR staging input
-> user manually runs existing ingestion script
-> vault Markdown
-> user manually rebuilds ChromaDB
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

Current validated engine:

- pytesseract

Deferred experimental engine:

- PaddleOCR

pytesseract is the current validated OCR backend for this project. PaddleOCR installed partially and downloaded models, but did not pass Windows/Paddle runtime validation. Treat PaddleOCR as experimental and deferred for a future Linux, Docker, or pinned-version phase.

The OCR layer does not use cloud OCR, OpenAI OCR, or external APIs.

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
- review metadata fields
- extracted text
- review notes
- raw OCR text

## Review Queue

Reviewed OCR artifacts can be organized under:

```text
automation/ocr/review_queue/pending/
automation/ocr/review_queue/approved/
automation/ocr/review_queue/rejected/
```

New OCR review files default to pending review. Moving files between queue folders is a human workflow aid only; the bridge trusts the metadata inside the reviewed Markdown file, not the folder name.

## Review Metadata

Generated review Markdown includes these fields near the top:

```text
review_status: pending_review
approved_for_ingestion: false
target_ingestion_type: none
reviewed_by:
reviewed_at:
review_notes:
```

Allowed `review_status` values:

- `pending_review`
- `approved`
- `rejected`

Allowed `target_ingestion_type` values:

- `announcement`
- `post_order`
- `none`

For the bridge to stage reviewed text, a human reviewer must explicitly set:

```text
review_status: approved
approved_for_ingestion: true
target_ingestion_type: announcement
```

or:

```text
review_status: approved
approved_for_ingestion: true
target_ingestion_type: post_order
```

OCR cleanup does not classify the target type automatically and does not expand community aliases.

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

The OCR review bridge must also never write to `vault/`, call ingestion scripts, update ChromaDB, summarize reviewed text, rewrite reviewed text, infer missing policy, or expand aliases.

This boundary exists because OCR can misread operational text. A wrong emergency code, date, or community name can create unsafe guidance if it enters the vault unchecked.

## Using OCR Output

After review, either copy corrected text into the appropriate input file manually:

- announcements and reminders: `automation/ingestion/sample_announcement_batch.md` or a new reviewed announcement batch file
- post orders: `automation/ingestion/sample_post_order_batch.md` or a new reviewed post-order batch file

or use the Phase 4F bridge to stage approved reviewed text:

```powershell
python automation/ocr/ocr_review_bridge.py --input automation/ocr/review_queue/approved/example_ocr_review.md
```

By default, the bridge appends reviewed text to one of these staging files based on `target_ingestion_type`:

```text
automation/ingestion/reviewed_ocr_inputs/reviewed_ocr_announcements.md
automation/ingestion/reviewed_ocr_inputs/reviewed_ocr_post_orders.md
```

The bridge supports:

```powershell
python automation/ocr/ocr_review_bridge.py --input path/to/review.md --mode append
python automation/ocr/ocr_review_bridge.py --input path/to/review.md --mode write
python automation/ocr/ocr_review_bridge.py --input path/to/review.md --output automation/ingestion/reviewed_ocr_inputs/custom.md
```

The bridge refuses if:

- `review_status` is not `approved`
- `approved_for_ingestion` is not `true`
- `target_ingestion_type` is `none` or unsupported
- reviewed text under `## Extracted Text` is missing

Then the user manually runs the existing deterministic ingestion script for that document type and rebuilds ChromaDB from Markdown.

## Known Limitations

- OCR accuracy depends on screenshot quality.
- Table-like layouts may lose structure.
- Bullets and indentation may need manual cleanup.
- Tesseract requires a local binary in addition to the Python package.
- PaddleOCR is not production validated in this repo and should not be documented as the active OCR backend.
- OCR output is not operational memory until reviewed and ingested.
