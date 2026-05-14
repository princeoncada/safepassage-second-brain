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

This is expected for high-risk content. Review the item manually when risk categories include:

- `access-control`
- `life-safety`
- `legal-compliance`
- `privacy`
- `security`
- `credential-risk`

## n8n Should Not Commit A File

Do not commit when:

- `requires_human_review` is `true`
- `normalized_markdown` is empty
- the target folder is outside `vault/`
- the filename does not end in `.md`
- the payload contains a real secret or credential

## Secret Appears In Input

Do not write the secret into the vault. Replace the secret with a generic note such as:

```text
[credential redacted]
```

Then flag the item with `credential-risk`.

## Phase Boundary Confusion

Phase 2 only covers structured ingestion. Do not add ChromaDB, RAG, Open WebUI, or advanced automation implementation until a later phase explicitly starts.
