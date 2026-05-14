# n8n Setup

## Purpose

This guide explains how to import and configure the Phase 2 structured ingestion workflow.

Phase 2 remains `IN PROGRESS` until this workflow is tested locally with real n8n executions.

## Required Files

- `workflows/n8n/phase_2_ingestion_workflow.json`
- `automation/scripts/sanitize_filename.js`
- `automation/scripts/validate_metadata.js`
- `automation/scripts/validate_payload.js`
- `automation/scripts/write_markdown.js`
- `automation/scripts/git_commit_push.js`
- `automation/ingestion/test_webhook_payload.json`

## Required Environment Variables

Set these in the n8n runtime environment:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
VAULT_PATH=./vault
GITHUB_REPO_URL=https://github.com/princeoncada/safepassage-second-brain.git
```

Do not commit `.env` or real API keys.

## Import Workflow

1. Open n8n.
2. Choose import from file.
3. Select `workflows/n8n/phase_2_ingestion_workflow.json`.
4. Confirm the workflow imports as inactive.
5. Review every node before activating.

## Webhook Endpoint

The workflow uses:

```text
POST /webhook/phase-2-ingestion
```

For manual n8n test mode, n8n may provide a temporary test webhook URL. Use the URL shown by n8n during the manual test execution.

## Volume And Path Expectations

The workflow assumes the n8n process can access:

- the repository working tree
- the `vault/` folder
- the `automation/scripts/` helper scripts
- Git credentials or a configured remote that can push to `origin master`

Use relative paths where possible. Do not hardcode local absolute paths into the workflow.

## Git Behavior

The workflow calls:

```text
node automation/scripts/git_commit_push.js "chore: ingest structured knowledge"
```

That helper script runs:

```text
git add .
git commit
git push origin master
```

Only enable this after confirming the n8n runtime has the correct repository path, Git identity, and GitHub authentication.

## Human Review Routing

If the classifier or QA risk checker requires human review, the workflow routes the Markdown file to:

```text
vault/00_Inbox
```

This keeps the item visible without treating it as approved operational truth.

## Phase Boundary

Do not add ChromaDB, RAG, Open WebUI, autonomous agents, vector databases, memory systems, semantic search, or advanced automations to this Phase 2 workflow.
