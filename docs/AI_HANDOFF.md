# AI Handoff

## Current Version: 4.15.0-alpha

## Current Phase

PHASE 4.15.0 [4.15.0-alpha] - Streaming response (/ask/stream SSE endpoint + Open WebUI pipe). Implemented but pending manual validation.

## Phase 4.15.0

Phase 4.15.0 adds a /ask/stream SSE endpoint and an Open WebUI pipe.
call_deepseek_stream() in answer_vault.py calls DeepSeek with stream=True
and yields tokens. stream_answer_question() in service.py is a generator
that runs retrieval synchronously then streams tokens as SSE data events,
followed by a [CITATIONS] event containing citations, confidence, and
warnings. The /ask/stream FastAPI endpoint wraps the generator in a
StreamingResponse. openwebui/pipe.py is a ready-to-install Open WebUI pipe
that calls /ask/stream and yields tokens live, appending formatted citations
at the end.
The original /ask endpoint is unchanged.

## Phase 4.12.0 In Progress

Phase 4.12.0-alpha fixes scoped post-order retrieval filtering in `rag/scripts/answer_vault.py`. Phase 4.9.0 filtered scoped candidates by checking whether uppercase letters `K` or `C` appeared in the indexed `scope` string, but ChromaDB stores scope as values such as `kiosk` and `kiosk, concierge`. The fix uses indexed `scope_key` metadata instead: kiosk keeps `k` and `kc`, concierge keeps `c` and `kc`. If scope filtering produces no matches, retrieval still falls back to the unfiltered candidate list.

## Phase 4.13.0 [4.13.0-stable]

Status: VALIDATED and STABLE — committed to master 2026-05-17.

Phase 4.13.0 archives two redundant Sierra Ridge K-scoped legacy migration post-order files that duplicated the canonical `/post-orders` ingestion batch rule for physical ID requirements:

- `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-visitors-present-physical-id-32e4f9f24f.md`
- `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-all-overnight-visitors-present-b89b46db47.md`

Both files are preserved for audit history with `status: archived`, `lifecycle_generation: archived`, `superseded_by: sierra-ridge-post-order-k-physical-id-required-at-all-times-83654ab9db.md`, and an archive reason. They were archived because the canonical active SR K rule is `sierra-ridge-post-order-k-physical-id-required-at-all-times-83654ab9db.md`, and the redundant legacy files caused kiosk scoped listings to include extra duplicate physical-ID rules.

## Phase 4.13.1 [4.13.1]

Status: VALIDATED and STABLE — committed to master 2026-05-17.

Phase 4.13.1 updates `rag/prompts/answer_from_context.md` so full scoped post-order listing answers include pending rules instead of only footnoting them. For full kiosk or concierge listing queries, pending rules must be shown in a separate `Pending — Not Yet Active` section and each pending entry must start with `[PENDING]`. Non-listing operational questions keep the existing behavior: answer from active sources and warn about pending sources.

## Phase 4.13.3 [4.13.3-stable]

Status: VALIDATED and STABLE — committed to master 2026-05-18.

Phase 4.13.3 fixes Sierra Ridge emergency-code vault metadata directly. The active concierge emergency code rule without a `(Pending)` marker is restored to `status: active` with no `superseded_by` reference, and the pending emergency-code variant keeps `status: pending` but no longer supersedes the active rule. This is a vault data fix only; no code, config, ingestion, or indexing scripts are changed or run in this phase.

Patch 2: near-duplicate deduplicator updated to preserve active rules over pending near-duplicates. Ensures active emergency codes are never dropped in favour of their pending variants during scoped listing retrieval.

## Phase 4.13.4 [4.13.4-stable]

Status: VALIDATED and STABLE — committed to master 2026-05-18.

Phase 4.13.4 gates the early print_sources call in answer_vault.py so it is suppressed in the normal AI answer path. Sources now print exactly once per CLI query. The --no-ai and refusal paths retain their existing source output. This is a single-line code change with no retrieval, scoring, or behavior changes.

## Phase 4.14.0 [4.14.0-stable]

Status: VALIDATED and STABLE — committed to master 2026-05-18.

Phase 4.14.0 adds incremental indexing with a `--files` flag. `rag/scripts/index_vault.py` now accepts `--files` to upsert only specified files without clearing the collection. `api/ingest.py` detects recently modified vault files after ingestion and passes them via `--files`, reducing post-ingestion index time from full-vault to new-files-only. If no recently modified vault files are detected, ingestion falls back to the existing full rebuild path.

## Phase 4.13.2 [4.13.2-stable]

Status: VALIDATED and STABLE — committed to master 2026-05-17.

Phase 4.13.2 applies two targeted fixes in `automation/ingestion/refresh_post_orders.py`. First, pending status detection now checks only for a literal `(Pending)` marker at the end of the original pasted rule text, instead of treating any rule body containing the word `pending` as pending. Second, parsed post-order rules are reversed before processing so the operator's first pasted rule is written and indexed first, preserving intended priority in retrieval.

## Phase 4.11.0 [4.11.0-stable]

Phase 4.11.0 removes rc from the active phase cycle across docs/WORKFLOW.md, docs/VERSIONING.md, docs/AI_HANDOFF.md, and the session checkpoint and opener prompts. After this phase, all future phases promote directly from alpha (or beta if partial validation) to stable when the user commits. No rc step.

Status: VALIDATED and STABLE - committed to master 2026-05-17.

## Phase 4.10.0 [4.10.0-stable] - Conversation Context Resolution

Phase 4.10.0-stable adds request-local conversation context resolution. `api/schemas.py` now accepts an optional `history` list of prior user turns. `api/service.py` adds `resolve_community_from_history()` and, when the current question has no resolved community, appends the most recent community found in the last 5 user turns to the retrieval query only. The original user question remains unchanged in the API response, and history is not sent to DeepSeek or stored server-side.

`openwebui/examples/openwebui_connection_example.md` now documents the `history` field and shows an Open WebUI Pipe snippet that builds history from prior user messages only.

Files changed for 4.10.0-stable: `api/schemas.py`, `api/service.py`, `openwebui/examples/openwebui_connection_example.md`, `docs/VERSIONING.md`, `docs/AI_HANDOFF.md`, `docs/PHASE_LOG.md`, and `README.md`. VALIDATED and STABLE - committed to master 2026-05-17.

## Phase 4.9.0 [4.9.0-stable]

Phase 4.9.0-alpha addresses two operational retrieval issues. First, scoped post-order listing queries such as "post orders for SR relevant to kiosk agents" now request complete scoped retrieval, filter candidates by K/C/KC scope metadata after community and type filtering, sort K-only or C-only rules before KC rules, and uncap scoped community post-order listings to all matching candidates. Second, API answer citations are deduplicated by `source_file` so multiple cited chunks from the same vault file do not render as duplicate source filenames.

Files changed for 4.9.0-alpha: `rag/query_intent.py`, `rag/scripts/answer_vault.py`, `rag/prompts/answer_from_context.md`, `api/service.py`, `docs/VERSIONING.md`, `docs/PHASE_LOG.md`, `docs/AI_HANDOFF.md`, and `README.md`. VALIDATED and STABLE - committed to master 2026-05-17.

Patch applied: community_aliases.json extended with partial-name aliases (SIERRA, MONTEREY, CLEARBROOK, etc.) to prevent cross-community bleed on scoped queries where the operator types a partial community name instead of the formal alias or full name.

Patch 2 applied: alias_tokens() regex cap raised from {2,6} to {2,20} in query_intent.py and answer_vault.py, fixing 17 long aliases that were silently dropped. New rag/config/ambiguous_community_aliases.json added to define parent communities with sub-communities. api/service.py now intercepts queries for ambiguous parent communities (HP, PLM, PALMS, HERITAGE) and returns a clarification message listing specific sub-community aliases instead of proceeding to retrieval.

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
- Phase 4I-lite slash command ingestion in `api/ingest.py` with /post-orders and /announcements commands routed through `api/service.py`.
- Phase 4I-lite operator guide at `openwebui/INGEST_COMMANDS.md`.
- Phase 4.14.0-stable incremental indexing in `rag/scripts/index_vault.py` with `--files`, and slash-command ingestion uses recently modified vault files for incremental post-ingestion indexing.
- Phase 4.15.0-alpha streaming response support through `/ask/stream`, `call_deepseek_stream()`, `stream_answer_question()`, and `openwebui/pipe.py`.
- Versioning reference at `docs/VERSIONING.md` - read this first for all versioning operations.
- Operational workflow reference at `docs/WORKFLOW.md` - read this at the start of every session.
- `docs/WORKFLOW.md` documents that the 3-section format is only for implementation work, not post-validation documentation, session checkpoints, or documentation-only tasks.
- Session checkpoint logs under `docs/SESSION_LOG/` for clean chathead handoff.
- Latest session checkpoint: `docs/SESSION_LOG/2026-05-18-session-01.md`.
- Scope-aware retrieval with requested_all detection in `rag/query_intent.py` and effective_top_k override in `rag/scripts/answer_vault.py`.
- Full community name matching in `rag/query_intent.py` using longest-first lookup from `rag/config/community_aliases.json`.

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
11. Read docs/WORKFLOW.md at the start of every session.
12. Read docs/VERSIONING.md before touching any version-related documentation.
13. Pull master before writing any Codex prompt.
14. Write a post-validation documentation prompt after every successful validation (promotes directly to stable - no rc step).
15. Write a session checkpoint prompt before closing a large chathead.

## Do Not Touch Without Explicit Request

- Do not rewrite the working Phase 2 Minimal POW workflow.
- Do not rewrite Phase 3A retrieval scripts from scratch.
- Do not rewrite Phase 3B answering from scratch.
- Do not revive the old complex Phase 2 workflow.
- Do not rewrite docs/WORKFLOW.md without explicit user instruction.
  This file defines the operational process and must remain stable.
- Do not skip the post-validation documentation prompt after a successful validation pass.
  It is a mandatory step in the phase cycle.
- Do not write validation commands inside Codex prompts.
  Validation commands are always given separately to the user.

## Do Not Do Yet

- Do not move retrieval, embeddings, ChromaDB, memory, ingestion, or business logic into Open WebUI.
- Do not add advanced automations beyond the documented Phase 2 ingestion workflow.
- Do not add autonomous agents, advanced memory systems, automatic memory editing, or dashboard behavior beyond the validated read-only dashboard without an explicit phase request.
- Do not use cloud embeddings.
- Do not expand Phase 3B beyond retrieved-context answer generation.
- Do not commit secrets, real API keys, `.env`, `n8n_data`, or generated credential files.

## Recommended Next Step

Next: Phase 4.16.0 - conflict detection + multi-turn wizard UX for /post-orders.

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
