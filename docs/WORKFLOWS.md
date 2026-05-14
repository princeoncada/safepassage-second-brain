# Workflows

## Phase 2 Structured Ingestion

The Phase 2 workflow turns raw operational notes into organized Markdown files in the Obsidian vault.

```text
User raw input
-> n8n webhook receives raw text
-> intent_classifier prompt classifies input
-> document_router chooses target folder and template
-> normalizer converts raw input into metadata-complete Markdown
-> qa_risk_checker flags QA-sensitive operational risks
-> n8n writes Markdown file into correct vault folder
-> n8n commits change to GitHub
```

## Source Files

| Purpose | File |
|---|---|
| Ingestion contract | `automation/ingestion/ingestion_contract.json` |
| Routing rules | `automation/ingestion/routing_rules.json` |
| Sample inputs | `automation/ingestion/sample_inputs.json` |
| Sample expected outputs | `automation/ingestion/sample_outputs.json` |
| Classifier prompt | `prompts/classification/intent_classifier.md` |
| Router prompt | `prompts/classification/document_router.md` |
| Normalizer prompt | `prompts/summarization/normalizer.md` |
| QA risk prompt | `prompts/compliance/qa_risk_checker.md` |
| n8n workflow documentation | `workflows/n8n/PHASE_2_INGESTION_WORKFLOW.md` |

## Routing Summary

| Document Type | Target Folder |
|---|---|
| `briefing` | `vault/01_Daily_Briefings` |
| `community_profile` | `vault/02_Communities` |
| `post_order` | `vault/03_Post_Orders` |
| `qa_rule` | `vault/04_QA_Rules` |
| `script` | `vault/05_Scripts` |
| `incident` | `vault/06_Incidents` |
| `visitor_log` | `vault/07_Visitor_Logs` |
| `training` | `vault/08_Training` |
| `sop` | `vault/09_SOPs` |
| `automation` | `vault/10_Automations` |
| `workflow` | `vault/10_Automations` |
| `code_snippet` | `vault/11_Code_Snippets` |
| `unknown` | `vault/00_Inbox` |
| `archived` | `vault/99_Archive` |

## Human Review Rules

Human review is required when:

- Classification is `unknown`.
- QA risk severity is `high` or `critical`.
- The item contains access control, life safety, legal, security, privacy, or credential risk.
- Required metadata is missing and the item could affect operations.

## Phase Boundary

This workflow is Phase 2 only. It prepares clean, routed, metadata-complete Markdown. It does not implement ChromaDB, RAG, Open WebUI, or advanced automations.
