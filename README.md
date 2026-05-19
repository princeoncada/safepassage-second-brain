# SafePassage Second Brain

A local-first AI-powered operational knowledge system for workflows, SOPs, post orders, QA protection, incidents, scripts, automations, and searchable work intelligence.

## Version Status

| Field | Value |
| --- | --- |
| Current | 4.18.3-alpha |
| Last Stable | 4.18.2-stable (Patch) |
| Status | alpha |

## Source Of Truth

Markdown files in `vault/`.

## Current Status

Working proof of work through 4.18.2-stable prevent DeepSeek inline Sources block in answers; current patch is 4.18.3-alpha to restore clean CLI citation display:

- Phase 2 [2.0.0-stable] - Minimal POW ingestion: passed
- Phase 3A [3.0.0-stable] - retrieval: passed
- Phase 3B [3.1.0-stable] - grounded answering: passed
- Phase 3C [3.2.0-stable] - RAG quality hardening: passed
- Phase 3D [3.3.0-stable] - local FastAPI wrapper: passed
- Phase 3E [3.4.0-stable] - Open WebUI integration: passed
- Phase 4A [4.0.0-stable] - retrieval quality hardening: passed with minor tuning
- Phase 4B [4.1.0-stable] - primary workflow ingestion: passed
- Phase 4B2 [4.1.1-stable] - primary workflow fallback confidence fix: passed
- Phase 4C [4.2.0-stable] - batch post order refresh/diffing: passed
- Phase 4C1 [4.2.1-stable] - lifecycle retrieval hardening: passed with known limitation
- Phase 4C2 [4.2.2-stable] - legacy post order migration / managed source conversion: passed
- Phase 4C3 [4.2.3-stable] - announcement / reminder lifecycle ingestion: passed with minor retrieval edge case
- Phase 4D [4.3.0-stable] - operational query parser / intent extraction: passed
- Phase 4E [4.4.0-stable] - OCR intake layer: passed using pytesseract fallback
- Phase 4F [4.4.1-stable] - OCR review + ingestion bridge: passed/validated
- Phase 4G [4.5.0-stable] - temporal expiry / activation engine: passed/validated
- Phase 4G1 [4.5.1-stable] - announcement retrieval precision hardening: passed/validated
- Phase 4J-lite [4.6.0-stable] - operational dashboard / shift briefing: passed/validated
- Phase UX-1 [4.7.0-stable] - dashboard usability hardening: passed/validated
- Phase 4I-lite [4.8.2-stable] - Text Ingestion via Open WebUI Slash Commands: passed/validated
- Phase 4.9.0 [4.9.0-stable] - Scope-aware retrieval + source deduplication + alias hardening: passed/validated
- Phase 4.10.0 [4.10.0-stable] - Conversation context resolution: passed/validated
- Phase 4.11.0 [4.11.0-stable] - Workflow simplification / remove rc state: passed/validated
- Phase 4.12.0 [4.12.0-alpha] - Scope filter fix using scope_key: alpha
- Phase 4.13.0 [4.13.0-stable] - Archive redundant legacy Sierra Ridge K files: stable
- Phase 4.13.1 [4.13.1-stable] - Surface pending rules in scoped listing answers: stable
- Phase 4.13.2 [4.13.2-stable] - Fix pending detection + reverse rule order: stable
- Phase 4.13.3 [4.13.3-stable] - Fix emergency code vault data: stable
- Phase 4.13.4 [4.13.4-stable] - Fix double sources display in CLI output: stable
- Phase 4.14.0 [4.14.0-stable] - Incremental indexing with --files flag: stable
- Phase 4.15.0 [4.15.0-stable] - Streaming response with /ask/stream SSE endpoint + Open WebUI pipe: stable
- Phase 4.16.0 [4.16.0-stable] - Conflict detection + multi-turn wizard UX for /post-orders: stable
- Phase 4.17.0 [4.17.0-stable] - Quick reply hints in Open WebUI pipe + FUTURE_PLANS.md: stable
- Patch 4.17.1 [4.17.1-stable] - Duplicate sources footer + community context bleed fixes: stable
- Phase 4.18.0 [4.18.0-stable] - Community-aware kiosk call flow synthesis: stable
- Patch 4.18.1 [4.18.1-stable] - GLEN QA tip wording fix: stable
- Patch 4.18.2 [4.18.2-stable] - Prevent DeepSeek inline Sources block in answers: stable
- Patch 4.18.3 [4.18.3-alpha] - Restore clean CLI citation display: alpha

Current architecture:

```text
Open WebUI
-> FastAPI /ask or /ask/stream
-> local retrieval
-> grounded answer generation
-> citations/refusal/confidence
```

Open WebUI is presentation-only. Markdown in `vault/` remains the source of truth.

Phase 4A keeps this architecture and improves only retrieval ranking, dedupe, source selection, and citation cleanup.

Phase 4B adds the SafePassage primary kiosk workflow as global default guidance below post orders and announcements.

Phase 4C adds deterministic batch post order refresh and diffing so incoming post-order batches can be compared against active vault rules before new Markdown is created.

Phase 4C1 hardens retrieval over lifecycle-managed post orders. Active managed post orders are the operational retrieval source of truth. Pending rules are advisory only, superseded/archived rules are penalized or skipped, and legacy freeform post-order notes are skipped by default instead of deleted.

Community aliases are resolved deterministically before retrieval. Letter prefixes such as `CBK`, `SR`, `MON`, and `OPB` map to their configured community names without using numeric client codes. `rag/config/community_aliases.json` now covers the full current virtual community alias list.

Phase 4C2 converts eligible legacy freeform post orders into managed active post-order documents while preserving the original legacy files. This is used first for Sierra Ridge physical ID post orders so policy retrieval can come from managed `post_order` sources instead of weaker QA support notes.

Phase 4C3 adds deterministic announcement and reminder ingestion from cleaned pasted text. Announcements are managed lifecycle documents under `vault/05_Announcements` and sit between post orders and primary workflow in authority: `post_order > announcement > primary_workflow`.

Phase 4D adds deterministic query intent parsing before retrieval. It extracts known community aliases, operational topics, expected document types, scope hints, and default/global intent so phrases like `Red Zone Protocol` are treated as announcement topics instead of missing communities.

Phase 4E adds a local OCR intake layer for screenshots and images. OCR creates raw and reviewable text artifacts only; it does not write to `vault/`, trigger ingestion scripts, update ChromaDB, or bypass human review.

The current validated OCR backend is `pytesseract`. PaddleOCR did not pass Windows runtime validation and is deferred as an experimental future Linux, Docker, or pinned-version candidate.

Phase 4F adds an explicit OCR review queue and a deterministic review bridge. The bridge only copies human-approved reviewed OCR text into staging files under `automation/ingestion/reviewed_ocr_inputs/`; it does not write to `vault/`, trigger ingestion scripts, or update ChromaDB.

Phase 4G adds a deterministic temporal expiry / activation engine. Vault Markdown remains the source of truth, but indexed chunks can now carry temporal lifecycle metadata such as `temporal_state`, `temporal_warning`, active/effective dates, and expiry/end dates. Retrieval still preserves the authority hierarchy `post_order > announcement > primary_workflow`, but now prefers currently active temporal sources, downgrades pending, not-yet-active, expired, superseded, archived, review, and unknown-temporal sources, and exposes warnings when context is stale or uncertain.

Temporal reports can be generated under `vault/08_Reports/temporal-lifecycle/`. These reports are review artifacts only. They do not mutate operational memory, run ingestion scripts, update ChromaDB, or bypass human review.

Phase 4G1 hardens announcement retrieval precision after the temporal engine exposed a Red Zone Protocol retrieval specificity regression. It keeps the same safety boundaries and adds deterministic section-aware reranking: exact topic/title/body matches, title overlap, category matches, and the `Announcement` section are boosted, while `Operational Notes`, `Source`, migration notes, and other metadata-heavy sections are penalized for direct operational questions. It does not lower refusal thresholds globally, use LLM reranking, rewrite vault files, or let announcements override post orders.

Phase 4J-lite adds a read-only operational dashboard and deterministic shift briefing layer over indexed memory. It aggregates active announcements, active post-order warnings, temporary protocols, gate/NVR/kiosk issues, events, compliance reminders, and expiring-soon notices while preserving source paths, authority, lifecycle status, and temporal state. It does not write to `vault/`, run ingestion, update ChromaDB, create autonomous workflows, or generate operational memory.

Phase UX-1 hardens the dashboard briefing presentation and Open WebUI operator workflow. Dashboard aggregation now deduplicates repeated chunks by source file and title, excludes derived reports, visitor logs, incidents, and daily briefings from dashboard sections, expands the community alias table to the full current virtual community list, and adds a VA operator shift reference guide for Open WebUI.

Phase 4I-lite adds a guarded Open WebUI text-ingestion path through `/ask` slash commands. `/post-orders` and `/announcements` create deterministic previews, require an explicit `YES` confirmation, then call the existing ingestion scripts and rebuild ChromaDB. It does not ingest on preview, use AI parsing, bypass human confirmation, add OCR upload, add new document types, or change authority rules.

Phase 4.9.0-stable improves scoped post-order listing retrieval, citation display, and alias hardening. Scoped kiosk or concierge post-order queries for a known community request the full matching rule set, keep K/C/KC scope ordering visible to the answer model, deduplicate answer citations by source file while leaving the full retrieved source list intact, resolve long partial-name aliases, and clarify ambiguous parent community aliases before retrieval.

Phase 4.10.0-stable adds request-local conversation context resolution. The `/ask` request can include optional prior user turns in `history`; the backend uses those turns only to resolve community context for ambiguous follow-up questions and does not send history to DeepSeek.

Phase 4.11.0-stable simplifies the documentation workflow by retiring rc as an active phase state. Future phases promote directly from alpha, or beta after partial validation, to stable when validation passes and the user commits.

Phase 4.12.0-alpha fixes scoped post-order filtering by using indexed `scope_key` metadata (`k`, `c`, `kc`) instead of searching for letters in the normalized `scope` string.

Phase 4.13.0-stable archives two redundant Sierra Ridge K-scoped legacy migration post-order files that duplicated the canonical managed physical-ID rule from `/post-orders` ingestion. The files are preserved for audit history with archived lifecycle metadata and supersede references.

Phase 4.13.1-stable updates the answer prompt so full kiosk or concierge scoped post-order listing answers include pending rules in a separate `Pending — Not Yet Active` section with each pending entry labelled `[PENDING]`.

Phase 4.13.2-stable fixes post-order ingestion pending detection so only a trailing `(Pending)` marker sets pending status, and reverses parsed rule order so the operator's first pasted rule is written and indexed first.

Phase 4.13.3-stable fixes Sierra Ridge emergency-code vault metadata, ingestion supersede behavior, retrieval near-duplicate handling, indexing near-duplicate status awareness, and the direct inference prompt gap for physical ID versus digital ID questions.

Phase 4.13.4-stable fixes the CLI double sources display issue by suppressing the early source print in the normal AI answer path. The --no-ai and refusal paths keep their existing source output.

Phase 4.14.0-stable adds incremental vault indexing. `rag/scripts/index_vault.py --files [path ...]` embeds and upserts only the specified Markdown files without clearing the ChromaDB collection, while the default no-flag path remains a full rebuild. Slash-command ingestion now indexes recently modified post-order or announcement vault files after confirmed ingestion, with a fallback to full rebuild when no recent files are detected.

Phase 4.15.0-stable adds live streaming for Open WebUI. `/ask/stream` returns Server-Sent Events, forwarding DeepSeek tokens as they arrive and ending with structured citations, confidence, and warnings. `openwebui/pipe.py` is a ready-to-install Open WebUI pipe that calls the streaming endpoint and falls back to `/ask` if streaming fails. The original `/ask` endpoint remains unchanged.

Phase 4.16.0-stable adds a guided `/post-orders` wizard and conflict preview. Typing `/post-orders` alone starts a two-step community/text flow, while the existing one-line `/post-orders [alias] [text]` shortcut remains available. Post-order previews now scan active vault post-order metadata for near-topic conflicts and ask KEEP NEW or KEEP OLD before allowing the normal YES/NO ingestion confirmation.

Phase 4.17.0-stable adds quick reply hints in `openwebui/pipe.py` for prompt-for-input responses. The pipe appends bold reply options for community alias prompts, YES/NO confirmations, and KEEP NEW/KEEP OLD conflict prompts. It also introduces `docs/FUTURE_PLANS.md` as the living backlog for future phases and unimplemented ideas.

Patch 4.17.1-stable suppresses duplicate Open WebUI Sources footers when answers already include inline `[N]` citations, and prevents prior community history from bleeding into general queries such as default, global, standard, or regardless-of-community workflow questions.

Phase 4.18.0-stable enriches primary kiosk call flow SOPs with full script dialogue, adds a GLEN registered-tag QA tip, marks call flow queries in deterministic intent parsing, retrieves global SOPs alongside community-specific post orders for call flow questions, and adds prompt rules for synthesizing one integrated community-aware kiosk call flow.

Dashboard endpoints:

```text
GET /dashboard/status
GET /dashboard/summary
GET /dashboard/briefing
GET /dashboard/announcements
GET /dashboard/post-orders
GET /dashboard/issues
```

Optional community filtering is supported with `?community=CBK` or `?community=Sierra Ridge`.

Use `/dashboard/briefing` for a plain Markdown shift briefing and `/dashboard/summary` for structured dashboard data. Add `?community=CBK`, `?community=SR`, or another configured alias to include that community plus global items.

## Open WebUI

Open WebUI remains a presentation layer over the local FastAPI RAG API. VA operators should use `openwebui/USAGE_GUIDE.md` as the practical shift reference for prompts, citations, dashboard briefing use, refusals, and operational boundaries.

Open WebUI text ingestion commands are documented in `openwebui/INGEST_COMMANDS.md`.

Supported guarded ingestion commands:

```text
/post-orders CBK 5/17/2026 Post Order (K): Only contact the resident twice.
/announcements CBK CBK Pickleball Tournament May 13. Visitors should say the event name.
```

Both commands return a preview first. The user must reply `YES` to write through the deterministic ingestion scripts or `NO` to cancel.

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
