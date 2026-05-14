# AI Handoff

## Current Phase

PHASE 2 - STRUCTURED INGESTION is in progress.

## What Exists

- Phase 1 vault folders, templates, docs, Docker Compose, n8n setup, and schema standards.
- Phase 2 prompt chain for classification, routing, normalization, and QA risk checking.
- Phase 2 ingestion contract and routing rules.
- Sample inputs and expected outputs for test-driven workflow buildout.
- n8n workflow documentation for manual implementation.

## Continue From Here

Future AI work should:

1. Keep `master` as the official branch.
2. Preserve Markdown in `vault/` as the source of truth.
3. Use `automation/ingestion/ingestion_contract.json` as the canonical payload contract.
4. Use `automation/ingestion/routing_rules.json` for folder routing.
5. Keep prompts modular.
6. Add or refine samples when document type behavior changes.
7. Keep `docs/PHASE_LOG.md` accurate.

## Do Not Do Yet

- Do not implement ChromaDB.
- Do not implement RAG.
- Do not implement Open WebUI.
- Do not add advanced automations beyond the documented Phase 2 ingestion workflow.
- Do not commit secrets, real API keys, `.env`, `n8n_data`, or generated credential files.

## Phase 2 Exit Criteria

Phase 2 should only be marked complete after:

- n8n workflow is built or exported.
- Sample inputs are run through the prompt chain.
- Generated Markdown is inspected for metadata completeness.
- Routing rules are verified against every supported document type.
- QA risk review behavior is tested.
- Git commit behavior is tested on `master`.

Until then, Phase 2 must remain `IN PROGRESS`.
