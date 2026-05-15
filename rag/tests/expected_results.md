# Phase 3A Expected Retrieval Results

Phase 3A passes when semantic retrieval returns the right source chunks from `vault/`. It does not need to generate answers.

Validated status: PASSED

Validated index output:

```text
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

By default, the index excludes low-value sections:

- `Change History`
- `Open Questions`
- `Source Input`

Preferred sections should rank higher:

- `Summary`
- `Details`
- `Agent Action`
- `QA Notes`

## Sierra Ridge Physical ID Rules

Command:

```powershell
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
```

Successful retrieval should include top results where:

- `Type` is `post_order` or `qa_rule`
- `Community` is `Sierra Ridge`
- `Section` is usually `Summary`, `Details`, or `Agent Action`
- the preview mentions physical ID, visitors, access, or digital ID handling
- duplicate-looking generated test files are reduced

## Monterey Tailgating

Command:

```powershell
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?"
```

Successful retrieval should include top results where:

- `Type` is `incident`
- `Community` is `Monterey`
- `Section` is usually `Summary` or `Details`
- the preview mentions tailgating, resident lane, vehicle, or Monterey
- `Change History` should not appear unless low-value sections were explicitly indexed and queried

## Digital ID When Physical ID Is Required

Command:

```powershell
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?"
```

Successful retrieval should include top results where:

- `Type` is `qa_rule`
- `Community` is `Sierra Ridge`
- `Section` is usually `Agent Action`, `QA Notes`, or `Details`
- the preview mentions digital ID, physical ID, QA failure, rejection, or escalation
- `Open Questions` should not appear unless low-value sections were explicitly indexed and queried

If these chunks are not retrieved, inspect whether the expected Markdown files exist in `vault/`, then reset and rebuild ChromaDB.

To inspect low-value sections for debugging, rebuild and query with:

```powershell
python rag/scripts/index_vault.py --include-low-value-sections
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?" --include-low-value-sections
```

## Known Issues

These are not blockers:

- duplicate source files still appear in retrieval results when generated test files contain nearly identical Sierra Ridge post orders;
- retrieval ranking can place QA Notes above Summary or Details;
- titles and filenames are too verbose.
