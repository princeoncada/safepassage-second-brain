# Future Plans

This file is the living backlog for SafePassage Second Brain.
Completed items are struck through. Every phase should update this file -
cross off completed items and add new ideas as they arise.

Last updated: 2026-05-20
Current stable version: 4.22.0-stable
Current working version: 4.23.0-alpha

---

## Completed

- ~~Phase 4.22.0 - Architecture Safety: Separation of Concerns~~
- ~~Phase 4.21.0 - Handoff Readiness~~
- ~~Phase 4.20.0 - model preloading + audit log source deduplication~~
- ~~Phase 4.19.0 - operational trust query/answer audit log~~
- ~~Patch 4.18.3 - restore clean CLI citation display ([Source N] regex fix)~~
- ~~Phase 4.18.0 - Community-aware kiosk call flow synthesis (SOP enrichment + call flow routing + merged output)~~
- ~~Phase 4.13.4 - Fix double sources display in CLI output~~
- ~~Phase 4.14.0 - Incremental indexing (`--files` flag on index_vault.py)~~
- ~~Phase 4.15.0 - Streaming response (`/ask/stream` SSE endpoint + Open WebUI pipe)~~
- ~~Phase 4.16.0 - Conflict detection + multi-turn wizard UX for `/post-orders`~~
- ~~Phase 4.17.0 - Quick reply hints in Open WebUI pipe + FUTURE_PLANS.md introduced~~

---

## In Progress

### Phase 4.23.0 - Developer Scalability: Retrieval Correctness Tests

Priority: Developer scalability (P5)

Add automated tests around retrieval correctness - the highest-risk
behavior in the system since wrong answers directly influence VA
access decisions.

Scope:
- Retrieval correctness test suite: assert that known queries return
  expected sources, expected confidence levels, and expected community
  resolution. Tests run against the live ChromaDB index.
- Refuse/weak confidence tests: assert that queries with no meaningful
  vault match return weak or none confidence and do not give confident
  AI answers.
- Community resolution tests: assert that community alias resolution
  works correctly for known aliases (SIERRA -> Sierra Ridge,
  GLEN -> The Glen (Tamiment), etc.).
- CI pipeline: basic GitHub Actions workflow that runs tests on push
  to master.

Tracked from 4.19.0 validation:
- xyzzy nonsense query returned [AI] at strong confidence instead of
  refusing. Resolved in 4.23.0-alpha with
  `minimum_raw_distance_floor` in `rag/retrieval.py` and
  `rag/config/retrieval_config.json`.

Files to change:
- rag/retrieval.py
- rag/config/retrieval_config.json
- rag/requirements.txt
- tests/ (new directory)
- tests/test_retrieval_correctness.py (new)
- tests/test_community_resolution.py (new)
- tests/test_confidence_thresholds.py (new)
- .github/workflows/ci.yml (new)
- docs (all four versioning locations + FUTURE_PLANS.md)
- api/version.py

---

## Planned

TBD after Phase 4.23.0 validation.

---

## Discarded / Won't Do

- Native Open WebUI form input fields (investigated, not possible)
  Open WebUI pipe responses cannot inject custom HTML input elements into the
  chat thread. The pipe can only yield text/markdown. Replaced by the
  multi-turn wizard UX in Phase 4.16.0.

---

## Notes for Future Sessions

When picking up this project in a new session:
1. Read docs/AI_HANDOFF.md first - it has the current version, phase, and
   recommended next step.
2. Check this file for what's planned next.
3. Cross off completed items in this file as part of every post-validation
   documentation prompt.
4. Add new ideas here during the session - don't lose them to chat history.
