# SafePassage Second Brain

A local-first AI-powered operational knowledge system for workflows, SOPs, post orders, QA protection, incidents, scripts, automations, and searchable work intelligence.

## Source Of Truth

Markdown files in `vault/`.

## Current Status

Working proof of work through Phase 4G validation, with Phase 4G1 implementation added for manual validation:

- Phase 2 Minimal POW ingestion: passed
- Phase 3A retrieval: passed
- Phase 3B grounded answering: passed
- Phase 3C RAG quality hardening: passed
- Phase 3D local FastAPI wrapper: passed
- Phase 3E Open WebUI integration: passed
- Phase 4A retrieval quality hardening: passed with minor tuning
- Phase 4B primary workflow ingestion: passed
- Phase 4B2 primary workflow fallback confidence fix: passed
- Phase 4C batch post order refresh/diffing: passed
- Phase 4C1 lifecycle retrieval hardening: passed with known limitation
- Phase 4C2 legacy post order migration / managed source conversion: passed
- Phase 4C3 announcement / reminder lifecycle ingestion: passed with minor retrieval edge case
- Phase 4D operational query parser / intent extraction: passed
- Phase 4E OCR intake layer: passed using pytesseract fallback
- Phase 4F OCR review + ingestion bridge: passed/validated
- Phase 4G temporal expiry / activation engine: passed/validated
- Phase 4G1 announcement retrieval precision hardening: implementation added, manual validation pending

Current architecture:

```text
Open WebUI
-> FastAPI /ask
-> local retrieval
-> grounded answer generation
-> citations/refusal/confidence
```

Open WebUI is presentation-only. Markdown in `vault/` remains the source of truth.

Phase 4A keeps this architecture and improves only retrieval ranking, dedupe, source selection, and citation cleanup.

Phase 4B adds the SafePassage primary kiosk workflow as global default guidance below post orders and announcements.

Phase 4C adds deterministic batch post order refresh and diffing so incoming post-order batches can be compared against active vault rules before new Markdown is created.

Phase 4C1 hardens retrieval over lifecycle-managed post orders. Active managed post orders are the operational retrieval source of truth. Pending rules are advisory only, superseded/archived rules are penalized or skipped, and legacy freeform post-order notes are skipped by default instead of deleted.

Community aliases are resolved deterministically before retrieval. Letter prefixes such as `CBK`, `SR`, `MON`, and `OPB` map to their configured community names without using numeric client codes.

Phase 4C2 converts eligible legacy freeform post orders into managed active post-order documents while preserving the original legacy files. This is used first for Sierra Ridge physical ID post orders so policy retrieval can come from managed `post_order` sources instead of weaker QA support notes.

Phase 4C3 adds deterministic announcement and reminder ingestion from cleaned pasted text. Announcements are managed lifecycle documents under `vault/05_Announcements` and sit between post orders and primary workflow in authority: `post_order > announcement > primary_workflow`.

Phase 4D adds deterministic query intent parsing before retrieval. It extracts known community aliases, operational topics, expected document types, scope hints, and default/global intent so phrases like `Red Zone Protocol` are treated as announcement topics instead of missing communities.

Phase 4E adds a local OCR intake layer for screenshots and images. OCR creates raw and reviewable text artifacts only; it does not write to `vault/`, trigger ingestion scripts, update ChromaDB, or bypass human review.

The current validated OCR backend is `pytesseract`. PaddleOCR did not pass Windows runtime validation and is deferred as an experimental future Linux, Docker, or pinned-version candidate.

Phase 4F adds an explicit OCR review queue and a deterministic review bridge. The bridge only copies human-approved reviewed OCR text into staging files under `automation/ingestion/reviewed_ocr_inputs/`; it does not write to `vault/`, trigger ingestion scripts, or update ChromaDB.

Phase 4G adds a deterministic temporal expiry / activation engine. Vault Markdown remains the source of truth, but indexed chunks can now carry temporal lifecycle metadata such as `temporal_state`, `temporal_warning`, active/effective dates, and expiry/end dates. Retrieval still preserves the authority hierarchy `post_order > announcement > primary_workflow`, but now prefers currently active temporal sources, downgrades pending, not-yet-active, expired, superseded, archived, review, and unknown-temporal sources, and exposes warnings when context is stale or uncertain.

Temporal reports can be generated under `vault/08_Reports/temporal-lifecycle/`. These reports are review artifacts only. They do not mutate operational memory, run ingestion scripts, update ChromaDB, or bypass human review.

Phase 4G1 hardens announcement retrieval precision after the temporal engine exposed a Red Zone Protocol retrieval specificity regression. It keeps the same safety boundaries and adds deterministic section-aware reranking: exact topic/title/body matches, title overlap, category matches, and the `Announcement` section are boosted, while `Operational Notes`, `Source`, migration notes, and other metadata-heavy sections are penalized for direct operational questions. It does not lower refusal thresholds globally, use LLM reranking, rewrite vault files, or let announcements override post orders.

## OCR Intake

```powershell
python automation/ocr/ocr_extract.py --input path/to/image.png
python automation/ocr/ocr_extract.py --input-dir path/to/screenshots
```

Review the generated Markdown under `automation/ocr/output/` before copying corrected text into announcement or post-order ingestion inputs.

OCR remains intake-only. Human review is mandatory before any OCR text is used for operational ingestion.

Reviewed OCR files can be organized under:

```text
automation/ocr/review_queue/pending/
automation/ocr/review_queue/approved/
automation/ocr/review_queue/rejected/
```

After human review, approved files may be staged for deterministic ingestion input:

```powershell
python automation/ocr/ocr_review_bridge.py --input automation/ocr/review_queue/approved/example_ocr_review.md
```

The bridge writes only to reviewed OCR staging inputs. The user must still run the appropriate announcement or post-order ingestion script manually, then rebuild ChromaDB manually.

## Post Order Batch Refresh

Dry run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
```

Real run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

## Announcement Batch Refresh

```powershell
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md --dry-run
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md
```

## Local RAG API

```powershell
pip install -r rag/requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

## Version Control

GitHub is required for rollback, audit history, and future AI handoff.

## Phase Rule

Do not proceed to the next phase until the current phase passes documentation, testing, and validation.
