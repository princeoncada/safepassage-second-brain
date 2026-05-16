# Phase Log

## Current Phase

PHASE 4B2 PRIMARY WORKFLOW FALLBACK CONFIDENCE FIX

## Overall System Status

WORKING PROOF OF WORK

The final project is not complete. The current validated checkpoint proves local ingestion, retrieval, grounded answering, local API access, Open WebUI presentation integration, Phase 4A retrieval hardening, and Phase 4B primary workflow ingestion. Phase 4B2 narrows primary workflow fallback confidence so default/base workflow answers can pass without weakening unknown-community refusals.

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

Finish Phase 3E validation in Open WebUI.

Scope:

- configure Open WebUI to call the local FastAPI `/ask` endpoint;
- validate grounded answers and citations in the UI;
- validate Atlantis Bay insufficient-context refusal;
- keep Open WebUI presentation-only.

After Phase 3E validation, consider the next hardening or integration phase. Do not jump to agents, direct vault editing, or Phase 4 automations without an explicit phase request.

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

IN PROGRESS

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

IN PROGRESS

- [x] Add configurable `primary_workflow_default_threshold`
- [x] Allow fallback confidence only for explicit default/base/primary workflow queries
- [x] Require global `authority_level: primary_workflow` context for fallback confidence
- [x] Keep unknown community-specific questions on the conservative refusal path
- [x] Preserve `post_order > announcement > primary_workflow`
- [x] Preserve API response compatibility
- [ ] User validates default call-attempt answer
- [ ] User validates Atlantis Bay community-specific refusal
- [ ] User validates Sierra Ridge post order priority
- [ ] User reviews changes manually
- [ ] User commits changes manually

This does not globally weaken `weak_context_distance_threshold`. It adds a separate fallback threshold only for default workflow questions.

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
