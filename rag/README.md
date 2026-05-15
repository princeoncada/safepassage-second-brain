# Phase 3 Local RAG Proof of Work

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
