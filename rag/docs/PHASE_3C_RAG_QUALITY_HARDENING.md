# Phase 3C RAG Quality Hardening

## Purpose

Phase 3C improves retrieval and answer quality without adding new major features.

It does not add Open WebUI, n8n changes, agents, autonomous memory, Git auto-commit, dashboards, voice, Phase 4 automations, new databases, or cloud embeddings.

## What Was Hardened

- Better dedupe for repeated/generated Markdown files.
- Section reranking so high-value sections are preferred.
- Query metadata hints for community and likely document type.
- Stronger insufficient-context refusal.
- Cleaner answer citation output.
- Clearer retrieval confidence output.

## Dedupe Strategy

The index stores normalized title, community, and section metadata. Indexing and query retrieval both compare content with lightweight token similarity so near-identical chunks from repeated/generated files are reduced.

Duplicates can still appear when files are meaningfully different or when multiple sections are legitimately relevant.

## Section Reranking Strategy

Preferred sections:

- `Summary`
- `Details`
- `Agent Action`
- `QA Notes`

Lower-value sections:

- `Open Questions`
- `Source Input`
- `Change History`

Low-value sections are excluded by default. If included, they are penalized so they should rank below higher-value operational sections.

## Refusal Strategy

The answer script refuses before calling DeepSeek when deterministic checks indicate weak context:

- no chunks returned;
- best retrieval distance is above the configured threshold;
- a community is mentioned but no indexed source matches it;
- the query implies a document type and retrieved sources do not match.

Expected refusal:

```text
The vault does not contain enough information to answer this safely.
```

## Citation Strategy

Retrieved sources keep stable source IDs in the context packet. Generated answers must cite those IDs exactly. The script now separates:

- retrieved sources;
- citations actually used by the generated answer.

If the model omits citations, the script prints retrieved sources for review instead of treating every retrieved chunk as an answer citation.

## Validation Commands

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

```powershell
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
```

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Retrieval-only:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context --top-k 5
```

## Known Limitations

- Retrieval quality depends on Markdown quality.
- Duplicate files can still affect results if content is meaningfully different.
- Section weighting is heuristic.
- Insufficient-context detection is conservative.
- No Open WebUI integration yet.
- No automatic vault cleanup yet.

## Manual Review

The user will manually review and commit Phase 3C changes. Do not auto-commit or push.
