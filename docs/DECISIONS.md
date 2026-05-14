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