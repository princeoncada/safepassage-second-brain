# Architectural Decisions

## ADR-001: Markdown is the source of truth

### Decision

All operational knowledge is stored as Markdown.

### Reason

Markdown is human-readable, portable, Git-friendly, easy for AI to parse, and compatible with Obsidian.

### Rejected Alternatives

- DOCX as source of truth: harder to diff, harder to parse, creates technical debt.
- Database-only storage: less human-readable, more complex early.

---

## ADR-002: DOCX is export only

### Decision

DOCX files are generated artifacts only.

### Reason

DOCX is useful for sharing, printing, and formal documentation, but it should not control system memory.

---

## ADR-003: GitHub is mandatory

### Decision

Every important change should be committed to GitHub.

### Reason

GitHub gives rollback safety, audit history, and future AI traceability.

---

## ADR-004: n8n handles operational automation

### Decision

n8n is the main automation layer.

### Reason

It is visual, modular, portable, and easier to maintain than custom automation code too early.

---

## ADR-005: Phase 2 uses modular ingestion prompts

### Decision

Structured ingestion is split into classifier, router, normalizer, and QA risk checker prompts.

### Reason

Separate prompts are easier to test, replace, and debug than one large ingestion prompt.

---

## ADR-006: Routing rules are stored as JSON

### Decision

Folder routing rules are stored in `automation/ingestion/routing_rules.json`.

### Reason

JSON is easy for n8n and future automation to parse while remaining human-readable for review.

---

## ADR-007: Phase 2 avoids vector search implementation

### Decision

Phase 2 does not implement ChromaDB, RAG, Open WebUI, or advanced automations.

### Reason

The system needs reliable structured ingestion before retrieval, chat, and automation layers are added.

---

## ADR-008: Semantic Phase Versioning

### Decision

All phases use semantic version tags in the format PHASE-[MAJOR].[MINOR].[PATCH]-[STATE] where STATE is one of alpha, beta, rc, or stable.

### Reason

As the project grows in complexity with multiple Codex agents, human operators, and live validation passes happening in parallel, an explicit versioning system prevents ambiguity about whether a phase is safe to rely on operationally. It also gives future AI agents a clear signal about what is production-ready vs in-progress.

### Promotion Rules

alpha -> beta: first partial validation pass completed
beta -> rc: all known bugs fixed, all validation commands pass
rc -> stable: user manually commits to master
stable -> patch: new bug found, fix applied, patch version incremented

### State Meanings

alpha: Implemented but not yet tested. Do not rely on operationally.
beta: Partially working. Known issues remain. Use with caution.
rc: All tests pass. Awaiting commit. Safe to test operationally.
stable: Committed to master. Production ready.

### Rejected Alternatives

- Date-only versioning: does not communicate stability state
- Semantic versioning without state suffix: hides validation status
- No versioning: causes confusion for AI agents continuing the project
