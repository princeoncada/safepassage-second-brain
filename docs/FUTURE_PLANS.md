# Future Plans

This file is the living backlog for SafePassage Second Brain.
Completed items are struck through. Every phase should update this file —
cross off completed items and add new ideas as they arise.

Last updated: 2026-05-19
Current stable version: 4.19.0-alpha

---

## Completed

- ~~Patch 4.18.3 — restore clean CLI citation display ([Source N] regex fix)~~
- ~~Phase 4.18.0 — Community-aware kiosk call flow synthesis (SOP enrichment + call flow routing + merged output)~~
- ~~Phase 4.13.4 — Fix double sources display in CLI output~~
- ~~Phase 4.14.0 — Incremental indexing (`--files` flag on index_vault.py)~~
- ~~Phase 4.15.0 — Streaming response (`/ask/stream` SSE endpoint + Open WebUI pipe)~~
- ~~Phase 4.16.0 — Conflict detection + multi-turn wizard UX for `/post-orders`~~
- ~~Phase 4.17.0 — Quick reply hints in Open WebUI pipe + FUTURE_PLANS.md introduced~~

---

## In Progress

- Phase 4.19.0 — operational trust audit log

---

## Planned

### Near-term (next 1–3 phases)

- Phase 4.20.0 — Model preloading (eliminate per-query SentenceTransformer weight load)

### UX / Open WebUI

- Action Function button UX (future)
  Replace quick reply hints with genuine tappable buttons using Open WebUI's
  Action Function system. Requires a separate `openwebui/action.py` file
  installed alongside the pipe. Uses `__event_call__` for two-way confirmation
  dialogs. Deferred because it requires a separate install step and is more
  complex than quick reply hints.

- Community alias autocomplete (future)
  When typing `/post-orders` in Open WebUI, show alias suggestions as the
  operator types. Requires Open WebUI frontend customization — not achievable
  via pipe alone.

### Ingestion / Vault

- `/post-orders` batch input (future)
  Allow pasting multiple dated post order blocks in a single ingestion.
  Currently each date block is parsed but only one community per command.
  Future: support multi-community batches in a single paste.

- Announcement expiry tracking (future)
  Auto-archive announcements past their event date. Currently announcements
  stay active indefinitely unless manually archived.

- Vault integrity check command (future)
  `/vault-check` slash command that scans for orphaned rules, duplicate hashes,
  missing frontmatter fields, and reports any inconsistencies without modifying
  anything.

### Retrieval / Answering

- Query intent confidence tuning (future)
  The rerank threshold (0.95) and refusal logic were hand-tuned. A future
  phase could add a calibration script that tests thresholds against a
  labelled query set and reports precision/recall.

- Multi-community queries (future)
  Currently each query resolves to one community. Future: detect queries that
  span multiple communities ("what is the ID policy for SR and CBK?") and
  retrieve from both.

### Infrastructure

- Production deployment (X = 1 milestone)
  Deploy to a cloud server so VA team accesses remotely instead of localhost.
  Replace ChromaDB local storage with a managed vector database.
  Add per-user authentication. This is the X = 1 version bump milestone.

- Model load optimization (future)
  Keep the SentenceTransformer model loaded as a long-lived FastAPI background
  service rather than loading it as a subprocess on each query. Reduces
  per-query latency by ~1–2 seconds.

- Automated vault backup (future)
  Daily git commit of vault/ changes to a separate backup branch or remote.
  Currently relies on manual commits.

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
