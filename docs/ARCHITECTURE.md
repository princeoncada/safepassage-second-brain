# System Architecture

## Purpose
This project is a local-first AI-powered operational second brain for SafePassage-style kiosk operations, workflows, SOPs, post orders, QA rules, incidents, scripts, and compliance memory.

## Source of Truth
Markdown files inside the `vault/` folder are the canonical source of truth.

## Artifact Outputs
DOCX and PDF files are generated exports only. They are not the source of truth.

## Main Components

### Obsidian Vault
Stores human-readable Markdown documents.

### GitHub
Provides version history, rollback, audit trail, and collaboration safety.

### n8n
Handles ingestion, formatting, routing, exports, GitHub commits, and future ChromaDB indexing.

### DeepSeek API
Used initially for classification, summarization, formatting, and structured ingestion.

### ChromaDB
Planned for Phase 3. Used for semantic retrieval and metadata-aware search.

For Phase 3A, ChromaDB is a local disposable index under `rag/chroma/`. It is rebuilt from Markdown in `vault/` and is not a source of truth.

### Open WebUI
Planned later as the chat interface only. It is not the storage layer.

Open WebUI is not part of Phase 3A.

## Phase 3A Retrieval Flow

Markdown files in `vault/`
-> deterministic section chunking
-> local sentence-transformers embeddings
-> local ChromaDB collection `safepassage_vault_chunks`
-> retrieval-only CLI query results

Phase 3A does not generate answers. It validates retrieval quality before adding answer generation.

## Phase 1 Data Flow

User input
→ n8n webhook
→ DeepSeek classification/normalization
→ Markdown file created in vault
→ Git commit
→ Optional DOCX export later
