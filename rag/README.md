# Phase 3 Local RAG Proof of Work

Current status: WORKING PROOF OF WORK

- Phase 3A retrieval works.
- Phase 3B grounded answering works.
- Phase 3D local API wrapper is available for HTTP access.
- Phase 3E documents Open WebUI as a presentation-only UI over FastAPI.

Phase 3A tests whether local semantic search can retrieve the right Markdown chunks from `vault/`.

Phase 3B adds minimal grounded answer generation using only retrieved vault chunks.

This does not add Open WebUI-hosted retrieval, n8n integration, agents, automatic memory editing, Git automation, dashboards, or Phase 4 automations.

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
