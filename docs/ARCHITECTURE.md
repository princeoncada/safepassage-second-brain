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
Handles the current stable Phase 2 Minimal POW ingestion webhook.

Current working ingestion flow:

```text
n8n webhook
-> deterministic classification/routing
-> optional DeepSeek Markdown cleanup
-> deterministic YAML/frontmatter creation
-> safe local vault write
```

The stable ingestion workflow is `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json`.

### DeepSeek API
Used optionally in Phase 2 Minimal POW to clean Markdown sections, with deterministic fallback when unavailable.

For Phase 3B, DeepSeek is used only for final answer generation from retrieved vault context. It must not retrieve, edit memory, or invent unsupported policy.

### ChromaDB
Used for local semantic retrieval and metadata-aware search.

ChromaDB is a local disposable index under `rag/chroma/`. It is rebuilt from Markdown in `vault/` and is not a source of truth.

### Open WebUI
Planned later as the chat interface only. It is not the storage layer.

Open WebUI is not implemented yet. Consider it only after Phase 3C RAG Quality Hardening.

## Current Working Flow

### Ingestion

```text
n8n webhook
-> deterministic classification/routing
-> optional DeepSeek Markdown cleanup
-> deterministic YAML/frontmatter creation
-> safe local vault write
```

### Retrieval

```text
vault Markdown
-> section-based chunking
-> local embeddings
-> ChromaDB
-> query_vault.py retrieval
```

### Answering

```text
question
-> retrieve top chunks
-> DeepSeek answer generation
-> cite source file + section
-> refuse when context is insufficient
```

## Phase 3A Retrieval Flow

Markdown files in `vault/`
-> deterministic section chunking
-> local sentence-transformers embeddings
-> local ChromaDB collection `safepassage_vault_chunks`
-> retrieval-only CLI query results

Phase 3A did not generate answers. It validated retrieval quality before Phase 3B added grounded answer generation.

## Phase 3B Answer Flow

User question
-> local sentence-transformers query embedding
-> ChromaDB retrieves top vault chunks
-> compact context packet is built
-> DeepSeek generates a grounded answer from retrieved context only
-> answer cites source file and section

If retrieved context is insufficient, the answer must say the vault does not contain enough information to answer safely.

## Phase 1 Data Flow

User input
→ n8n webhook
→ DeepSeek classification/normalization
→ Markdown file created in vault
→ Git commit
→ Optional DOCX export later
