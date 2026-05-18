# Version History

| Version | Phase | State | Date | Summary |
| --- | --- | --- | --- | --- |
| 4.13.1-stable | Patch | stable | 2026-05-17 | surface pending rules in scoped listing - VALIDATED |
| 4.13.0-stable | Phase 4.13.0 | stable | 2026-05-17 | archive redundant legacy SR K files - VALIDATED |
| 4.12.1 | Patch | stable | 2026-05-17 | lock X.Y.Z versioning convention |
| 4.12.0-alpha | Phase 4.12.0 | alpha | 2026-05-17 | scope filter fix - scope_key |
| 4.11.0-stable | Phase 4.11.0 | stable | 2026-05-17 | workflow simplification - remove rc state - VALIDATED |
| 4.10.0-stable | Phase 4.10.0 | stable | 2026-05-17 | conversation context resolution - VALIDATED |
| 4.9.0-stable | Phase 4.9.0 | stable | 2026-05-17 | scope retrieval + source dedup + alias hardening - VALIDATED |
| 4.8.2-stable | Phase 4I-lite | stable | 2026-05-17 | DATE_PATTERN word boundary fix - VALIDATED |
| 4.8.1-stable | Phase 4I-lite | stable | 2026-05-17 | top_k fix + name match fix - VALIDATED |
| 4.8.0-beta | Phase 4I-lite | beta | 2026-05-17 | slash commands, scope rerank partial |
| 4.7.0-stable | Phase UX-1 | stable | 2026-05-17 | dashboard + alias expansion |
| 4.6.0-stable | Phase 4J-lite | stable | 2026-05-17 | operational dashboard |
| 4.5.1-stable | Phase 4G1 | stable | 2026-05-17 | retrieval precision hardening |
| 4.5.0-stable | Phase 4G | stable | 2026-05-17 | temporal lifecycle engine |
| 4.4.1-stable | Phase 4F | stable | 2026-05-17 | OCR review bridge |
| 4.4.0-stable | Phase 4E | stable | 2026-05-17 | OCR intake layer |
| 4.3.0-stable | Phase 4D | stable | 2026-05-17 | query intent parser |
| 4.2.3-stable | Phase 4C3 | stable | 2026-05-17 | announcement ingestion |
| 4.2.2-stable | Phase 4C2 | stable | 2026-05-17 | legacy post order migration |
| 4.2.1-stable | Phase 4C1 | stable | 2026-05-17 | lifecycle retrieval hardening |
| 4.2.0-stable | Phase 4C | stable | 2026-05-17 | batch post order refresh |
| 4.1.1-stable | Phase 4B2 | stable | 2026-05-17 | fallback confidence fix |
| 4.1.0-stable | Phase 4B | stable | 2026-05-17 | primary workflow ingestion |
| 4.0.0-stable | Phase 4A | stable | 2026-05-17 | retrieval quality hardening |
| 3.4.0-stable | Phase 3E | stable | 2026-05-17 | Open WebUI integration |
| 3.3.0-stable | Phase 3D | stable | 2026-05-17 | FastAPI local wrapper |
| 3.2.0-stable | Phase 3C | stable | 2026-05-17 | RAG quality hardening |
| 3.1.0-stable | Phase 3B | stable | 2026-05-17 | grounded answering |
| 3.0.0-stable | Phase 3A | stable | 2026-05-17 | retrieval POW |
| 2.0.0-stable | Phase 2 | stable | 2026-05-17 | minimal POW ingestion |

# Phase Log

## Phase 4.13.1 Surface Pending Rules in Scoped Listing Answers

Status: PASSED — stable

Version: 4.13.1-stable

Date: 2026-05-17

Purpose:

Update the answer prompt so full scoped post-order listing queries include pending rules inline instead of only footnoting them.

Implementation scope:

- `rag/prompts/answer_from_context.md`: add full-listing instruction requiring active rules first and pending rules in a separate `Pending — Not Yet Active` section with each pending entry labelled `[PENDING]`.
- `docs/VERSIONING.md`, `docs/AI_HANDOFF.md`, `docs/PHASE_LOG.md`, and `README.md`: record 4.13.1 as the current prompt-only patch.

Validation checklist:

- [ ] User validates full kiosk scoped listing includes active K/KC rules and pending K/KC rules.
- [ ] User validates full concierge scoped listing includes active C/KC rules and pending C/KC rules.
- [ ] User validates every pending rule in a full listing starts with `[PENDING]`.
- [ ] User validates pending rules appear under `Pending — Not Yet Active`.
- [ ] User validates specific non-listing operational questions still answer from active sources and warn about pending sources.
- [ ] User validates no Python code, config, vault, indexing, or retrieval logic changed.

### Validation Record — 4.13.1-stable
Date: 2026-05-17
All checks passed. Committed to master.
- [x] Kiosk listing correct: 8 total (3K + 4KC active, 1KC pending)
- [x] Concierge listing correct: 9 total (1C + 4KC active, 2C + 1KC pending)
- [x] Specific query old behavior preserved
- [x] No code files touched
Non-blocking: sources list appears twice in CLI output — display only

## Phase 4.13.0 Archive Redundant Legacy SR K Files

Status: PASSED — stable

Version: 4.13.0-stable

Date: 2026-05-17

Purpose:

Archive two redundant Sierra Ridge K-scoped legacy migration post-order files that duplicate the canonical managed post order from the `/post-orders` ingestion batch.

Files archived:

- `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-visitors-present-physical-id-32e4f9f24f.md`
- `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-all-overnight-visitors-present-b89b46db47.md`

Reason:

The files were Phase 4C2 legacy migration artifacts and are operationally superseded by `vault/03_Post_Orders/sierra-ridge-post-order-k-physical-id-required-at-all-times-83654ab9db.md`. Keeping them active caused Sierra Ridge kiosk scoped listings to include redundant physical-ID rules. The files were not deleted; their frontmatter was changed to `status: archived` and `lifecycle_generation: archived` with `superseded_by` and `archive_reason` metadata for audit history.

### Validation Record — 4.13.0-stable
Date: 2026-05-17
All checks passed. Committed to master.
- [x] Both legacy files archived correctly
- [x] ChromaDB rebuilt successfully (206 chunks, 111 files)
- [x] Kiosk returns 8 rules — correct count
- [x] No legacy bleed
- [x] No code files touched

## Phase 4.12.0 Scope Filter Fix - scope_key

Status: IN PROGRESS

Version: 4.12.0-alpha

Date started: 2026-05-17

Purpose:

Phase 4.12.0 fixes the scoped post-order candidate filter introduced in Phase 4.9.0. The filter now uses indexed `scope_key` metadata instead of searching for letters in the normalized `scope` string.

Implementation scope:

- `rag/scripts/answer_vault.py`: kiosk scope filtering keeps candidates with `scope_key` `k` or `kc`; concierge scope filtering keeps candidates with `scope_key` `c` or `kc`.
- `docs/VERSIONING.md`, `docs/AI_HANDOFF.md`, `docs/PHASE_LOG.md`, and `README.md`: record 4.12.0-alpha as the current in-progress implementation.

Validation checklist:

- [ ] User validates kiosk scoped listing returns K and KC rules using `scope_key`.
- [ ] User validates concierge scoped listing returns C and KC rules using `scope_key`.
- [ ] User validates fallback to unfiltered candidates remains intact when scoped filtering returns no matches.
- [ ] User validates no unrelated retrieval, reranking, query intent, indexing, ingestion, config, vault, or API behavior changed.

## Phase 4.11.0 Workflow Simplification - Remove rc State

Status: PASSED - stable

Version: 4.11.0-stable

Date started: 2026-05-17

Goal:

Remove rc state from the active phase cycle. Documentation-only phase.

Files changed:

- `docs/VERSIONING.md`
- `docs/WORKFLOW.md`
- `docs/AI_HANDOFF.md`
- `docs/PHASE_LOG.md`
- `docs/SESSION_LOG/` (checkpoint)
- `docs/NEW_CHATHEAD_OPENER.md`
- `README.md`

Validation checklist:

- [x] docs/VERSIONING.md: rc removed from active promotion rules
- [x] docs/WORKFLOW.md: DOCUMENT step updated, rc references removed
- [x] docs/AI_HANDOFF.md: updated to reflect simplified cycle
- [x] docs/PHASE_LOG.md: updated
- [x] Session checkpoint and opener prompts updated in session log
- [x] All existing phase entries preserved unchanged

### Validation Record - 4.11.0-stable
Date: 2026-05-17
All checks passed. Committed to master.
- [x] rc retired from active cycle in VERSIONING.md and WORKFLOW.md
- [x] 4.10.0 promoted to stable in all four locations
- [x] No code files touched
- [x] All existing phase history preserved

## Phase 4.10.0 Conversation Context Resolution

Status: PASSED - stable

Version: 4.10.0-stable

Date started: 2026-05-17

Purpose:

Phase 4.10.0 adds lightweight conversation context resolution to `/ask`. The API can accept up to 5 prior user turns in a request-local `history` field and use them only to resolve community context when the current question is ambiguous. History is not stored server-side and is not sent to DeepSeek.

Implementation scope:

- `api/schemas.py`: add optional `history` list to `AskRequest`.
- `api/service.py`: add `resolve_community_from_history()` and patch the retrieval question with a history-derived community only when the current question has no community.
- `openwebui/examples/openwebui_connection_example.md`: document the optional `history` field and Open WebUI Pipe history extraction.
- `docs/VERSIONING.md`, `docs/AI_HANDOFF.md`, `docs/PHASE_LOG.md`, and `README.md`: record 4.10.0-stable validation status.

Validation checklist:

- [x] User validates callers without `history` continue to work unchanged.
- [x] User validates history is capped to the last 5 user turns.
- [x] User validates current-query community takes priority over history.
- [x] User validates an ambiguous follow-up can resolve community from prior user turns.
- [x] User validates history is not sent to DeepSeek.
- [x] User validates `request.question` in the API response remains the original unpatched question.
- [x] User validates safe refusal remains unchanged when neither current question nor history resolves a community.

### Validation Record - 4.10.0-stable
Date: 2026-05-17
All checks passed. Committed to master.

Passed:
- [x] AskRequest history field added, defaults to empty list
- [x] Existing callers unaffected
- [x] Ambiguous follow-up resolves community from history
- [x] Original question preserved in response
- [x] Explicit community in current question ignores history
- [x] Most-recent-first resolution correct
- [x] Empty history stateless fallback clean
- [x] Normal RAG unaffected

Non-blocking:
- History patches retrieval query only, not DeepSeek prompt - by design
- Pipe update required to activate feature in Open WebUI

## Phase 4.9.0 Scope-Aware Retrieval + Source Deduplication

Status: PASSED - stable

Version: 4.9.0-stable

Date started: 2026-05-17

Purpose:

Phase 4.9.0 fixes two operational usability bugs found after 4.8.2-stable:

- Scope-filtered post-order listing queries could set `scope_hint` but still return only the default top 5 chunks, causing missing kiosk or concierge rules.
- API `answer_citations` could show duplicate source filenames when DeepSeek cited multiple chunks from the same vault file.

Implementation scope:

- `rag/query_intent.py`: extend requested-all phrase detection for scoped post-order language and mark known community + scoped post-order queries as complete-list requests.
- `rag/scripts/answer_vault.py`: filter scoped candidates after community/type filtering, sort K-only or C-only rules before KC rules, and uncap scoped community post-order listings to all matching candidates.
- `rag/prompts/answer_from_context.md`: instruct the answer model to label scope and group full scoped listings by K/C-only first, then KC.
- `api/service.py`: deduplicate `answer_citations` by `source_file` while leaving the full retrieved `sources` list unchanged.
- `docs/VERSIONING.md`, `docs/AI_HANDOFF.md`, `docs/PHASE_LOG.md`, and `README.md`: record 4.9.0-alpha as the current in-progress implementation.

Validation checklist:

- [x] User validates `what are the post orders for SR relevant to kiosk agents` returns all K and KC rules.
- [x] User validates kiosk scoped listings show K-only rules before KC rules.
- [x] User validates concierge scoped listings show C-only rules before KC rules.
- [x] User validates scoped listing retrieval does not leak rules from another community.
- [x] User validates normal non-scoped queries keep normal top_k behavior.
- [x] User validates `answer_citations` has no duplicate `source_file` entries.
- [x] User validates safe refusal remains unchanged when no relevant context exists.

### Validation Record - 4.9.0-rc
Date: 2026-05-17
All checks passed.
Committed to master: 2026-05-17

Passed:
- [x] requested_all triggers on scoped listing phrases
- [x] scope_hint=kiosk and scope_hint=concierge detected correctly
- [x] Scoped listing returns all matching rules uncapped
- [x] No cross-community bleed on scoped queries
- [x] K-only / K&C grouping in AI answer
- [x] Concierge scope symmetric
- [x] answer_citations deduplicated by source_file
- [x] SIERRA and all partial-name aliases resolve correctly
- [x] Long aliases (>6 chars) resolve after regex fix
- [x] HP/PLM/PALMS/HERITAGE return clarification message
- [x] Sub-community aliases (HPS, HPD, HPN, PLMIM) not intercepted
- [x] Existing aliases unbroken
- [x] Normal RAG unaffected

Non-blocking:
- SIERRA may show as alias label instead of SR when both in alias table
- Some scoped answers cite Scope section chunk instead of Rule section chunk for same file - content correct, cosmetic only

## Current Phase

PHASE 4.12.0 [4.12.0-alpha] SCOPE FILTER FIX

## Overall System Status

WORKING PROOF OF WORK

The final project is not complete. The current validated checkpoint proves local ingestion, retrieval, grounded answering, local API access, Open WebUI presentation integration, Phase 4A retrieval hardening, Phase 4B primary workflow ingestion, Phase 4B2 fallback confidence, Phase 4C batch post order refresh/diffing, Phase 4C1 lifecycle retrieval hardening, Phase 4C2 legacy post-order managed conversion, Phase 4C3 announcement lifecycle ingestion, Phase 4D query intent parsing, Phase 4E OCR intake using pytesseract fallback, Phase 4F OCR review + ingestion bridge, Phase 4G temporal expiry / activation, Phase 4G1 announcement retrieval precision hardening, Phase 4J-lite operational dashboard / shift briefing, Phase UX-1 dashboard/OpenWebUI usability hardening, Phase 4I-lite slash command ingestion plus scope retrieval fixes, Phase 4.9.0 scope retrieval/source deduplication/alias hardening, Phase 4.10.0 conversation context resolution, and Phase 4.11.0 workflow simplification. Phase 4.11.0 is stable.

## Phase 2 Minimal POW

PASSED

Validated:

- [x] `/help` returned usage and wrote no file
- [x] `/post` routed to `vault/03_Post_Orders`
- [x] `/qa` routed to `vault/04_QA_Rules`
- [x] `/incident` routed to `vault/06_Incidents`
- [x] `/log` routed to `vault/07_Visitor_Logs`
- [x] unknown fallback routed to `vault/00_Inbox`
- [x] invalid DeepSeek key still produced fallback Markdown and wrote a file
- [x] deterministic classification works
- [x] deterministic routing works
- [x] local vault writing works

Stable workflow:

```text
workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json
```

Do not revive or rewrite the older complex Phase 2 workflow unless specifically requested.

## Phase 3A Minimal RAG Retrieval POW

PASSED

Validated:

- [x] ChromaDB local index works
- [x] `sentence-transformers` embeddings work
- [x] vault Markdown chunking works
- [x] low-value section filtering works
- [x] duplicate chunks reduced
- [x] retrieval returns correct community/type/sections
- [x] no AI answer generation in Phase 3A

Validated index run:

```text
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

Successful retrieval queries:

```text
overnight visitors must present physical ID before access
What happened with tailgating at Monterey?
What should the agent do if digital ID is presented instead of physical ID?
```

## Phase 3B Grounded Answering POW

PASSED

Validated:

- [x] retrieval-only `--no-ai` works
- [x] DeepSeek answer generation works
- [x] answers use retrieved context
- [x] source citations are included
- [x] insufficient context question correctly refuses unsafe answer
- [x] operational answers are concise and grounded

Validated answer commands:

```text
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Expected results:

- first three questions answer correctly from retrieved context
- Atlantis Bay refuses with insufficient context

## Known Issues / Next Refinements

These are not blockers.

1. Duplicate source files still appear in retrieval results.
   Cause: multiple generated test files contain nearly identical Sierra Ridge post orders.
   Future fix: add stronger dedupe by normalized title + section + community, or clean duplicate test files.

2. Citations can still be incomplete if DeepSeek omits explicit source IDs.
   Future fix: improve prompt enforcement or add stricter answer post-validation.

3. Retrieval ranking remains heuristic.
   Future fix: add measured reranking tests once more real vault documents exist.

4. Source numbering depends on the model citing retrieved source IDs exactly.
   Future fix: reject or retry generated answers that cite missing IDs.

5. Titles and filenames are too verbose.
   Future fix: add deterministic title compression and filename compression.

6. Incident documents need richer structured fields.
   Future fix: expand incident ingestion format with time, lane, vehicle details, action taken, escalation, and camera reference.

7. Open Questions may contain generic AI filler.
   Future fix: only include open questions when confidence is low or required operational fields are missing.

8. Git auto-commit remains deferred.
   Future fix: add manual or controlled sync later only after retrieval and answering remain stable.

## Next Recommended Step

Start Phase 4.9.0-alpha Community Onboarding + Scope-Aware Retrieval Improvements after the 4.8.2-stable commit is in place.

Scope:

- continue onboarding remaining unindexed communities with reviewed post-order text;
- use `/post-orders [ALIAS] [text]` in Open WebUI for deterministic ingestion;
- preserve confirmation-before-write behavior for all ingestion;
- improve scope-aware "show me all" retrieval behavior across more communities;
- keep vault Markdown as source of truth and `rag/chroma/` disposable.

Do not jump to agents, direct vault editing, automatic OCR ingestion, or Phase 5 without an explicit phase request.

## Phase 3C RAG Quality Hardening

PASSED

- [x] Add stronger near-duplicate suppression
- [x] Add section reranking refinements
- [x] Add deterministic community/type query hints
- [x] Add stronger insufficient-context checks
- [x] Separate retrieved sources from answer citations
- [x] Add retrieval confidence output
- [x] User runs validation commands locally
- [x] User reviews changes manually
- [ ] User commits changes manually

No Open WebUI, n8n changes, agents, Git auto-commit, dashboards, voice, or Phase 4 automations were added.

## Phase 3D Local API Interface Wrapper

PASSED

- [x] Add FastAPI app under `api/`
- [x] Add `/ask` endpoint
- [x] Reuse existing RAG answer pipeline
- [x] Return JSON answer, citations, confidence, and retrieved sources
- [x] Support `no_ai=true`
- [x] Handle missing `DEEPSEEK_API_KEY` cleanly
- [x] User starts local API server
- [x] User validates `/ask` AI mode
- [x] User validates `/ask` no-AI mode
- [x] User validates Atlantis Bay insufficient-context refusal
- [x] User reviews changes manually
- [ ] User commits changes manually

No Open WebUI, n8n changes, agents, autonomous memory editing, Git auto-commit, dashboards, voice, or Phase 4 automations were added.

## Phase 3E Open WebUI Integration

PASSED

- [x] Add Open WebUI setup documentation
- [x] Add Open WebUI connection example
- [x] Document FastAPI as the operational backend
- [x] Document UI formatting for answers, citations, confidence, and warnings
- [x] Document Open WebUI operational boundaries
- [x] User configures Open WebUI to call local FastAPI
- [x] User validates Sierra Ridge ID rules prompt
- [x] User validates Sierra Ridge digital ID prompt
- [x] User validates Monterey tailgating prompt
- [x] User validates Atlantis Bay refusal prompt
- [x] User reviews changes manually
- [ ] User commits changes manually

Open WebUI is presentation-only. No agents, automatic vault editing, memory rewriting, tool calling, workflow automation, Git auto-commit, dashboards, or Phase 4 automations were added.

## Phase 4A Retrieval Quality Hardening

PASSED WITH MINOR TUNING

- [x] Prefer operational sections in retrieval scoring: `Agent Action`, `Summary`, `Details`, `Rule`, `Policy`, then `QA Notes`
- [x] Keep low-value sections below useful sections when explicitly included
- [x] Deduplicate after reranking so the strongest near-duplicate source survives
- [x] Dedupe by normalized title, community, type, section, content preview, and lightweight content similarity
- [x] Strip model-generated trailing Sources blocks from API answers
- [x] Keep `answer_citations` separate from `sources`
- [x] Preserve source ID alignment between retrieved context and answer citations
- [x] Preserve conservative insufficient-context refusal behavior
- [x] User rebuilds ChromaDB and validates retrieval locally
- [x] User validates FastAPI/Open WebUI answer formatting
- [x] User reviews changes manually
- [ ] User commits changes manually

No agents, autonomous memory editing, n8n changes, Open WebUI custom UI changes, Git auto-commit, dashboards, voice, Phase 4B chat modes, or Phase 4C continuous ingestion were added.

## Phase 4B Primary Workflow Ingestion

PASSED

- [x] Add primary workflow input template
- [x] Add structured sample primary workflow input
- [x] Add deterministic primary workflow ingestion script
- [x] Generate workflow documents with `authority_level: primary_workflow`
- [x] Preserve source document, source section, source page, and authority note
- [x] Add authority metadata to ChromaDB indexing
- [x] Add authority-aware retrieval ranking
- [x] Add primary workflow fallback behavior for unknown communities
- [x] Update answer prompt rules for authority hierarchy
- [ ] User runs primary workflow ingestion
- [ ] User rebuilds ChromaDB
- [ ] User validates primary workflow fallback answers
- [ ] User validates post orders still outrank primary workflow
- [ ] User reviews changes manually
- [ ] User commits changes manually

Authority hierarchy:

```text
post_order
announcement
primary_workflow
```

No batch post order diffing, announcement diffing, autonomous memory editing, n8n changes, Open WebUI UI changes, agents, Git automation, dashboards, or Phase 4C behavior were added.

## Phase 4B2 Primary Workflow Fallback Confidence Fix

PASSED

- [x] Add configurable `primary_workflow_default_threshold`
- [x] Allow fallback confidence only for explicit default/base/primary workflow queries
- [x] Require global `authority_level: primary_workflow` context for fallback confidence
- [x] Keep unknown community-specific questions on the conservative refusal path
- [x] Preserve `post_order > announcement > primary_workflow`
- [x] Preserve API response compatibility
- [x] User validates default call-attempt answer
- [x] User validates Atlantis Bay community-specific refusal
- [x] User validates Sierra Ridge post order priority
- [ ] User reviews changes manually
- [ ] User commits changes manually

This does not globally weaken `weak_context_distance_threshold`. It adds a separate fallback threshold only for default workflow questions.

## Phase 4C Batch Post Order Refresh + Diffing

PASSED

- [x] Add deterministic post order batch parser
- [x] Support `POST ORDER (K)`, `POST ORDER (C)`, `POST ORDER (K&C)`, `POST ORDER (K & C)`, and `POST ORDER (K and C)`
- [x] Normalize atomic rules without AI
- [x] Add SHA-256 `rule_hash`
- [x] Add stable `rule_id` and `topic_key`
- [x] Add metadata for `source_batch`, `batch_date`, `supersedes`, and `superseded_by`
- [x] Detect exact duplicates by active rule hash
- [x] Supersede same-topic active managed rules conservatively
- [x] Detect simple deterministic conflicts
- [x] Report missing active managed rules without deleting them
- [x] Generate Markdown refresh reports
- [x] Preserve lifecycle metadata in Chroma indexing
- [x] Penalize superseded/conflict/review/inactive rules in retrieval
- [ ] User validates dry run
- [ ] User validates real run
- [ ] User validates same-batch re-run duplicate behavior
- [ ] User rebuilds ChromaDB
- [ ] User validates retrieval sanity
- [ ] User reviews changes manually
- [ ] User commits changes manually

No autonomous agents, n8n rewrite, Open WebUI business logic, AI diffing, deletion of old post orders, or global lifecycle for every document type was added.

## Phase 4C1 Lifecycle Retrieval Hardening

PASSED WITH KNOWN LIMITATION

- [x] Add deterministic community alias configuration
- [x] Expand letter-prefix community aliases before semantic retrieval
- [x] Preserve lifecycle generation metadata in ChromaDB indexing
- [x] Treat lifecycle-managed post orders as operational retrieval source of truth
- [x] Skip legacy post-order lifecycle documents by default
- [x] Strengthen lifecycle status order: active, pending, review/needs_review, superseded, archived
- [x] Keep pending rules advisory and below active rules
- [x] Preserve Atlantis Bay unknown-community refusal behavior
- [x] Preserve primary workflow default fallback behavior
- [ ] User rebuilds ChromaDB
- [ ] User validates Sierra Ridge digital ID answer
- [ ] User validates Atlantis Bay refusal
- [ ] User validates default call-attempt primary workflow fallback
- [ ] User validates CBK physical ID alias retrieval
- [ ] User validates Clearbrook emergency active/pending warning
- [ ] User validates active managed docs rank above legacy review docs
- [ ] User reviews changes manually
- [ ] User commits changes manually

Known limitation:

- Sierra Ridge previously had no managed active post-order docs, so physical ID retrieval could fall back to a `qa_rule` with `status: needs_review`. Phase 4C2 addresses this by converting eligible Sierra Ridge legacy post orders into managed active post-order docs.

## Phase 4C2 Legacy Post Order Migration / Managed Source Conversion

PASSED

- [x] Add deterministic legacy post-order migration utility
- [x] Detect legacy `post_order` files missing managed lifecycle metadata
- [x] Preserve original legacy post-order files
- [x] Generate managed active post-order copies with `lifecycle_generation: managed`
- [x] Add `source_legacy_file`, `source_migration`, and `migration_date` metadata
- [x] Reuse Phase 4C normalization, hashing, topic, and rule ID helpers
- [x] Prevent duplicate managed rules by `rule_hash`
- [x] Generate migration report path under `vault/08_Reports/post-order-migration/`
- [x] Convert initial Sierra Ridge physical ID legacy post orders
- [x] Preserve migration metadata in ChromaDB indexing and API source schema
- [ ] User rebuilds ChromaDB
- [ ] User validates Sierra Ridge digital ID answer retrieves managed active post orders first
- [ ] User validates QA rules remain supporting context only
- [ ] User validates Atlantis Bay refusal still works
- [ ] User validates primary workflow fallback still works
- [ ] User reviews changes manually
- [ ] User commits changes manually

## Phase 4C3 Announcement / Reminder Lifecycle Ingestion

PASSED WITH MINOR RETRIEVAL EDGE CASE

- [x] Add deterministic announcement refresh script
- [x] Add sample announcement batch from cleaned reminder text
- [x] Parse batch metadata: `batch_date`, `source_name`, `update_type`, `default_status`
- [x] Split pasted reminder text into atomic announcement items
- [x] Classify announcement categories without AI
- [x] Extract community references from aliases and known phrases
- [x] Generate managed announcement metadata
- [x] Detect duplicate announcements by deterministic hash
- [x] Generate announcement refresh reports
- [x] Preserve announcement metadata in Chroma indexing and API schema
- [x] Keep announcements below post orders and above primary workflow
- [x] Document OCR as deferred
- [x] User runs announcement dry run manually
- [x] User runs announcement refresh manually
- [x] User rebuilds ChromaDB manually
- [x] User validates reminder retrieval manually
- [x] User validates post orders still outrank announcements manually
- [ ] User reviews changes manually
- [ ] User commits changes manually

Known minor edge case:

- `Red Zone Protocol` could be treated as a missing community hint instead of an operational topic. Phase 4D addresses this with a deterministic query intent parser.

## Phase 4D Operational Query Parser / Intent Extraction

PASSED

- [x] Add deterministic `QueryIntent` object
- [x] Add configured operational topic dictionary
- [x] Keep community extraction limited to known names, aliases, and configured synonyms
- [x] Prevent operational phrases such as `Red Zone Protocol`, `Support Room`, `Physical ID`, and `Emergency Code` from becoming fake communities
- [x] Preserve unknown-community refusal for real community-style questions such as Atlantis Bay
- [x] Extract expected document types for reminders, announcements, policies, incidents, visitor logs, default workflow, and emergency codes
- [x] Integrate query intent into CLI retrieval and answering
- [x] Preserve lifecycle scoring, authority scoring, community alias boosts, primary workflow fallback, pending advisory warnings, and citation behavior
- [x] User rebuilds ChromaDB if needed
- [x] User validates Red Zone Protocol reminder answer manually
- [x] User validates Atlantis Bay refusal manually
- [x] User validates Sierra Ridge post order priority manually
- [x] User validates default workflow fallback manually
- [ ] User reviews changes manually
- [ ] User commits changes manually

## Phase 4E OCR Intake Layer

PASSED USING PYTESSERACT FALLBACK

- [x] Add local OCR extraction script
- [x] Support single-image OCR input
- [x] Support folder OCR input
- [x] Support `png`, `jpg`, `jpeg`, and `webp`
- [x] Validate pytesseract fallback as the operational OCR backend
- [x] Document PaddleOCR as experimental/deferred
- [x] Add conservative preprocessing
- [x] Write raw OCR text artifacts
- [x] Write human-review Markdown artifacts
- [x] Include OCR engine and confidence when available
- [x] Preserve aliases during OCR cleanup without expanding them
- [x] Document that OCR cannot write to `vault/`
- [x] Document that OCR cannot trigger announcement or post-order refresh
- [x] User installs local OCR dependency manually
- [x] User runs OCR manually using pytesseract
- [x] User reviews generated OCR artifacts manually
- [x] User verifies reviewed OCR text can be copied into existing ingestion inputs
- [ ] User reviews changes manually
- [ ] User commits changes manually

Validation notes:

- PaddleOCR installed partially and model downloads succeeded, but runtime execution failed on Windows/Paddle runtime compatibility.
- PaddleOCR did not pass validation and is not the production OCR backend.
- pytesseract fallback succeeded and generated OCR review artifacts.
- The OCR architecture passed because it remains intake-only and requires human review before ingestion.

## Phase 4F OCR Review + Ingestion Bridge

PASSED / VALIDATED

- [x] Add OCR review queue folders for pending, approved, and rejected review artifacts
- [x] Add `.gitkeep` files for empty review queue folders
- [x] Add deterministic OCR review metadata fields to generated review Markdown
- [x] Default new review artifacts to `review_status: pending_review`
- [x] Default `approved_for_ingestion: false`
- [x] Default `target_ingestion_type: none`
- [x] Preserve OCR warnings about formatting, aliases, dates, times, emergency codes, gate names, and manual review
- [x] Add deterministic `automation/ocr/ocr_review_bridge.py`
- [x] Require `review_status: approved`
- [x] Require `approved_for_ingestion: true`
- [x] Require `target_ingestion_type: announcement` or `post_order`
- [x] Extract reviewed text from `## Extracted Text`
- [x] Stage reviewed text under `automation/ingestion/reviewed_ocr_inputs/`
- [x] Avoid writing to `vault/`
- [x] Avoid calling announcement or post-order ingestion scripts
- [x] Avoid ChromaDB indexing
- [x] Preserve reviewed text without summarizing or rewriting it
- [x] User manually validates refusal for missing review file
- [x] User manually validates refusal for pending or unapproved review files
- [x] User manually validates announcement staging output
- [x] User manually validates post-order staging output
- [ ] User manually runs the appropriate deterministic ingestion script if staging output is acceptable
- [ ] User manually rebuilds ChromaDB after ingestion
- [ ] User reviews changes manually
- [ ] User commits changes manually

Phase 4F workflow:

```text
image
-> OCR extraction
-> raw OCR artifact
-> review Markdown artifact
-> human review/edit
-> approved review bridge
-> reviewed OCR staging input under automation/ingestion/reviewed_ocr_inputs/
-> user manually runs existing deterministic ingestion script
-> vault Markdown
-> user manually rebuilds ChromaDB
```

No automatic OCR-to-vault ingestion, autonomous agents, AI semantic rewriting, alias expansion during OCR cleanup, ingestion-script calls, direct vault writes, artifact deletion, or ChromaDB updates were added.

## Phase 4G Temporal Expiry / Activation Engine

PASSED / VALIDATED

- [x] Add deterministic temporal lifecycle utility
- [x] Support status, lifecycle status, effective/start/active date fields, expiry/end date fields, supersede metadata, document type, and authority fields
- [x] Tolerate ISO dates and ISO datetimes
- [x] Treat invalid date formats as unknown/missing with warnings instead of crashing lifecycle evaluation
- [x] Add temporal metadata to indexed ChromaDB chunks
- [x] Preserve existing authority hierarchy and lifecycle generation behavior
- [x] Add temporal scoring so active sources are preferred and pending, not-yet-active, expired, review, unknown, superseded, and archived sources are downgraded
- [x] Expose temporal source fields through CLI/API source metadata
- [x] Add conservative answer warnings/refusal when only non-current temporal sources are retrieved
- [x] Add read-only temporal lifecycle report script under `automation/ingestion/`
- [x] Document temporal lifecycle behavior and safety boundaries
- [x] User manually rebuilds ChromaDB
- [x] User manually validates active post orders still outrank announcements and primary workflow
- [x] User manually validates expired-source warning or refusal behavior
- [x] User manually validates pending/not-yet-active warning or refusal behavior
- [x] User manually validates active source with missing temporal metadata exposes a low-priority source warning
- [x] User manually validates unknown-community refusal still works
- [x] User manually runs temporal lifecycle report and reviews grouped output
- [ ] User reviews changes manually
- [ ] User commits changes manually

Expected validation examples:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/answer_vault.py "What is the CBK rule for physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python automation/ingestion/report_temporal_lifecycle.py --expiring-soon-days 7
```

Phase 4G does not delete historical lifecycle records, rewrite source vault documents, auto-ingest OCR or staging files, bypass human review, weaken authority hierarchy, weaken unknown-community refusal, use AI semantic rewriting, introduce agents, or update ChromaDB automatically.

## Phase 4G1 Announcement Retrieval Precision Hardening

PASSED / VALIDATED

Known regression:

- `What is the Red Zone Protocol reminder?` had correct parser classification and safe refusal behavior, but vector retrieval could return nearby operational reminder chunks instead of the exact Red Zone Protocol announcement.
- Root cause was retrieval specificity, not intent parsing: reminder announcements share dense operational language, and metadata/title/category/section signals were not weighted strongly enough.

Implemented:

- [x] Preserve announcement title/topic locality in indexed chunk text
- [x] Preserve `normalized_announcement` metadata for deterministic reranking
- [x] Add deterministic reranking using exact topic phrase matches, title overlap, keyword overlap, category matches, section weighting, authority, lifecycle, and temporal state
- [x] Boost direct `Announcement` body sections for announcement questions
- [x] Penalize metadata-heavy sections such as `Operational Notes`, `Source`, and `Migration Notes` without fully excluding them
- [x] Surface optional rerank diagnostics in CLI/API source output
- [x] Preserve safe refusal thresholds and unknown-community refusal behavior
- [x] Preserve `post_order > announcement > primary_workflow`
- [x] User manually rebuilds ChromaDB
- [x] User manually validates Red Zone Protocol announcement precision
- [x] User manually validates Pickleball Tournament, NVR reminder, and Support Room reminder precision
- [x] User manually validates post orders still outrank announcements
- [x] User manually validates Atlantis Bay refusal still works
- [ ] User reviews changes manually
- [ ] User commits changes manually

Phase 4G1 does not add LLM reranking, AI semantic rewriting, autonomous retrieval agents, vault rewrites, automatic ingestion, automatic ChromaDB updates, global threshold weakening, or announcement override behavior.

## Phase 4J-lite Operational Dashboard / Shift Briefing

PASSED / VALIDATED

- [x] Add read-only FastAPI dashboard routes under `/dashboard`
- [x] Add `/dashboard/status`
- [x] Add `/dashboard/summary`
- [x] Add `/dashboard/briefing`
- [x] Add `/dashboard/announcements`
- [x] Add `/dashboard/post-orders`
- [x] Add `/dashboard/issues`
- [x] Add deterministic briefing sections for temporary protocols, gate/NVR/kiosk issues, active events, operational reminders, expiring-soon notices, community alerts, and QA/compliance warnings
- [x] Add deterministic priority scoring from authority, temporal state, expiring-soon dates, category, issue keywords, and community specificity
- [x] Add optional community filtering using existing alias logic
- [x] Preserve source file, authority, type, lifecycle status, temporal state, effective date, and expiry date per dashboard item
- [x] Add optional read-only CLI briefing preview
- [x] Preserve dashboard as visibility only, not operational memory
- [x] User manually validates dashboard API routes
- [x] User manually validates community filtering
- [x] User manually validates briefing grouping and ordering
- [x] User manually validates dashboard does not mutate vault or ChromaDB
- [ ] User reviews changes manually
- [ ] User commits changes manually

Phase 4J-lite does not auto-ingest OCR, update vault memory, bypass human review, weaken safe refusal, hallucinate operational guidance, override authority hierarchy, create autonomous workflows, add background mutation tasks, add browser automation agents, or generate operational memory.

## Phase UX-1 User Workflow & OpenWebUI Usability Pass

PASSED / VALIDATED

- [x] Change dashboard deduplication from `(source_file, section)` to `(source_file, title)`
- [x] Exclude dashboard items from `vault/08_Reports/`
- [x] Exclude dashboard items from `vault/07_Visitor_Logs/`
- [x] Exclude dashboard items from `vault/06_Incidents/`
- [x] Exclude dashboard items from `vault/01_Daily_Briefings/`
- [x] Preserve dashboard scoring, grouping, filtering, source metadata, authority metadata, lifecycle status, and temporal state behavior
- [x] Expand `rag/config/community_aliases.json` to the full current virtual community alias table
- [x] Correct aliases such as `CBKN`, `PBM`, and `PLM` to match the authoritative letter-only alias list
- [x] Add `openwebui/USAGE_GUIDE.md` as a practical VA operator shift reference
- [x] Document Open WebUI prompt patterns, citations, safe refusals, low-confidence warnings, shift-start workflow, dashboard briefing usage, and operator boundaries
- [x] Update `README.md` with the current validated state, dashboard endpoint guidance, Open WebUI usage guide reference, and full alias-table note
- [x] Update `docs/AI_HANDOFF.md` with UX-1 implementation status and next-step guidance
- [x] User manually validates dashboard deduplication
- [x] User manually validates dashboard source-prefix exclusions
- [x] User manually validates expanded alias behavior
- [x] User reviews Open WebUI guide manually
- [ ] User reviews changes manually
- [ ] User commits changes manually

Phase UX-1 does not add new operational memory, ingestion pipelines, authority layers, agents, autonomous behavior, AI semantic rewriting, automatic vault writes, automatic ChromaDB updates, or any weakening of safe refusal. The authority hierarchy remains `post_order > announcement > primary_workflow`.

## Phase 4I-lite Text Ingestion via Open WebUI Slash Commands [4.8.2-stable]

PASSED / VALIDATED

### 4.8.1-stable Patch Notes

- Fixed top_k ceiling: added requested_all detection and effective_top_k=25 override
- Fixed community name matching: added longest-first full name lookup from aliases.json
- Validated and promoted to 4.8.1-stable on 2026-05-17

### Validation Record - 4.8.1-stable

Validated: 2026-05-17
Validator: manual (user)
Result: PASSED - all 11 validation checks passed

Validation summary:
- /post-orders preview: 13 HPS rules and 10 GLEN rules parsed correctly
- YES confirmation: vault written, ChromaDB rebuilt, ingestion complete
- NO cancellation: nothing written to vault
- Unrecognized community: error returned with alias list
- Missing community: usage instructions returned
- top_k override: complete HPS kiosk list returned 10 active rules (was 4)
- Full name matching: Heritage Palms South and The Glen resolved by full name
- Normal query top_k: not affected by override
- Community isolation: Glen rules returned no HPS bleed
- Versioning: confirmed in all four documentation locations
- Vault integrity: no unintended mutations

Known remaining items (non-blocking, future improvement):
- /announcements command not yet validated end-to-end with confirmed YES
- Res Confirmation alert rule flagged as review-status in CBK vault (not a bug - correct lifecycle behavior)

## Patch 4.8.2 — DATE_PATTERN Word Boundary Fix

Version: 4.8.2-stable
Date: 2026-05-17
Phase: Phase 4I-lite

### Root Cause
DATE_PATTERN used \b word boundary anchors. The \b assertion fails when a
date string is immediately followed by a capital letter with no whitespace
(e.g. "5/17/2026Post Order"). Python treats digit-to-letter as \w-to-\w,
so no word boundary fires. Result: zero date matches, zero rules parsed,
and the "No post order rules were parsed" error was returned to the operator
even on valid input.

### Fix Applied
- api/ingest.py DATE_PATTERN: replaced \b anchors with negative digit
  lookbehind (?<!\d) and lookahead (?!\d) to prevent matching inside longer
  number strings while correctly matching dates that run into letters.
- api/ingest.py POST_ORDER_LABEL_PATTERN: added \s* inside the type
  parentheses to handle all spacing variants: (K & C), (K&C), (KC), (K), (C).

### Validation Record
- [x] DATE_PATTERN regex updated correctly in api/ingest.py
- [x] /post-orders SR [no-space input] returns preview (not error)
- [x] 2 rules parsed from 2-rule compact input
- [x] Rule text extracted correctly for K and C types
- [x] NO cancels cleanly, nothing written to vault
Validated: 2026-05-17

- [x] Add `api/ingest.py` for guarded slash command ingestion state and handlers
- [x] Add `/post-orders` command detection through `/ask`
- [x] Add `/announcements` command detection through `/ask`
- [x] Resolve community aliases and configured full community names deterministically
- [x] Return plain-text usage errors for missing community or missing pasted text
- [x] Return plain-text unrecognized-community errors with valid alias examples
- [x] Parse post order text deterministically from dated `Post Order (K/C/K&C)` entries
- [x] Normalize post order type markers to `K`, `C`, or `KC`
- [x] Generate post order preview before any vault write
- [x] Parse announcement text deterministically from blocks or numbered items
- [x] Infer announcement category from fixed keyword rules
- [x] Generate announcement preview before any vault write
- [x] Store one pending ingestion state in memory with a 5-minute expiry
- [x] Route `YES` confirmation before normal RAG answering
- [x] Route `NO` cancellation before normal RAG answering
- [x] Call `refresh_post_orders.py` only after `YES` for post order pending state
- [x] Call `refresh_announcements.py` only after `YES` for announcement pending state
- [x] Call `rag/scripts/index_vault.py` after successful ingestion
- [x] Avoid calling `reset_chroma.py`
- [x] Delete temporary batch file after successful ingestion and rebuild
- [x] Add `openwebui/INGEST_COMMANDS.md` operator guide with supported aliases and worked examples
- [x] Update README and AI handoff for 4I-lite status
- [x] User manually validates `/post-orders` preview flow
- [x] User manually validates `/announcements` preview flow
- [x] User manually validates `YES` ingestion flow
- [x] User manually validates `NO` cancellation flow
- [x] User manually validates normal RAG `/ask` behavior remains unchanged
- [x] User reviews changes manually
- [x] User commits changes manually

Phase 4I-lite does not add OCR or image upload, autonomous ingestion, AI parsing or rewriting, new authority layers, new document types, retrieval changes, dashboard changes, direct vault writes before confirmation, or announcement override behavior. The authority hierarchy remains `post_order > announcement > primary_workflow`.

## Deferred

- Open WebUI-hosted retrieval, memory, agents, or direct vault access
- n8n RAG integration
- autonomous agents
- Git auto-commit
- additional dashboard features beyond the validated read-only dashboard
- voice/UI
- Phase 4B chat modes
- Phase 4C continuous ingestion
- Phase 4 automations

## Ready For Final Project Completion

NO
