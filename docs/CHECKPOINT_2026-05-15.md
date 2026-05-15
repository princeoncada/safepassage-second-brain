# Checkpoint 2026-05-15

## Current Phase Status

Overall system status: WORKING PROOF OF WORK

- Phase 2 Minimal POW: PASSED
- Phase 3A Minimal RAG Retrieval POW: PASSED
- Phase 3B Grounded Answering POW: PASSED

The final project is not complete.

## What Works

- n8n minimal ingestion webhook receives commands and writes Markdown.
- Deterministic classification, routing, YAML/frontmatter creation, and safe vault writing work.
- Optional DeepSeek Markdown cleanup has deterministic fallback.
- Local ChromaDB index works.
- Local `sentence-transformers` embeddings work.
- Vault Markdown is chunked by section.
- Low-value section filtering works.
- Duplicate chunks are reduced.
- Retrieval returns correct community/type/sections.
- `answer_vault.py --no-ai` retrieval-only mode works.
- DeepSeek grounded answer generation works.
- Answers use retrieved context and include citations.
- Insufficient context refuses unsafe answers.

## Intentionally Deferred

- Open WebUI
- n8n RAG integration
- autonomous agents
- automatic memory editing
- Git auto-commit
- dashboards
- voice/UI
- Phase 4 automations

## Validation Commands

Phase 2:

```text
/help
/post
/qa
/incident
/log
unknown fallback input
invalid DeepSeek key fallback
```

Phase 3A:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
```

Validated index result:

```text
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

Phase 3B:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

## Pass / Fail Results

Pass:

- `/help` returned usage and wrote no file.
- `/post`, `/qa`, `/incident`, `/log`, and unknown input routed correctly.
- invalid DeepSeek key still wrote fallback Markdown.
- retrieval found correct Sierra Ridge, Monterey, and digital ID chunks.
- answer generation answered the first three Phase 3B questions from retrieved context.
- Atlantis Bay refused with insufficient context.

Fail signs:

- answers invent policies;
- citations are missing;
- one community's rule is generalized to another community;
- Open WebUI, agents, or n8n RAG integration are added before Phase 3C.

## Known Issues / Next Refinements

These are not blockers.

1. Duplicate source files still appear in retrieval results.
   Cause: multiple generated test files contain nearly identical Sierra Ridge post orders.
   Future fix: add stronger dedupe by normalized title + section + community, or clean duplicate test files.

2. Citations currently list all retrieved chunks, including weak or less relevant chunks.
   Future fix: only cite chunks actually used in the generated answer.

3. Retrieval ranking can place QA Notes above Summary or Details.
   Future fix: add section weighting or reranking so Summary, Details, and Agent Action are preferred for factual answers.

4. Source numbering between generated answer and printed citation list can be confusing.
   Future fix: standardize final answer citation numbering to match retrieved source IDs exactly.

5. Titles and filenames are too verbose.
   Future fix: add deterministic title compression and filename compression.

6. Incident documents need richer structured fields.
   Future fix: expand incident ingestion format with time, lane, vehicle details, action taken, escalation, and camera reference.

7. Open Questions may contain generic AI filler.
   Future fix: only include open questions when confidence is low or required operational fields are missing.

8. Git auto-commit remains deferred.
   Future fix: add manual or controlled sync later only after retrieval and answering remain stable.

## Next Recommended Phase

PHASE 3C - RAG QUALITY HARDENING

Scope:

- dedupe improvement
- citation cleanup
- section reranking
- title/filename compression
- answer citation alignment
- stronger insufficient-context filtering

After Phase 3C, consider Open WebUI integration.

## What Not To Touch

- Do not rewrite `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json`.
- Do not revive the old complex Phase 2 workflow unless specifically requested.
- Do not rewrite `rag/scripts/index_vault.py` from scratch.
- Do not rewrite `rag/scripts/query_vault.py` from scratch.
- Do not rewrite `rag/scripts/answer_vault.py` from scratch.
- Do not add Open WebUI before Phase 3C.
- Do not add agents or Git auto-commit.
