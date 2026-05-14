# Phase 2 Ingestion Workflow

## Status

Phase 2 workflow documentation is ready for local n8n validation. The importable workflow export is `workflows/n8n/phase_2_ingestion_workflow.json`.

## Goal

Accept raw operational knowledge, classify it, route it to the correct vault folder, normalize it into metadata-complete Markdown, check QA risk, write the file, and commit the change to GitHub.

## Pipeline

```text
User raw input
-> n8n webhook receives raw text
-> intent_classifier prompt classifies input
-> document_router chooses target folder and template
-> normalizer converts raw input into metadata-complete Markdown
-> qa_risk_checker flags QA-sensitive operational risks
-> n8n writes Markdown file into correct vault folder
-> n8n commits change to GitHub
-> n8n stores workflow export in workflows/n8n later
```

## Required Inputs

The webhook must produce the canonical payload defined in `automation/ingestion/ingestion_contract.json`:

```json
{
  "input_text": "",
  "source": "",
  "community": "",
  "received_at": "",
  "classification": "",
  "priority": "",
  "target_folder": "",
  "suggested_filename": "",
  "normalized_markdown": ""
}
```

## Node Plan

| Step | n8n Node | Purpose |
|---|---|---|
| 1 | Webhook | Receive raw input from an operations form, manual call, or future connector. |
| 2 | Set | Shape the input into the canonical ingestion payload. |
| 3 | AI Request | Run `prompts/classification/intent_classifier.md`. |
| 4 | Code or Set | Merge classifier output into the payload. |
| 5 | AI Request or Lookup | Run `prompts/classification/document_router.md` and validate against `automation/ingestion/routing_rules.json`. |
| 6 | AI Request | Run `prompts/summarization/normalizer.md`. |
| 7 | AI Request | Run `prompts/compliance/qa_risk_checker.md`. |
| 8 | IF | If human review is required, route the Markdown to `vault/00_Inbox`. |
| 9 | Code | Write Markdown to the selected `vault/` folder. |
| 10 | Execute Command | Run Git add and commit on `master`. |
| 11 | Respond to Webhook | Return classification, filename, target folder, and review status. |

## Guardrails

- Do not write files outside `vault/`.
- Do not write secrets into Markdown.
- Do not call ChromaDB, RAG, or Open WebUI in Phase 2.
- When `qa_risk_checker` returns `requires_human_review: true`, write only to `vault/00_Inbox`.
- Do not commit generated n8n credentials, `.env`, or `n8n_data`.
- Keep workflow exports in `workflows/n8n/` once the workflow is built.

## Expected Success Response

```json
{
  "status": "accepted",
  "classification": "post_order",
  "priority": "high",
  "target_folder": "vault/03_Post_Orders",
  "suggested_filename": "2026-05-14-sierra-ridge-after-hours-visitor-id-post-order.md",
  "requires_human_review": true
}
```

## Importable Workflow

Import this file into n8n:

```text
workflows/n8n/phase_2_ingestion_workflow.json
```

Use `docs/N8N_SETUP.md` and `docs/LOCAL_TESTING.md` for setup and validation. Phase 2 is not complete until local import, API calls, vault writes, and Git push behavior are verified.
