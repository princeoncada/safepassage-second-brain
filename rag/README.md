# Phase 3 Local RAG Proof of Work

Current status: WORKING PROOF OF WORK

- Phase 3A retrieval works.
- Phase 3B grounded answering works.
- Phase 3D local API wrapper is available for HTTP access.
- Phase 3E documents Open WebUI as a presentation-only UI over FastAPI.
- Phase 4D adds deterministic query intent parsing before retrieval.
- Phase 4E adds OCR intake artifacts before reviewed ingestion.
- Phase 4F adds a reviewed OCR staging bridge before manual deterministic ingestion.
- Phase 4G adds deterministic temporal expiry and activation metadata for lifecycle-aware retrieval.
- Phase 4G1 adds deterministic announcement retrieval precision hardening.
- Phase 4J-lite adds read-only operational dashboard and shift briefing endpoints.

Phase 3A tests whether local semantic search can retrieve the right Markdown chunks from `vault/`.

Phase 3B adds minimal grounded answer generation using only retrieved vault chunks.

This does not add Open WebUI-hosted retrieval, n8n integration, agents, automatic memory editing, Git automation, dashboards, or Phase 4 automations.

Phase 4E OCR output is not indexed directly. Phase 4F can stage human-approved reviewed OCR text under `automation/ingestion/reviewed_ocr_inputs/`, but this is not ingestion. The user must still run the existing deterministic ingestion scripts manually before Markdown enters `vault/` and ChromaDB is rebuilt.

## Query Intent Parsing

Phase 4D parses operational questions before semantic retrieval.

The parser extracts:

- known community names and letter-code aliases;
- missing community hints only when the query clearly asks about an unknown community;
- operational topics such as `Red Zone Protocol`, `Emergency Code`, `Physical ID`, `Support Room`, and `Pickleball Tournament`;
- expected document types such as `announcement`, `post_order`, `qa_rule`, `incident`, `visitor_log`, and primary workflow fallback;
- default/global workflow intent.

This prevents global operational topics from being treated as fake communities while keeping Atlantis Bay-style unknown-community refusal behavior conservative. The parser is deterministic and does not use an LLM.

## Temporal Lifecycle Metadata

Phase 4G evaluates temporal lifecycle metadata deterministically during indexing and retrieval.

Supported frontmatter fields include:

```text
status
lifecycle_status
effective_date
active_from
start_date
expires_at
expiry_date
active_until
end_date
expires_on
superseded_by
supersedes
lifecycle_generation
authority_level
document_type
type
```

Indexed chunks may include optional source metadata:

```text
temporal_state
temporal_warning
temporal_start_date
temporal_start_field
temporal_end_date
temporal_end_field
```

Temporal states are `active`, `pending`, `not_yet_active`, `expired`, `superseded`, `archived`, `review`, and `unknown`. Retrieval prefers active temporal sources and downgrades non-current or uncertain sources without changing source Markdown. If only expired, pending, or not-yet-active sources are retrieved, answering is conservative and may refuse instead of presenting stale or future-dated material as current policy.

Generate a read-only report:

```powershell
python automation/ingestion/report_temporal_lifecycle.py --expiring-soon-days 7
```

Reports are written under `vault/08_Reports/temporal-lifecycle/` and do not update ChromaDB or operational memory.

## Retrieval Reranking

Phase 4G1 adds deterministic reranking after vector retrieval.

The final retrieval order is influenced by:

- vector distance from ChromaDB;
- deterministic query intent, including community and topic terms;
- authority hierarchy: `post_order > announcement > primary_workflow`;
- lifecycle and temporal state;
- exact topic phrase matches in title, normalized announcement text, or chunk body;
- title and keyword overlap;
- category match;
- section weighting.

Announcement chunks include title, category, and normalized announcement topic text in the embedded chunk and metadata. This reduces mixed-reminder retrieval pollution for questions such as `What is the Red Zone Protocol reminder?`.

For direct operational questions, `Announcement`, `Rule`, `Agent Action`, `Policy`, `Summary`, and `Details` sections are preferred. Metadata-heavy sections such as `Operational Notes`, `Source`, `Migration Notes`, `Change History`, `Open Questions`, and `Source Input` are penalized but not fully excluded when available.

Optional source diagnostics may include:

```text
rerank_score
rerank_delta
rerank_reasons
```

These fields explain deterministic scoring and are not operational policy. Safe refusal behavior remains conservative when context is still weak.

## Dashboard / Shift Briefing

Phase 4J-lite adds a read-only dashboard layer over indexed memory.

FastAPI routes:

```text
GET /dashboard/status
GET /dashboard/summary
GET /dashboard/briefing
GET /dashboard/announcements
GET /dashboard/post-orders
GET /dashboard/issues
```

Optional community filtering:

```text
/dashboard/briefing?community=CBK
/dashboard/briefing?community=Sierra Ridge
```

The dashboard groups operational memory into deterministic briefing sections:

- Active Temporary Protocols
- Gate / NVR / Kiosk Issues
- Active Events
- Important Operational Reminders
- Expiring Soon
- Community-Specific Alerts
- QA / Compliance Warnings

Each item preserves title, category, community, authority level, document type, lifecycle status, temporal state, effective/expiry dates, section, source file, and preview text.

Preview from CLI without mutating memory:

```powershell
python automation/dashboard/preview_briefing.py --community CBK
```

The dashboard reads the existing ChromaDB index only. It does not write to `vault/`, run ingestion scripts, update ChromaDB, generate operational memory, or bypass source authority.

## Install

```powershell
pip install -r rag/requirements.txt
```

## Index

```powershell
python rag/scripts/index_vault.py
```

This reads Markdown from `vault/`, skips `vault/99_Archive` by default, chunks documents by Markdown section, embeds chunks with `sentence-transformers/all-MiniLM-L6-v2`, and stores them in local ChromaDB under `rag/chroma/`.

## Query

```powershell
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?"
```

The query script prints retrieved chunks only.

## Answer

Set the DeepSeek key:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Run grounded answer generation:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Validate retrieval without AI:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

Answers must cite retrieved source files and sections. If context is insufficient, the answer should say the vault does not contain enough information to answer safely.

## Reset

```powershell
python rag/scripts/reset_chroma.py --yes
```

The ChromaDB index is disposable. Rebuild it any time from the Markdown vault.

## Validated Results

Indexing:

```text
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

Retrieval passed for:

```text
overnight visitors must present physical ID before access
What happened with tailgating at Monterey?
What should the agent do if digital ID is presented instead of physical ID?
```

Answering passed for:

```text
What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?
What happened with tailgating at Monterey?
What are Sierra Ridge overnight visitor ID rules?
What is the vehicle policy for Atlantis Bay?
```

The first three answer from retrieved context. Atlantis Bay refuses with insufficient context.

## Known Issues / Next Refinements

These are not blockers.

1. Duplicate source files still appear in retrieval results.
2. Citations can still be incomplete if DeepSeek omits explicit source IDs.
3. Retrieval ranking remains heuristic and depends on available Markdown quality.
4. Source numbering depends on the model citing retrieved source IDs exactly.
5. Titles and filenames are too verbose.
6. Incident documents need richer structured fields.
7. Open Questions may contain generic AI filler.
8. Git auto-commit remains deferred.

Recommended next phase after Phase 3E: keep Open WebUI presentation-only and validate the UI connection before considering any Phase 4 automation.

## Phase 3C Hardening

Phase 3C hardens quality without adding major features:

- near-duplicate chunk reduction;
- community/type query hints;
- section reranking;
- stronger insufficient-context refusal;
- cleaner answer citation output.

Validation:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

## Phase 4C2 Legacy Post Order Migration

Phase 4C2 converts eligible legacy freeform post orders into managed active post-order copies.

```powershell
python automation/ingestion/migrate_legacy_post_orders.py --dry-run
python automation/ingestion/migrate_legacy_post_orders.py
```

The script only targets `type: post_order` legacy files. It does not migrate QA rules into post orders and does not delete old files.

Generated managed migration docs include:

- `lifecycle_generation: managed`
- `status: active`
- `rule_id`
- `rule_hash`
- `source_legacy_file`
- `source_migration: legacy_post_order`
- `migration_date`

After migration, rebuild ChromaDB from Markdown so managed post-order copies can become the operational retrieval source of truth.

## Phase 4C3 Announcement Lifecycle Ingestion

Phase 4C3 ingests cleaned pasted reminder text into managed announcement documents.

```powershell
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md --dry-run
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md
```

Announcements use:

- `type: announcement`
- `authority_level: announcement`
- `lifecycle_generation: managed`
- `announcement_id`
- `announcement_hash`
- `category`
- `status`
- `expires_on` when detected

Announcements sit between post orders and primary workflow:

```text
post_order > announcement > primary_workflow
```

OCR is not included in Phase 4C3. The script expects cleaned pasted text.

Details: `rag/docs/PHASE_3C_RAG_QUALITY_HARDENING.md`.

## Phase 3D Local API

Start the local FastAPI wrapper:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Ask through HTTP:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?",
    "top_k":5
  }'
```

Retrieval-only:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What are Sierra Ridge overnight visitor ID rules?",
    "top_k":5,
    "no_ai":true,
    "show_context":true
  }'
```

The API is only a local interface wrapper. Markdown remains the source of truth and ChromaDB remains rebuildable derived data.

## Phase 3E Open WebUI

Open WebUI should call the local FastAPI endpoint:

```text
POST http://localhost:8000/ask
```

If Open WebUI runs in Docker and FastAPI runs on the host, use:

```text
POST http://host.docker.internal:8000/ask
```

Open WebUI is only the conversational UI. It should display the `answer`, `answer_citations`, `retrieval_confidence`, `confidence_reason`, `sources`, and `warnings` returned by FastAPI. It should not call ChromaDB directly, write Markdown, edit memory, or bypass the refusal behavior.

Details: `openwebui/README.md`.

## Phase 4A Retrieval Quality Hardening

Phase 4A improves retrieval and citation quality without changing the architecture.

What changed:

- section weighting now prefers `Agent Action`, `Summary`, `Details`, `Rule`, `Policy`, then `QA Notes`;
- low-value sections remain excluded by default and penalized when explicitly included;
- dedupe happens after reranking so the strongest near-duplicate source is kept;
- duplicate detection uses normalized title, community, type, section, content preview, and lightweight content similarity;
- generated answer text is cleaned so API/UI clients render only one Sources section;
- `answer_citations` contains only source IDs explicitly cited by the generated answer.

Validation:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Known limitations:

- retrieval quality still depends on Markdown quality;
- generated test files can still pollute results if they are meaningfully different;
- section weighting is heuristic;
- refusal behavior remains conservative by design;
- no agents, automatic vault cleanup, or Phase 4B chat modes are included.

## Phase 4B Primary Workflow Ingestion

Phase 4B adds global base kiosk workflow content as fallback authority.

Authority hierarchy:

```text
post_order
announcement
primary_workflow
```

Primary workflow is default guidance only. It should not override post orders or announcements.

Ingest the structured sample:

```powershell
python automation/ingestion/ingest_primary_workflow.py
```

Then rebuild the index:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Validate:

```powershell
python rag/scripts/query_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident for Atlantis Bay?" --top-k 5
```

Expected:

- default workflow questions can retrieve `primary-*.md`;
- answers from primary workflow say they are based on default or primary workflow guidance;
- Sierra Ridge post order and QA rule sources still outrank primary workflow;
- unknown communities are not hallucinated as community-specific policy.

Details: `docs/PHASE_4B_PRIMARY_WORKFLOW_INGESTION.md`.

## Phase 4B2 Primary Workflow Fallback Confidence

Phase 4B2 adds a separate fallback threshold for explicit default workflow questions:

```json
"primary_workflow_default_threshold": 1.1
```

This allows a global primary workflow source to answer when it is slightly above the normal weak-context threshold, but only for default/base/primary workflow queries.

Validation:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident for Atlantis Bay?" --top-k 5
```

Expected:

- default query can answer from `primary-call-attempts-by-community.md`;
- Atlantis Bay community-specific query still refuses if no Atlantis Bay source exists.

## Phase 4C Post Order Refresh

Phase 4C adds deterministic batch refresh for highest-authority post orders.

Dry run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
```

Real run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Then rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Indexing preserves `rule_id`, `rule_hash`, `source_batch`, `supersedes`, and `superseded_by`. Retrieval boosts active rules and penalizes `superseded`, `conflict`, `review`, and `inactive` rules.

Details: `docs/PHASE_4C_POST_ORDER_REFRESH_DIFFING.md`.

## Phase 4C1 Lifecycle Retrieval Hardening

Phase 4C1 strengthens retrieval now that post-order lifecycle metadata exists.

Lifecycle priority:

```text
active
pending
review / needs_review
superseded
archived
```

Active managed post orders are the operational retrieval source of truth. Pending rules are advisory and should trigger a warning when relevant. Legacy freeform post-order documents are skipped by default instead of deleted.

Community aliases live in:

```text
rag/config/community_aliases.json
```

Examples:

```text
CBK -> Clearbrook Main
SR -> Sierra Ridge
MON -> Monterey
OPB -> Old Pelican Bay
```

Numeric client-code portions are ignored. Alias expansion happens before semantic retrieval so community metadata can be boosted deterministically.

Validation:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/answer_vault.py "What is the CBK rule for physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the emergency code for Clearbrook Main?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```
