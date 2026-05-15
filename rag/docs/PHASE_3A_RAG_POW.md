# Phase 3A Minimal RAG Proof of Work

## Goal

Phase 3A answers one question: can local semantic search retrieve the correct Markdown chunks from the vault?

It intentionally does not generate final AI answers.

## Architecture

- `vault/` is the source of truth.
- `rag/chroma/` is a disposable local ChromaDB index.
- `sentence-transformers/all-MiniLM-L6-v2` creates local embeddings.
- Markdown is chunked deterministically by section heading.
- Chunks keep metadata for title, section, source file, type, community, priority, tags, and status.

## Install

```powershell
pip install -r rag/requirements.txt
```

No API keys are required.

## Index The Vault

```powershell
python rag/scripts/index_vault.py
```

By default, `vault/99_Archive` is skipped. To include it:

```powershell
python rag/scripts/index_vault.py --include-archive
```

## Query The Index

```powershell
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?"
```

The script prints rank, distance, title, type, community, section, source file, and chunk preview.

## Reset The Index

```powershell
python rag/scripts/reset_chroma.py --yes
```

Then rebuild:

```powershell
python rag/scripts/index_vault.py
```

## Why ChromaDB Is Disposable

ChromaDB stores derived embeddings and chunk metadata. Every record can be rebuilt from Markdown files in `vault/`, so ChromaDB should not be treated as canonical storage.

## Why Markdown Remains Source Of Truth

Markdown files are human-readable, reviewable, versionable, and portable. If a retrieval result is wrong, fix or add the Markdown source first, then rebuild the index.

## Why No AI Answers Yet

Answer generation is intentionally excluded until retrieval quality is validated. Phase 3A checks whether the right evidence can be found before any model is allowed to summarize or answer from it.

## Successful Validation

Phase 3A is successful when:

- `python rag/scripts/index_vault.py` runs without API keys.
- local ChromaDB files are created under `rag/chroma/`.
- `query_vault.py` returns relevant chunks from the vault.
- Sierra Ridge physical ID queries retrieve `post_order` or `qa_rule` chunks.
- Monterey tailgating queries retrieve an `incident` chunk.
- no Open WebUI or answer generation exists in this phase.
