# Phase 3A Expected Retrieval Results

Phase 3A passes when semantic retrieval returns the right source chunks from `vault/`. It does not need to generate answers.

## Sierra Ridge Physical ID Rules

Command:

```powershell
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?"
```

Successful retrieval should include at least one top result where:

- `Type` is `post_order` or `qa_rule`
- `Community` is `Sierra Ridge`
- the preview mentions physical ID, visitors, access, or digital ID handling

## Monterey Tailgating

Command:

```powershell
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?"
```

Successful retrieval should include at least one top result where:

- `Type` is `incident`
- `Community` is `Monterey`
- the preview mentions tailgating, resident lane, vehicle, or Monterey

## Digital ID When Physical ID Is Required

Command:

```powershell
python rag/scripts/query_vault.py "What should I do if a digital ID is accepted when physical ID is required?"
```

Successful retrieval should include at least one top result where:

- `Type` is `qa_rule`
- `Community` is `Sierra Ridge`
- the preview mentions digital ID, physical ID, QA failure, rejection, or escalation

If these chunks are not retrieved, inspect whether the expected Markdown files exist in `vault/`, then reset and rebuild ChromaDB.
