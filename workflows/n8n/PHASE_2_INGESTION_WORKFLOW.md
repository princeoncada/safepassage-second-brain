# Phase 2 Ingestion Workflow

## Status

Phase 2 workflow documentation is ready for n8n buildout. This file describes the intended workflow but does not include an exported n8n workflow yet.

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
| 8 | IF | If human review is required, route to `vault/00_Inbox` or stop for review. |
| 9 | Write Binary File or Execute Command | Write Markdown to the selected `vault/` folder. |
| 10 | Execute Command | Run Git add and commit on `master`. |
| 11 | Respond to Webhook | Return classification, filename, target folder, and review status. |

## Guardrails

- Do not write files outside `vault/`.
- Do not write secrets into Markdown.
- Do not call ChromaDB, RAG, or Open WebUI in Phase 2.
- Do not make unattended writes when `qa_risk_checker` returns `requires_human_review: true`.
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

## Manual Build Notes

The current repository contains the contract, prompts, routing rules, and sample fixtures needed to build this workflow in n8n. The actual n8n export should be added later after manual credential setup and test execution.
