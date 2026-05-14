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
