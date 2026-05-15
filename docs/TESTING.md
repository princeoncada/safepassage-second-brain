# Testing

## Phase 2 Validation Checklist

- [ ] All required prompt files exist.
- [ ] `automation/ingestion/ingestion_contract.json` is valid JSON.
- [ ] `automation/ingestion/routing_rules.json` is valid JSON.
- [ ] `automation/ingestion/sample_inputs.json` is valid JSON.
- [ ] `automation/ingestion/sample_outputs.json` is valid JSON.
- [ ] Sample inputs cover at least one post order, one incident, and one automation note.
- [ ] Sample outputs include classification, priority, target folder, filename, QA risk, and normalized Markdown.
- [ ] `workflows/n8n/phase_2_ingestion_workflow.json` is valid JSON and imports into n8n.
- [ ] Helper scripts exist in `automation/scripts/`.
- [ ] `automation/ingestion/test_webhook_payload.json` is valid JSON and includes post order, incident, automation, and unknown examples.
- [ ] `docs/WORKFLOWS.md` explains the ingestion flow.
- [ ] `workflows/n8n/PHASE_2_INGESTION_WORKFLOW.md` explains the n8n workflow design.
- [ ] `docs/N8N_SETUP.md` explains local n8n import and configuration.
- [ ] `docs/LOCAL_TESTING.md` explains local validation.
- [ ] `docs/AI_HANDOFF.md` explains how future AI should continue.
- [ ] `docs/PHASE_LOG.md` shows Phase 2 as in progress, not complete.
- [ ] No Phase 3 implementation files are added.
- [ ] No secrets are committed.

## Practical Test Cases

### Test 1: Post Order Routing

Input:

```text
For Sierra Ridge, overnight guards must verify a physical photo ID for all after-hours visitors before granting access.
```

Expected:

- Classification: `post_order`
- Priority: `high`
- Target folder before review routing: `vault/03_Post_Orders`
- Final write folder: `vault/00_Inbox` when QA review is required
- QA review: required because this affects access control

### Test 2: Incident Routing

Input:

```text
At Harbor Point, the east gate arm stayed open after a vendor truck exited.
```

Expected:

- Classification: `incident`
- Target folder before review routing: `vault/06_Incidents`
- Final write folder: `vault/00_Inbox` when QA review is required
- QA review: required because this affects access control and follow-up

### Test 3: Unknown Routing

Input:

```text
Need to remember this thing from yesterday.
```

Expected:

- Classification: `unknown`
- Target folder: `vault/00_Inbox`
- QA review: required because the content lacks operational context

### Test 4: Automation Note Routing

Input:

```text
Create an n8n workflow later that accepts a webhook from the operations form and writes Markdown to the vault.
```

Expected:

- Classification: `automation`
- Target folder: `vault/10_Automations`
- QA review: not required unless credentials or risky implementation details are included

## Command-Line Validation

Run these checks before committing Phase 2 work:

```powershell
git status --short
Get-Content automation/ingestion/ingestion_contract.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/routing_rules.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/sample_inputs.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/sample_outputs.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/test_webhook_payload.json | ConvertFrom-Json | Out-Null
Get-Content workflows/n8n/phase_2_ingestion_workflow.json | ConvertFrom-Json | Out-Null
node automation/scripts/sanitize_filename.js "Sierra Ridge: After Hours Visitor ID.md"
rg -n "DEEPSEEK_API_KEY=sk-|api[_-]?key\\s*[:=]\\s*['\\\"][A-Za-z0-9]" .
```

The secret scan should return no real secrets. Placeholder values in `.env.example` are acceptable.

## Local Execution Status

Do not mark Phase 2 complete until a human validates the workflow in local n8n. Repository-level JSON and script checks are not the same as confirming DeepSeek API calls, vault writes, or Git pushes.

## Phase 3A RAG Validation

Install dependencies:

```powershell
pip install -r rag/requirements.txt
```

Build the local disposable ChromaDB index:

```powershell
python rag/scripts/index_vault.py
```

Run retrieval-only test queries:

```powershell
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?"
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?"
python rag/scripts/query_vault.py "What should I do if a digital ID is accepted when physical ID is required?"
```

Expected results are documented in `rag/tests/expected_results.md`. Phase 3A passes only when relevant chunks are retrieved; it does not generate AI answers.

Reset the index when needed:

```powershell
python rag/scripts/reset_chroma.py --yes
```
