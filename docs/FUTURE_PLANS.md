# Future Plans

This file is the living backlog for SafePassage Second Brain.
Completed items are struck through. Every phase should update this file —
cross off completed items and add new ideas as they arise.

Last updated: 2026-05-19
Current stable version: 4.20.0-alpha

---

## Completed

- ~~Phase 4.19.0 — operational trust query/answer audit log~~
- ~~Patch 4.18.3 — restore clean CLI citation display ([Source N] regex fix)~~
- ~~Phase 4.18.0 — Community-aware kiosk call flow synthesis (SOP enrichment + call flow routing + merged output)~~
- ~~Phase 4.13.4 — Fix double sources display in CLI output~~
- ~~Phase 4.14.0 — Incremental indexing (`--files` flag on index_vault.py)~~
- ~~Phase 4.15.0 — Streaming response (`/ask/stream` SSE endpoint + Open WebUI pipe)~~
- ~~Phase 4.16.0 — Conflict detection + multi-turn wizard UX for `/post-orders`~~
- ~~Phase 4.17.0 — Quick reply hints in Open WebUI pipe + FUTURE_PLANS.md introduced~~

---

## In Progress

- Phase 4.20.0 — model preloading + audit log source deduplication

---

## Planned

### Phase 4.21.0 — Handoff Readiness

Priority: Handoff readiness (P3)

Make the repository understandable and operable by someone other
than the original developer.

Scope:
- Architecture diagram (Mermaid) in docs/ showing the full data
  flow: vault → indexer → ChromaDB → answer_vault → service → pipe
- Formal vault schema documentation: every frontmatter field defined
  with type, required/optional, valid values, and authority hierarchy
- Onboarding guide: setup steps, environment variables, how to
  ingest new post orders, how to validate, how to deploy
- Session log automation: Python script that reads git log for the
  current day and PHASE_LOG.md validation records, then generates a
  SESSION_LOG draft file — reduces manual session checkpoint effort

Files to change:
- docs/ARCHITECTURE.md (new)
- docs/VAULT_SCHEMA.md (new)
- docs/ONBOARDING.md (new)
- automation/generate_session_log.py (new)
- docs (all four versioning locations + FUTURE_PLANS.md)
- api/version.py

---

### Phase 4.22.0 — Architecture Safety: Separation of Concerns

Priority: Architecture safety (P4)

Address the main architectural smell identified in external senior
engineering review: services acting multiple roles with no clear
domain boundaries.

Scope:
- Separate ingestion from querying in api/service.py. The file
  currently owns wizard state, conflict detection, ingestion routing,
  retrieval routing, answer formatting, and community resolution.
  Extract ingestion orchestration into api/ingest_service.py and
  retrieval/answer into api/query_service.py.
- Extract retrieval pipeline from rag/scripts/answer_vault.py monolith.
  answer_vault.py currently handles retrieval, reranking, context
  assembly, prompt building, model calling, citation parsing, and
  source formatting. Extract into focused modules:
  rag/retrieval.py (retrieve_chunks, rerank),
  rag/context.py (build_context_packet),
  rag/answer.py (call_deepseek, strip_sources, cited_source_ids).
- Formalize vault frontmatter metadata model with Pydantic. Add
  validation at ingest time so malformed frontmatter raises a clear
  error rather than silently producing wrong retrieval results.

Files to change:
- api/service.py (reduced)
- api/query_service.py (new)
- api/ingest_service.py (new)
- rag/retrieval.py (new, extracted from answer_vault.py)
- rag/context.py (new, extracted)
- rag/answer.py (new, extracted)
- rag/scripts/answer_vault.py (reduced to orchestration only)
- rag/vault_schema.py (new Pydantic models)
- docs (all four versioning locations + FUTURE_PLANS.md)
- api/version.py

Note: This phase requires careful incremental extraction with full
regression testing after each file move. Do not do as a single
big-bang rewrite.

---

### Phase 4.23.0 — Developer Scalability: Retrieval Correctness Tests

Priority: Developer scalability (P5)

Add automated tests around retrieval correctness — the highest-risk
behavior in the system since wrong answers directly influence VA
access decisions.

Scope:
- Retrieval correctness test suite: assert that known queries return
  expected sources, expected confidence levels, and expected
  community resolution. Tests run against the live ChromaDB index.
- Refuse/weak confidence tests: assert that queries with no meaningful
  vault match return weak or none confidence and do not give
  confident AI answers. Addresses the 4.19.0 validation observation
  where a nonsense query ("xyzzy unknown community gate protocol")
  returned strong confidence and a full AI answer.
- Community resolution tests: assert that community alias resolution
  works correctly for known aliases (SIERRA → Sierra Ridge,
  GLEN → The Glen (Tamiment), etc.).
- CI pipeline: basic GitHub Actions workflow that runs tests on push
  to master.

Tracked from 4.19.0 validation:
- xyzzy nonsense query returned [AI] at strong confidence instead of
  refusing. Fix: add retrieval correctness threshold test that asserts
  queries with no relevant vault content return confidence=weak or
  confidence=none. If the model currently scores nonsense queries as
  strong, adjust the confidence threshold or add a minimum semantic
  similarity floor before allowing AI answer generation.

Files to change:
- tests/ (new directory)
- tests/test_retrieval_correctness.py (new)
- tests/test_community_resolution.py (new)
- tests/test_confidence_thresholds.py (new)
- .github/workflows/ci.yml (new)
- docs (all four versioning locations + FUTURE_PLANS.md)
- api/version.py

---

## Discarded / Won't Do

- Native Open WebUI form input fields (investigated, not possible)
  Open WebUI pipe responses cannot inject custom HTML input elements into the
  chat thread. The pipe can only yield text/markdown. Replaced by the
  multi-turn wizard UX in Phase 4.16.0.

---

## Notes for Future Sessions

When picking up this project in a new session:
1. Read docs/AI_HANDOFF.md first — it has the current version, phase, and
   recommended next step.
2. Check this file for what's planned next.
3. Cross off completed items in this file as part of every post-validation
   documentation prompt.
4. Add new ideas here during the session — don't lose them to chat history.
