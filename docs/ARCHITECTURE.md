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

### Open WebUI
Planned later as the chat interface only. It is not the storage layer.

## Phase 1 Data Flow

User input
→ n8n webhook
→ DeepSeek classification/normalization
→ Markdown file created in vault
→ Git commit
→ Optional DOCX export later