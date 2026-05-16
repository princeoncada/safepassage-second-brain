# Troubleshooting

## Classifier Returns Unknown Too Often

Check that the raw input includes enough operational context:

- What happened or changed
- Which community is affected
- Whether this is a rule, incident, procedure, script, or automation note
- Any urgency or risk signal

Route unclear items to `vault/00_Inbox` for human review.

## File Routes To The Wrong Folder

Compare the classifier output with `automation/ingestion/routing_rules.json`.

Common causes:

- The input mixes multiple document types.
- The classifier returned `workflow` when the note should be `automation` or `sop`.
- The community or purpose is missing.

## Markdown Is Missing Metadata

Use `prompts/summarization/normalizer.md` and verify the output starts with the required YAML frontmatter:

```yaml
---
title:
type:
community:
priority:
effective_date:
source:
status:
tags:
last_updated:
version:
---
```

## QA Risk Checker Blocks A Write

In the Phase 2 workflow, high-risk content should be routed to `vault/00_Inbox` for review. Review the item manually when risk categories include:

- `access-control`
- `life-safety`
- `legal-compliance`
- `privacy`
- `security`
- `credential-risk`

## n8n Should Not Write Outside Inbox

For review-required items, confirm the workflow writes to:

```text
vault/00_Inbox
```

Do not write directly to operational folders when:

- `requires_human_review` is `true`
- classification is `unknown`
- QA risk severity is `high` or `critical`

## n8n Should Not Commit A File

Do not commit when:

- `normalized_markdown` is empty
- the target folder is outside `vault/`
- the filename does not end in `.md`
- the payload contains a real secret or credential

## Workflow Import Fails

Check:

- `workflows/n8n/phase_2_ingestion_workflow.json` is valid JSON.
- Your n8n version supports Webhook, Set, HTTP Request, Code, IF, Execute Command, and Respond to Webhook nodes.
- The workflow remains inactive until reviewed.

## Execute Command Cannot Find Helper Scripts

The n8n runtime must be able to access:

```text
automation/scripts/git_commit_push.js
```

Run n8n from the repository root or mount the repository into the container so relative paths resolve correctly.

## Git Push Fails

Check:

- n8n has Git installed.
- `origin` points to the expected GitHub repository.
- the checked out branch is `master`.
- Git user name and email are configured.
- GitHub credentials are available to the n8n runtime without committing secrets.

## Secret Appears In Input

Do not write the secret into the vault. Replace the secret with a generic note such as:

```text
[credential redacted]
```

Then flag the item with `credential-risk`.

## Phase Boundary Confusion

Phase 2 only covers structured ingestion. Phase 3A retrieval, Phase 3B grounded answering, Phase 3C quality hardening, Phase 3D local API access, and Phase 3E Open WebUI presentation docs are proof-of-work layers. Do not move retrieval, memory, vault writes, agents, or automation implementation into Open WebUI.

## Phase 3A Index Has No Results

Run:

```powershell
python rag/scripts/index_vault.py
```

Confirm `vault/` contains Markdown files and that they are not only under `vault/99_Archive`, which is skipped by default.

## Phase 3A Query Fails Because Collection Is Missing

The local ChromaDB index has not been built or was reset. Rebuild it:

```powershell
python rag/scripts/index_vault.py
```

## Phase 3A Retrieval Looks Wrong

Check the source Markdown first. ChromaDB is disposable derived data, while `vault/` is the source of truth.

Then reset and rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

By default, Phase 3A excludes low-value sections from indexing:

- `Change History`
- `Open Questions`
- `Source Input`

If those sections are appearing in results, rebuild the index without the debug flag:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

If duplicate-looking results appear, confirm the index was rebuilt after the dedupe refinement. The indexer skips effectively identical chunks, and the query script dedupes repeated source/title/section and content fingerprints.

To inspect excluded low-value sections for debugging only:

```powershell
python rag/scripts/index_vault.py --include-low-value-sections
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?" --include-low-value-sections --top-k 5
```

## Phase 3A Dependency Install Fails

Confirm Python and pip are available, then run:

```powershell
pip install -r rag/requirements.txt
```

Phase 3A uses local `sentence-transformers` embeddings and does not require API keys.

## Hugging Face Token Warning

An `HF_TOKEN` warning from `sentence-transformers` or Hugging Face is non-blocking for the local model used in this proof of work. Indexing and querying can still pass without `HF_TOKEN`.

## ChromaDB Reset Is Safe

ChromaDB is disposable derived data. Reset it safely with:

```powershell
python rag/scripts/reset_chroma.py --yes
```

Then rebuild:

```powershell
python rag/scripts/index_vault.py
```

The Markdown vault remains the source of truth.

## Duplicate Retrieval Results

Duplicates can happen if generated test files are not cleaned. This is a known non-blocking refinement item. Future work should add stronger dedupe by normalized title + section + community, or clean duplicate generated test files.

## Weak Context Refusal

The weak context threshold may trigger refusal correctly. If the retrieved chunks do not directly answer the question, Phase 3B should say the vault does not contain enough information to answer safely.

## Phase 3C Query Refuses Unexpectedly

Phase 3C uses conservative checks:

- retrieval distance threshold;
- community hint mismatch;
- expected document type mismatch.

If a refusal seems too strict, inspect retrieval only:

```powershell
python rag/scripts/answer_vault.py "your question" --no-ai --show-context --top-k 5
python rag/scripts/query_vault.py "your question" --top-k 5
```

Then improve vault Markdown quality or adjust `rag/config/retrieval_config.json`.

## Phase 3C Citation Output Looks Shorter

This is expected. `answer_vault.py` separates retrieved sources from answer citations and only prints citations that the generated answer explicitly used. If the model omits source IDs, the script prints retrieved sources for review.

## Phase 3C Duplicate Results Still Appear

This can happen when duplicate files have meaningfully different content. The dedupe is lightweight and heuristic. Future hardening can add stronger title/section/community dedupe or clean generated test files from the vault.

## Phase 3D API Server Does Not Start

Install dependencies:

```powershell
pip install -r rag/requirements.txt
```

Then start:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

If port `8000` is already in use, choose another local port.

## Phase 3D Missing DeepSeek Key

If `/ask` returns `status: "error"` because `DEEPSEEK_API_KEY` is missing, set it:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Or send:

```json
{
  "no_ai": true
}
```

to validate retrieval only.

## Phase 3D API Refuses A Question

This can be correct. The API reuses the conservative insufficient-context checks from `answer_vault.py`. Inspect `retrieval_confidence`, `confidence_reason`, `sources`, and `warnings` in the JSON response.

## Phase 3E Open WebUI Cannot Reach API

Confirm FastAPI is running:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Test directly:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What are Sierra Ridge overnight visitor ID rules?",
    "top_k":5,
    "no_ai":true
  }'
```

If Open WebUI is running in Docker, use `http://host.docker.internal:8000/ask` instead of `http://localhost:8000/ask`.

## Phase 3E CORS Issues

The FastAPI app allows localhost origins. If Open WebUI uses another origin, add that local origin to `api/main.py` only after confirming it is still local-first.

## Phase 3E Missing DeepSeek Key

If Open WebUI receives a `DEEPSEEK_API_KEY` error, set the key in the shell running FastAPI:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
python -m uvicorn api.main:app --reload --port 8000
```

Use `no_ai=true` to validate retrieval without DeepSeek.

## Phase 3E Stale Chroma Index

If Open WebUI answers look stale or missing, rebuild the local index:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Open WebUI should never bypass FastAPI or call ChromaDB directly.

## Phase 4A Duplicate Sources In Open WebUI

Phase 4A separates retrieved `sources` from `answer_citations` and strips trailing model-generated `Sources:` blocks from the API `answer`. The Open WebUI connector should render one Sources section from `answer_citations`.

If duplicate source lists still appear, check the Open WebUI connector template and make sure it is not rendering both:

- a model-generated `Sources:` block inside `answer`;
- a second manually formatted list from `answer_citations`.

## Phase 4A Duplicate Retrieval Results

Phase 4A dedupes after reranking so the strongest near-duplicate survives. It compares normalized title, community, type, section, content preview, and lightweight content similarity.

Duplicates can still appear when files are similar but not effectively identical. Generated test files can still pollute the vault until they are manually cleaned or archived.

## Phase 4A Section Ranking Looks Wrong

The section weighting is heuristic. Preferred sections are:

```text
Agent Action
Summary
Details
Rule
Policy
QA Notes
```

`QA Notes` should still appear when relevant, but should not dominate factual or policy questions when stronger operational sections are available. Rebuild the index before evaluating:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

## Phase 4A Citation List Is Empty

If DeepSeek answers without explicit source IDs like `[1]`, the API cannot safely infer which sources were actually used. The response will include a warning and leave `answer_citations` empty rather than citing unrelated chunks.

Re-run with retrieval context visible:

```powershell
python rag/scripts/answer_vault.py "your question" --no-ai --show-context --top-k 5
```

## Phase 4A Refusal Still Happens

This can be correct. Phase 4A does not weaken conservative refusal behavior. Community mismatch, missing community sources, weak distance, or expected type mismatch can still trigger:

```text
The vault does not contain enough information to answer this safely.
```

## Phase 4B Primary Workflow Files Are Not Created

Run the deterministic ingester:

```powershell
python automation/ingestion/ingest_primary_workflow.py
```

If files already exist, the script skips them. Re-run with `--force` only when you intentionally want to overwrite generated primary workflow files:

```powershell
python automation/ingestion/ingest_primary_workflow.py --force
```

## Phase 4B PDF Text Extraction Is Unreliable

OCR is not required. Manually paste extracted text into:

```text
automation/ingestion/sample_primary_workflow_input.md
```

Use the blank structure in:

```text
automation/ingestion/primary_workflow_input_template.md
```

Then run the ingester.

## Phase 4B Primary Workflow Does Not Appear In Retrieval

Confirm generated files exist in:

```text
vault/09_SOPs/
```

Then rebuild ChromaDB:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Check that indexed chunks include `authority_level: primary_workflow` in retrieved output:

```powershell
python rag/scripts/query_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
```

## Phase 4B Primary Workflow Overrides A Post Order

Treat this as a failed validation. The authority hierarchy is:

```text
post_order
announcement
primary_workflow
```

For community-specific questions, post orders and announcements should outrank global primary workflow. Check retrieved source authority levels and confirm the community-specific document is indexed.

## Phase 4B Unknown Community Answer Sounds Too Specific

Unknown-community fallback must not invent community-specific policy. The answer should say no source exists for that community and only use primary workflow as default guidance when relevant.

## Phase 4B2 Default Workflow Query Refuses

If a default workflow question retrieves the correct global primary workflow source but refuses because the distance is slightly above `weak_context_distance_threshold`, check:

```json
"primary_workflow_default_threshold": 1.1
```

This threshold should only apply to explicit default/base/primary workflow queries such as:

```text
How many times do I call the resident by default?
```

It should not be used for community-specific questions such as:

```text
How many times do I call the resident for Atlantis Bay?
```

If the community-specific question does not have an indexed matching source, refusal is the correct behavior.

## Phase 4C Refresh Creates No Files

If dry run was used, no vault files should be written. Run without `--dry-run` to create Markdown and a report:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

If the same batch was already applied, unchanged rules are reported as duplicates and no duplicate active files are created.

## Phase 4C Superseded Rule Still Appears In Retrieval

Rebuild ChromaDB after refresh:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Superseded rules are still indexable but receive a heavy retrieval penalty. If one ranks above an active rule, check that the active rule has `status: active` and `authority_level: post_order`.

## Phase 4C Conflict Was Created

Conflict files are expected when deterministic checks find contradictory patterns such as different resident call counts, save-tag contradictions, or physical-ID versus digital-ID acceptance. Review the generated report under:

```text
vault/08_Reports/post-order-refresh/
```

Do not rely on a `status: conflict` rule operationally until manually reviewed.

## Phase 3B Missing DeepSeek Key

If `answer_vault.py` says `DEEPSEEK_API_KEY` is not set, set it in PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

To validate retrieval without an API key:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

## Phase 3B Answer Has No Citations

The answer is not valid unless it cites source file and section. Re-run with context visible:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --show-context --top-k 5
```

Check that retrieved chunks are relevant before trusting the answer.

## Phase 3B Invents A Policy

Treat this as a failed validation. The prompt requires the model to answer only from retrieved context and to say:

```text
The vault does not contain enough information to answer this safely.
```

when context is insufficient. Improve vault source content or retrieval quality before expanding answer generation.

## Phase 3B DeepSeek Request Fails

Check:

- `DEEPSEEK_API_KEY` is set in the current shell.
- network access is available.
- the ChromaDB index exists and was built with `python rag/scripts/index_vault.py`.
- `--no-ai` still works for retrieval-only validation.
