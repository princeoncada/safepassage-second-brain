# Phase Log

## Current Phase

PHASE 4G TEMPORAL EXPIRY / ACTIVATION ENGINE

## Overall System Status

WORKING PROOF OF WORK

The final project is not complete. The current validated checkpoint proves local ingestion, retrieval, grounded answering, local API access, Open WebUI presentation integration, Phase 4A retrieval hardening, Phase 4B primary workflow ingestion, Phase 4B2 fallback confidence, Phase 4C batch post order refresh/diffing, Phase 4C1 lifecycle retrieval hardening, Phase 4C2 legacy post-order managed conversion, Phase 4C3 announcement lifecycle ingestion, Phase 4D query intent parsing, Phase 4E OCR intake using pytesseract fallback, and Phase 4F OCR review + ingestion bridge. Phase 4G implementation adds deterministic temporal expiry and activation awareness and is awaiting manual validation.

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

Manually validate Phase 4G Temporal Expiry / Activation Engine.

Scope:

- rebuild ChromaDB manually so indexed chunks include temporal metadata;
- validate active post orders still outrank announcements and primary workflow;
- validate expired, pending, not-yet-active, superseded, archived, review, and unknown-temporal records are downgraded or warned;
- validate unknown-community refusal still works;
- generate the temporal lifecycle report manually and inspect it under `vault/08_Reports/temporal-lifecycle/`;
- confirm the report is review output only and does not update ChromaDB or operational source documents.

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

IMPLEMENTATION ADDED, MANUAL VALIDATION PENDING

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
- [ ] User manually rebuilds ChromaDB
- [ ] User manually validates active post orders still outrank announcements and primary workflow
- [ ] User manually validates expired-source warning or refusal behavior
- [ ] User manually validates pending/not-yet-active warning or refusal behavior
- [ ] User manually validates active source with missing temporal metadata exposes a low-priority source warning
- [ ] User manually validates unknown-community refusal still works
- [ ] User manually runs temporal lifecycle report and reviews grouped output
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

## Deferred

- Open WebUI-hosted retrieval, memory, agents, or direct vault access
- n8n RAG integration
- autonomous agents
- Git auto-commit
- dashboards
- voice/UI
- Phase 4B chat modes
- Phase 4C continuous ingestion
- Phase 4 automations

## Ready For Final Project Completion

NO
