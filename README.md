# SafePassage Second Brain

A local-first AI-powered operational knowledge system for workflows, SOPs, post orders, QA protection, incidents, scripts, automations, and searchable work intelligence.

## Source Of Truth

Markdown files in `vault/`.

## Current Status

Working proof of work through Phase 3E integration documentation:

- Phase 2 Minimal POW ingestion: passed
- Phase 3A retrieval: passed
- Phase 3B grounded answering: passed
- Phase 3C RAG quality hardening: passed
- Phase 3D local FastAPI wrapper: passed
- Phase 3E Open WebUI integration: passed
- Phase 4A retrieval quality hardening: passed with minor tuning
- Phase 4B primary workflow ingestion: in progress

Current architecture:

```text
Open WebUI
-> FastAPI /ask
-> local retrieval
-> grounded answer generation
-> citations/refusal/confidence
```

Open WebUI is presentation-only. Markdown in `vault/` remains the source of truth.

Phase 4A keeps this architecture and improves only retrieval ranking, dedupe, source selection, and citation cleanup.

Phase 4B adds the SafePassage primary kiosk workflow as global default guidance below post orders and announcements.

## Local RAG API

```powershell
pip install -r rag/requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

## Version Control

GitHub is required for rollback, audit history, and future AI handoff.

## Phase Rule

Do not proceed to the next phase until the current phase passes documentation, testing, and validation.
