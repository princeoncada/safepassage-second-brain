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
- [ ] `docs/PHASE_LOG.md` reflects the current checkpoint status.
- [ ] No unplanned features are added beyond the current checkpoint scope.
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

## Current Checkpoint Status

Phase 2 Minimal POW, Phase 3A Retrieval POW, and Phase 3B Grounded Answering POW passed on 2026-05-15. The system is a working proof of work, not a finished final product.

## Phase 2 Minimal POW Validated Tests

Validated outcomes:

- `/help` returned usage and wrote no file.
- `/qa` routed to `vault/04_QA_Rules`.
- `/incident` routed to `vault/06_Incidents`.
- `/log` routed to `vault/07_Visitor_Logs`.
- unknown input routed to `vault/00_Inbox`.
- `/post` routed to `vault/03_Post_Orders`.
- invalid DeepSeek key still produced fallback Markdown and wrote a file.

Stable workflow:

```text
workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json
```

## Phase 3A RAG Validation

Install dependencies:

```powershell
pip install -r rag/requirements.txt
```

Build the local disposable ChromaDB index:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Validated index result:

```text
Indexed 26 chunks from 7 files after filtering
Skipped low-value sections: 21
Skipped duplicate chunks: 2
```

The index excludes `Change History`, `Open Questions`, and `Source Input` by default because those sections are boilerplate-heavy and polluted top results during retrieval testing. Preferred sections are `Summary`, `Details`, `Agent Action`, and `QA Notes`.

Run retrieval-only test queries:

```powershell
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
```

Expected results are documented in `rag/tests/expected_results.md`. Phase 3A passed: relevant chunks were retrieved, low-value sections were filtered, and duplicate-looking results were reduced. Phase 3A does not generate AI answers.

Reset the index when needed:

```powershell
python rag/scripts/reset_chroma.py --yes
```

Then rebuild:

```powershell
python rag/scripts/index_vault.py
```

To debug excluded sections:

```powershell
python rag/scripts/index_vault.py --include-low-value-sections
python rag/scripts/query_vault.py "What are Sierra Ridge physical ID rules?" --include-low-value-sections --top-k 5
```

## Phase 3B Answer Validation

Set the DeepSeek key in PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Run grounded answer tests:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Retrieval-only validation:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

Expected results are documented in `rag/tests/answer_expected_results.md`. Phase 3B passed: the first three questions answered from retrieved context, citations were included, and Atlantis Bay refused with insufficient context.

## Known Issues / Next Refinements

These are not blockers.

1. Duplicate source files still appear in retrieval results. Future fix: stronger dedupe by normalized title + section + community, or clean duplicate test files.
2. Citations currently list all retrieved chunks, including weak or less relevant chunks. Future fix: cite only chunks actually used.
3. Retrieval ranking can place QA Notes above Summary or Details. Future fix: section weighting or reranking.
4. Source numbering between generated answer and printed citation list can be confusing. Future fix: align citation numbering.
5. Titles and filenames are too verbose. Future fix: deterministic title and filename compression.
6. Incident documents need richer structured fields. Future fix: add time, lane, vehicle details, action taken, escalation, and camera reference.
7. Open Questions may contain generic AI filler. Future fix: include them only when confidence is low or required fields are missing.
8. Git auto-commit remains deferred. Future fix: add controlled sync later.

## Phase 3C RAG Quality Hardening Validation

Rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Retrieval:

```powershell
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
```

Expected:

- Sierra Ridge `post_order` appears top 3 for physical ID.
- Monterey `incident` appears top 3 for tailgating.
- Sierra Ridge `qa_rule` appears top 3 for digital ID.
- low-value sections do not dominate.
- duplicate near-identical chunks are reduced.

Answering:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context --top-k 5
```

Expected:

- answer citations are limited to sources actually cited by the generated answer;
- Atlantis Bay refuses before inventing a policy;
- output shows retrieval confidence and refusal reason when context is weak.

The user will manually review and commit Phase 3C changes.

## Phase 3D Local API Validation

Install dependencies:

```powershell
pip install -r rag/requirements.txt
```

Start the server:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

AI mode:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?",
    "top_k":5
  }'
```

No-AI mode:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What are Sierra Ridge overnight visitor ID rules?",
    "top_k":5,
    "no_ai":true,
    "show_context":true
  }'
```

Insufficient context:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/ask" `
  -ContentType "application/json" `
  -Body '{
    "question":"What is the vehicle policy for Atlantis Bay?",
    "top_k":5
  }'
```

Expected:

- `/ask` returns grounded answer with citations in AI mode.
- `no_ai=true` returns retrieved sources without DeepSeek.
- Atlantis Bay refuses safely.
- existing CLI scripts still work.
- no Open WebUI integration exists yet.
