# AI Handoff

## Current Version: 4.8.1-rc

## Current Phase

PHASE 4I-lite [4.8.1-rc] - Text Ingestion via Open WebUI Slash Commands. Both known bugs fixed. Manual validation pending to promote to stable. Phase 2 [2.0.0-stable] Minimal POW, Phase 3A [3.0.0-stable] Retrieval POW, Phase 3B [3.1.0-stable] Grounded Answering POW, Phase 3C [3.2.0-stable] RAG Quality Hardening, Phase 3D [3.3.0-stable] Local API Wrapper, Phase 3E [3.4.0-stable] Open WebUI Integration, Phase 4A [4.0.0-stable] Retrieval Quality Hardening, Phase 4B [4.1.0-stable] Primary Workflow Ingestion, Phase 4B2 [4.1.1-stable] fallback confidence, Phase 4C [4.2.0-stable] post order refresh, Phase 4C1 [4.2.1-stable] lifecycle retrieval hardening, Phase 4C2 [4.2.2-stable] managed post-order conversion, Phase 4C3 [4.2.3-stable] announcement ingestion, Phase 4D [4.3.0-stable] query parsing, Phase 4E [4.4.0-stable] OCR intake using pytesseract, Phase 4F [4.4.1-stable] OCR review + ingestion bridge, Phase 4G [4.5.0-stable] temporal expiry / activation, Phase 4G1 [4.5.1-stable] announcement retrieval precision hardening, Phase 4J-lite [4.6.0-stable] operational dashboard / shift briefing, and Phase UX-1 [4.7.0-stable] dashboard/OpenWebUI usability hardening are validated or mostly working.

## What Exists

- Phase 1 vault folders, templates, docs, Docker Compose, n8n setup, and schema standards.
- Phase 2 prompt chain for classification, routing, normalization, and QA risk checking.
- Phase 2 ingestion contract and routing rules.
- Sample inputs and expected outputs for test-driven workflow buildout.
- Importable n8n workflow export for local validation.
- Helper scripts for filename sanitization, payload validation, metadata validation, Markdown writing, and Git commit/push.
- n8n setup and local testing documentation.
- Phase 3A local RAG scripts under `rag/` for disposable ChromaDB indexing and retrieval-only querying.
- Phase 3A retrieval quality refinement filters low-value sections by default and prioritizes useful evidence sections.
- Phase 3B CLI answer generation in `rag/scripts/answer_vault.py`, grounded only in retrieved ChromaDB chunks.
- Phase 3D FastAPI wrapper under `api/` for local HTTP access.
- Phase 3E Open WebUI documentation under `openwebui/` for presentation-only UI integration.
- Phase 4A retrieval hardening in `query_vault.py`, `answer_vault.py`, and `api/service.py` for stronger dedupe, section weighting, and cleaner citations.
- Phase 4B primary workflow ingestion under `automation/ingestion/` for global base kiosk workflow documents.
- Phase 4C post order refresh under `automation/ingestion/refresh_post_orders.py`.
- Phase 4C1 lifecycle-aware retrieval and community aliases under `rag/scripts/` and `rag/config/community_aliases.json`.
- Phase 4C2 legacy post-order migration under `automation/ingestion/migrate_legacy_post_orders.py`.
- Phase 4C3 announcement refresh under `automation/ingestion/refresh_announcements.py`.
- Phase 4D deterministic query parser in `rag/query_intent.py` with topic config in `rag/config/query_topics.json`.
- Phase 4E OCR intake scripts under `automation/ocr/`.
- Phase 4F OCR review queue under `automation/ocr/review_queue/`.
- Phase 4F reviewed OCR staging bridge at `automation/ocr/ocr_review_bridge.py`.
- Reviewed OCR staging folder under `automation/ingestion/reviewed_ocr_inputs/`.
- Phase 4G deterministic temporal lifecycle utility in `rag/lifecycle.py`.
- Phase 4G read-only temporal report script at `automation/ingestion/report_temporal_lifecycle.py`.
- Phase 4G1 deterministic retrieval reranking helpers in `rag/retrieval_rerank.py`.
- Phase 4J-lite dashboard aggregation in `rag/dashboard.py`.
- Phase 4J-lite FastAPI dashboard routes in `api/dashboard.py`.
- Phase 4J-lite read-only CLI preview at `automation/dashboard/preview_briefing.py`.
- Phase UX-1 Open WebUI VA operator shift reference at `openwebui/USAGE_GUIDE.md`.
- Full virtual community alias table in `rag/config/community_aliases.json`.
- Phase 4I-lite slash command ingestion handler at `api/ingest.py`.
- Phase 4I-lite Open WebUI ingest command guide at `openwebui/INGEST_COMMANDS.md`.

## Current Stable Components

- `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json`
- `rag/scripts/index_vault.py`
- `rag/scripts/query_vault.py`
- `rag/scripts/answer_vault.py`
- `api/main.py`
- `api/service.py`
- `api/schemas.py`

Do not revive the old complex Phase 2 workflow unless specifically requested. The minimal POW workflow is the current stable ingestion base.

## Continue From Here

Future AI work should:

1. Keep `master` as the official branch.
2. Preserve Markdown in `vault/` as the source of truth.
3. Use `automation/ingestion/ingestion_contract.json` as the canonical payload contract.
4. Use `automation/ingestion/routing_rules.json` for folder routing.
5. Keep prompts modular.
6. Add or refine samples when document type behavior changes.
7. Keep `docs/PHASE_LOG.md` accurate.
8. Keep `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json` as the stable ingestion base.
9. Treat `vault/` Markdown as the source of truth.
10. Treat `rag/chroma/` as disposable derived data.

## Do Not Touch Without Explicit Request

- Do not rewrite the working Phase 2 Minimal POW workflow.
- Do not rewrite Phase 3A retrieval scripts from scratch.
- Do not rewrite Phase 3B answering from scratch.
- Do not revive the old complex Phase 2 workflow.

## Do Not Do Yet

- Do not move retrieval, embeddings, ChromaDB, memory, ingestion, or business logic into Open WebUI.
- Do not add advanced automations beyond the documented Phase 2 ingestion workflow.
- Do not add autonomous agents, advanced memory systems, automatic memory editing, or dashboard behavior beyond the validated read-only dashboard without an explicit phase request.
- Do not use cloud embeddings.
- Do not expand Phase 3B beyond retrieved-context answer generation.
- Do not commit secrets, real API keys, `.env`, `n8n_data`, or generated credential files.

## Recommended Next Step

After 4I-lite manual validation and commit (-> 4.8.1-stable), next phase is 4.9.0-alpha: scope-aware complete listing improvements and additional community onboarding workflows.

## Phase 4I-lite Implementation Added

Phase 4I-lite adds guarded text ingestion through Open WebUI chat messages sent to the existing `/ask` endpoint. It does not add OCR upload, autonomous ingestion, AI parsing, new authority layers, new document types, retrieval changes, or dashboard changes.

Implemented:

- `api/ingest.py` contains module-level pending state under `pending_ingest`, with a 5-minute expiry.
- `/post-orders` parses a known community alias or full community name, then deterministic dated `Post Order (K/C/K&C)` entries.
- `/announcements` parses a known community alias or full community name, then announcement blocks or numbered items with fixed keyword category inference.
- `api/service.py` routes `/post-orders`, `/announcements`, `YES`, and `NO` before normal RAG retrieval.
- Preview responses use the normal `AskResponse` shape with empty sources/citations and no AI.
- `YES` calls the existing deterministic ingestion script, then `rag/scripts/index_vault.py`; it does not call `reset_chroma.py`.
- `NO` clears pending state and writes nothing.
- Temporary batch files are written under `automation/ingestion/` and are deleted after successful ingestion plus rebuild.
- `openwebui/INGEST_COMMANDS.md` documents operator usage, confirmation, cancellation, common mistakes, supported aliases, and worked CBK examples.

Manual validation remains pending. Do not treat 4I-lite as validated until the user confirms slash command preview, confirmation, cancellation, error handling, ingestion script execution, ChromaDB rebuild, and unchanged normal RAG `/ask` behavior.

## Phase UX-1 Validated

Phase UX-1 is a usability hardening pass. It does not add operational memory, ingestion pipelines, authority layers, agents, autonomous behavior, or AI semantic rewriting.

Implemented:

- `rag/dashboard.py` now deduplicates dashboard items by `(source_file, title)` instead of `(source_file, section)`.
- `rag/dashboard.py` excludes dashboard items from `vault/08_Reports/`, `vault/07_Visitor_Logs/`, `vault/06_Incidents/`, and `vault/01_Daily_Briefings/`.
- `rag/config/community_aliases.json` now reflects the full current virtual community alias table using uppercase letter-only aliases.
- `openwebui/USAGE_GUIDE.md` gives VA operators practical shift guidance for prompts, citations, refusals, warning responses, shift-start checks, dashboard briefing endpoints, and operational boundaries.
- `README.md`, `docs/PHASE_LOG.md`, and this handoff were updated for UX-1 implementation status.

UX-1 is validated. Dashboard deduplication, source-prefix exclusion, expanded alias behavior, and Open WebUI usage documentation are part of the current working baseline.

## Phase 4J-lite Dashboard Context

Phase 4J-lite adds read-only operational visibility over indexed memory. It does not retrieve through an agent or generate new operational memory. It reads ChromaDB metadata derived from vault Markdown, groups active operational context deterministically, and returns compact shift briefing sections.

Dashboard routes are:

```text
/dashboard/status
/dashboard/summary
/dashboard/briefing
/dashboard/announcements
/dashboard/post-orders
/dashboard/issues
```

Briefing generation is deterministic. It groups active temporary protocols, gate/NVR/kiosk issues, active events, important reminders, expiring-soon notices, community-specific alerts, and QA/compliance warnings. Each item preserves source file, authority level, document type, lifecycle status, temporal state, effective date, and expiry date.

This is an operational usability layer only. It must not write to `vault/`, run ingestion, update ChromaDB, bypass human review, bypass safe refusal, create agents, or let summaries override source authority.

Phase 4G1 was needed after Phase 4G validation exposed a retrieval precision regression: `What is the Red Zone Protocol reminder?` parsed correctly but could retrieve nearby reminder chunks instead of the exact Red Zone Protocol announcement. The failure was chunk/ranking specificity, not safe refusal or intent extraction.

Retrieval now uses deterministic reranking after vector retrieval. The reranker considers exact topic phrase matches, title overlap, keyword overlap, category match, direct answer section weighting, authority, lifecycle, and temporal state. It boosts the direct `Announcement` body section and penalizes `Operational Notes`, `Source`, migration notes, and other metadata-heavy sections for direct operational questions without fully excluding them.

Phase 4G adds deterministic date-aware lifecycle interpretation for managed operational memory. Temporal states are `active`, `pending`, `not_yet_active`, `expired`, `superseded`, `archived`, `review`, and `unknown`. Retrieval still preserves `post_order > announcement > primary_workflow`, but active temporal sources should rank above stale, future-dated, review, archived, superseded, or unknown-temporal sources.

Generated temporal reports under `vault/08_Reports/temporal-lifecycle/` are reports only. They are not operational memory unless separately reviewed and ingested by deterministic processes. The report script must not delete or mutate source vault documents, run ingestion scripts, or update ChromaDB.

OCR is operational using pytesseract. PaddleOCR did not pass Windows runtime validation and should be treated as experimental/deferred unless a future phase pins a compatible version or moves OCR to Linux/Docker.

Phase 4F only stages human-approved reviewed OCR text into `automation/ingestion/reviewed_ocr_inputs/`. It must not directly modify operational memory. Do not add automatic OCR-to-vault ingestion, autonomous agents, n8n rewrites, Open WebUI business logic, destructive cleanup, AI-based parsing, automatic ingestion-script calls, or ChromaDB updates.

## Phase 3C Passed

Phase 3C changes are intentionally narrow:

- stronger near-duplicate suppression;
- section and metadata reranking;
- deterministic community/type hints;
- conservative insufficient-context refusal;
- cleaner answer citation reporting.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 3D Passed

Phase 3D adds a local FastAPI wrapper only:

- `api/main.py`
- `api/schemas.py`
- `api/service.py`
- `api/README.md`

The `/ask` endpoint wraps the existing `rag/scripts/answer_vault.py` logic. It does not add Open WebUI, n8n changes, agents, memory editing, or Git automation.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 3E Passed

Phase 3E documents Open WebUI as a presentation layer that calls the local FastAPI backend.

Created docs:

- `openwebui/README.md`
- `openwebui/examples/openwebui_connection_example.md`

Architecture boundary:

```text
Open WebUI -> FastAPI -> retrieval -> grounded answering -> citations/refusal
```

Do not move retrieval, embeddings, ChromaDB, memory, ingestion, or business logic into Open WebUI. Do not add agents, tool calling, automatic vault editing, workflow automation, or Git auto-commit.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 4A Passed With Minor Tuning

Phase 4A is quality hardening only. It keeps the current architecture:

```text
Open WebUI -> FastAPI /ask -> ChromaDB retrieval -> Markdown vault -> DeepSeek grounded answer -> citations/refusal
```

Current changes:

- retrieval scoring prefers `Agent Action`, `Summary`, `Details`, `Rule`, `Policy`, then `QA Notes`;
- dedupe runs after reranking, so the strongest duplicate survives;
- duplicate detection uses normalized title, community, type, section, content preview, and lightweight content similarity;
- API answers strip trailing model-generated `Sources:` blocks and return citations through `answer_citations`;
- refusal behavior remains conservative for missing community or weak context.

Do not add agents, autonomous memory editing, n8n changes, Open WebUI custom UI changes, Git auto-commit, dashboards, voice, Phase 4B chat modes, or Phase 4C continuous ingestion.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 4B In Progress

Phase 4B adds primary workflow ingestion only.

Authority hierarchy:

```text
post_order > announcement > primary_workflow
```

Primary workflow documents are global default guidance. They must not override community post orders or announcements.

Key files:

- `automation/ingestion/primary_workflow_input_template.md`
- `automation/ingestion/sample_primary_workflow_input.md`
- `automation/ingestion/ingest_primary_workflow.py`
- `docs/PHASE_4B_PRIMARY_WORKFLOW_INGESTION.md`
- `rag/tests/primary_workflow_test_queries.json`

RAG changes:

- `index_vault.py` preserves `authority_level` and `scope`;
- `query_vault.py` and `answer_vault.py` apply authority-aware scoring;
- `answer_from_context.md` instructs DeepSeek to label primary workflow answers as default guidance;
- unknown community workflow questions can fall back to global primary workflow when context is relevant;
- community-specific post orders and announcements should outrank primary workflow.

Do not add batch diffing, announcement automation, autonomous memory editing, n8n changes, Open WebUI UI changes, agents, Git automation, dashboards, or Phase 4C behavior.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 4B2 In Progress

Phase 4B2 is a narrow confidence/refusal refinement.

What changed:

- `primary_workflow_default_threshold` allows slightly higher distances for explicit default/base workflow questions;
- fallback confidence requires global `authority_level: primary_workflow` context;
- unknown community-specific questions still refuse when no community source exists;
- post orders and announcements remain higher authority than primary workflow.

Do not globally raise `weak_context_distance_threshold`. Do not expand 4B2 beyond the narrow fallback-confidence rule.

## Phase 4C In Progress

Phase 4C implements deterministic batch post order refresh only.

Key files:

- `automation/ingestion/refresh_post_orders.py`
- `automation/ingestion/sample_post_order_batch.md`
- `automation/ingestion/post_order_refresh_expected_results.md`
- `docs/PHASE_4C_POST_ORDER_REFRESH_DIFFING.md`

Lifecycle metadata:

- `rule_id`
- `rule_hash`
- `topic_key`
- `source_batch`
- `batch_date`
- `supersedes`
- `superseded_by`

Behavior:

- duplicate active hashes are not duplicated;
- same community/scope/topic with a changed hash supersedes the old managed active rule unless a simple conflict is detected;
- conflicts are written as `status: conflict` and reported;
- missing active managed rules are report-only;
- old rules are never deleted.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 4C1 In Progress

Phase 4C1 hardens retrieval over lifecycle-managed post orders.

Key files:

- `rag/config/community_aliases.json`
- `rag/config/retrieval_config.json`
- `rag/scripts/index_vault.py`
- `rag/scripts/query_vault.py`
- `rag/scripts/answer_vault.py`
- `api/service.py`
- `api/schemas.py`

Behavior:

- aliases such as `CBK`, `SR`, `MON`, and `OPB` expand before retrieval;
- `lifecycle_generation: managed` post orders are preferred;
- `lifecycle_generation: legacy` post orders are skipped by default;
- `active` outranks `pending`, `review`, `needs_review`, `superseded`, and `archived`;
- pending rules are advisory and must not override active rules;
- unknown community refusal remains conservative.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 4C2 In Progress

Phase 4C2 converts eligible legacy freeform post orders into lifecycle-managed active post-order documents.

Key files:

- `automation/ingestion/migrate_legacy_post_orders.py`
- `vault/03_Post_Orders/sierra-ridge-managed-post-order-*.md`
- `vault/08_Reports/post-order-migration/2026-05-16-legacy-post-order-migration.md`

Behavior:

- only `type: post_order` legacy files are eligible;
- QA rules are not migrated into post orders;
- original legacy files are preserved;
- generated managed copies include `lifecycle_generation: managed`, `status: active`, `rule_id`, `rule_hash`, `source_legacy_file`, `source_migration`, and `migration_date`;
- duplicate managed rules are skipped by `rule_hash`;
- managed docs are the operational retrieval source of truth.

The user will manually validate, review, and commit. Do not run `git commit` or `git push`.

## Phase 4C3 Passed With Minor Retrieval Edge Case

Phase 4C3 ingests daily reminder and announcement text as managed lifecycle documents.

Key files:

- `automation/ingestion/refresh_announcements.py`
- `automation/ingestion/sample_announcement_batch.md`
- `vault/05_Announcements/`
- `vault/08_Reports/announcement-refresh/`

Behavior:

- parses cleaned pasted text only;
- OCR and screenshot parsing are deferred;
- creates `type: announcement` documents with `authority_level: announcement`;
- announcement authority is below post orders and above primary workflow;
- active announcements are usable context;
- pending announcements are advisory;
- expired and archived announcements are penalized or skipped by retrieval;
- post orders must still win when they conflict with announcements.

Phase 4C3 is treated as passed with a minor retrieval edge case: `Red Zone Protocol` needed to be parsed as an operational topic instead of a missing community. Phase 4D addresses that parser issue. Do not run `git commit` or `git push`.

## Phase 4D Passed

Phase 4D adds deterministic query intent extraction before retrieval.

Key files:

- `rag/query_intent.py`
- `rag/config/query_topics.json`
- `rag/scripts/query_vault.py`
- `rag/scripts/answer_vault.py`

Behavior:

- community extraction only trusts configured aliases, known community names, and narrow unknown-community patterns;
- operational proper nouns such as `Red Zone Protocol`, `Support Room`, `Community Approved List`, `Emergency Code`, and `Pickleball Tournament` are treated as topics, not communities;
- expected document types are inferred deterministically from keywords and configured topics;
- global announcement topics do not require a community hint;
- unknown community-specific questions still refuse safely when no matching community source exists.

The parser must not replace lifecycle scoring, authority hierarchy, primary workflow fallback, or grounded-answer refusal behavior. Do not run `git commit` or `git push`.

## Phase 4E Passed Using Pytesseract

Phase 4E adds local OCR intake only. The validated backend is pytesseract.

Key files:

- `automation/ocr/ocr_extract.py`
- `automation/ocr/ocr_review_formatter.py`
- `automation/ocr/output/`
- `automation/ocr/sample_images/`
- `docs/OCR_WORKFLOW.md`

Behavior:

- accepts `png`, `jpg`, `jpeg`, and `webp`;
- supports one image or an input directory;
- uses pytesseract as the current validated OCR backend;
- treats PaddleOCR as experimental/deferred after Windows runtime validation failure;
- writes raw text and review Markdown artifacts;
- includes OCR engine and confidence when available;
- performs conservative whitespace cleanup only;
- preserves community aliases such as `CBK`, `PBM`, `SR`, `SSR`, and `OPB`;
- never writes to `vault/`;
- never calls `refresh_announcements.py` or `refresh_post_orders.py`;
- never bypasses human review.

The future direction is reviewed OCR handoff into existing deterministic ingestion inputs, not autonomous memory editing.

## Phase 4F Implementation Added

Phase 4F creates a deterministic bridge from reviewed OCR Markdown into staging ingestion input files.

Key files:

- `automation/ocr/ocr_review_bridge.py`
- `automation/ocr/review_queue/pending/.gitkeep`
- `automation/ocr/review_queue/approved/.gitkeep`
- `automation/ocr/review_queue/rejected/.gitkeep`
- `automation/ingestion/reviewed_ocr_inputs/.gitkeep`
- `automation/ocr/ocr_review_formatter.py`

Behavior:

- generated OCR review Markdown now includes `review_status`, `approved_for_ingestion`, `target_ingestion_type`, `reviewed_by`, `reviewed_at`, and `review_notes`;
- new review files default to pending, not approved;
- the bridge refuses unless `review_status: approved`, `approved_for_ingestion: true`, and `target_ingestion_type` is `announcement` or `post_order`;
- the bridge extracts only the reviewed text under `## Extracted Text`;
- default staging outputs are `reviewed_ocr_announcements.md` and `reviewed_ocr_post_orders.md`;
- reviewed text is preserved as-is with a simple source filename and timestamp header;
- the bridge never writes to `vault/`, never calls ingestion scripts, and never updates ChromaDB.

After manual validation, the next recommended step is for the user to manually run the appropriate deterministic ingestion script against acceptable reviewed OCR staging input, then manually rebuild ChromaDB.

## Phase 3A Exit Criteria

Phase 3A should only be marked validated after:

- dependencies install from `rag/requirements.txt`;
- `python rag/scripts/index_vault.py` creates a local ChromaDB index;
- `query_vault.py` retrieves Sierra Ridge `post_order` or `qa_rule` chunks for physical ID questions;
- `query_vault.py` retrieves a Monterey `incident` chunk for tailgating questions;
- low-value sections such as `Change History`, `Open Questions`, and `Source Input` do not pollute default top results;
- retrieval quality is inspected before any answer generation is added.

## Phase 3B Exit Criteria

Phase 3B should only be marked validated after:

- `DEEPSEEK_API_KEY` is handled through the environment only;
- `answer_vault.py --no-ai --show-context` works without an API key;
- generated answers cite source file and section;
- insufficient context produces a safe refusal;
- no Open WebUI-hosted retrieval, n8n changes, agents, or automation are added.

## Phase 2 Exit Criteria

Phase 2 should only be marked complete after:

- n8n workflow imports successfully.
- Sample inputs are run through the prompt chain.
- Generated Markdown is inspected for metadata completeness.
- Routing rules are verified against every supported document type.
- QA risk review behavior is tested.
- Git commit behavior is tested on `master`.

Until then, Phase 2 must remain `IN PROGRESS`.
