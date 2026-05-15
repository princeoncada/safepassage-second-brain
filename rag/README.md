# Phase 3 Local RAG Proof of Work

Current status: WORKING PROOF OF WORK

- Phase 3A retrieval works.
- Phase 3B grounded answering works.
- Open WebUI is not implemented yet.

Phase 3A tests whether local semantic search can retrieve the right Markdown chunks from `vault/`.

Phase 3B adds minimal grounded answer generation using only retrieved vault chunks.

This does not add Open WebUI, n8n integration, agents, automatic memory editing, Git automation, dashboards, or Phase 4 automations.

## Install

```powershell
pip install -r rag/requirements.txt
```

## Index

```powershell
python rag/scripts/index_vault.py
```

This reads Markdown from `vault/`, skips `vault/99_Archive` by default, chunks documents by Markdown section, embeds chunks with `sentence-transformers/all-MiniLM-L6-v2`, and stores them in local ChromaDB under `rag/chroma/`.

## Query

```powershell
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?"
```

The query script prints retrieved chunks only.

## Answer

Set the DeepSeek key:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Run grounded answer generation:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Validate retrieval without AI:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

Answers must cite retrieved source files and sections. If context is insufficient, the answer should say the vault does not contain enough information to answer safely.

## Reset

```powershell
python rag/scripts/reset_chroma.py --yes
```

The ChromaDB index is disposable. Rebuild it any time from the Markdown vault.

## Validated Results

Indexing:

```text
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

Retrieval passed for:

```text
overnight visitors must present physical ID before access
What happened with tailgating at Monterey?
What should the agent do if digital ID is presented instead of physical ID?
```

Answering passed for:

```text
What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?
What happened with tailgating at Monterey?
What are Sierra Ridge overnight visitor ID rules?
What is the vehicle policy for Atlantis Bay?
```

The first three answer from retrieved context. Atlantis Bay refuses with insufficient context.

## Known Issues / Next Refinements

These are not blockers.

1. Duplicate source files still appear in retrieval results.
2. Citations currently list all retrieved chunks, including weak or less relevant chunks.
3. Retrieval ranking can place QA Notes above Summary or Details.
4. Source numbering between generated answer and printed citation list can be confusing.
5. Titles and filenames are too verbose.
6. Incident documents need richer structured fields.
7. Open Questions may contain generic AI filler.
8. Git auto-commit remains deferred.

Recommended next phase: PHASE 3C - RAG QUALITY HARDENING. After Phase 3C, consider Open WebUI integration.
