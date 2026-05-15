# AI Handoff

## Current Phase

PHASE 3E OPEN WEBUI INTEGRATION. Phase 2 Minimal POW, Phase 3A Retrieval POW, Phase 3B Grounded Answering POW, Phase 3C RAG Quality Hardening, and Phase 3D Local API Wrapper are validated and passed.

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
- Do not add autonomous agents, advanced memory systems, automatic memory editing, or dashboards.
- Do not use cloud embeddings.
- Do not expand Phase 3B beyond retrieved-context answer generation.
- Do not commit secrets, real API keys, `.env`, `n8n_data`, or generated credential files.

## Recommended Next Phase

PHASE 3C - RAG QUALITY HARDENING

Focus on dedupe improvement, citation cleanup, section reranking, title/filename compression, answer citation alignment, and stronger insufficient-context filtering.

After Phase 3C, Phase 3D added FastAPI access and Phase 3E documents Open WebUI as a presentation-only client.

## Phase 3C In Progress

Current Phase 3C changes are intentionally narrow:

- stronger near-duplicate suppression;
- section and metadata reranking;
- deterministic community/type hints;
- conservative insufficient-context refusal;
- cleaner answer citation reporting.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 3D In Progress

Phase 3D adds a local FastAPI wrapper only:

- `api/main.py`
- `api/schemas.py`
- `api/service.py`
- `api/README.md`

The `/ask` endpoint wraps the existing `rag/scripts/answer_vault.py` logic. It does not add Open WebUI, n8n changes, agents, memory editing, or Git automation.

The user will manually review and commit. Do not run `git commit` or `git push`.

## Phase 3E In Progress

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
