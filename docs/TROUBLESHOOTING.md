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

Phase 2 only covers structured ingestion. Do not add ChromaDB, RAG, Open WebUI, autonomous agents, vector databases, memory systems, semantic search, or advanced automation implementation until a later phase explicitly starts.

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
