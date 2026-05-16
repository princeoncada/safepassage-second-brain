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

Phase 2 Minimal POW, Phase 3A Retrieval POW, Phase 3B Grounded Answering POW, Phase 3C RAG Quality Hardening, Phase 3D Local API Wrapper, Phase 3E Open WebUI integration, Phase 4A retrieval hardening, Phase 4B primary workflow ingestion, Phase 4B2 fallback confidence, Phase 4C post-order refresh, Phase 4C1 lifecycle retrieval hardening, Phase 4C2 managed post-order conversion, Phase 4C3 announcement ingestion, and Phase 4D query intent parsing have passed or mostly passed local validation. Phase 4E OCR intake is the current manual-validation phase. The system is a working proof of work, not a finished final product.

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
2. Citations can still be incomplete if DeepSeek omits explicit source IDs. Future fix: stricter answer post-validation or retry.
3. Retrieval ranking remains heuristic. Future fix: measured reranking tests over a larger vault.
4. Source numbering depends on the model citing retrieved source IDs exactly. Future fix: reject or retry missing citation IDs.
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
- Open WebUI remains presentation-only and does not bypass FastAPI.

## Phase 3E Open WebUI Validation

First validate FastAPI directly:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Then configure Open WebUI to call:

```text
POST http://localhost:8000/ask
```

If Open WebUI runs in Docker and FastAPI runs on the host:

```text
POST http://host.docker.internal:8000/ask
```

Validate these prompts in Open WebUI:

```text
What are Sierra Ridge overnight visitor ID rules?
What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?
What happened with tailgating at Monterey?
What is the vehicle policy for Atlantis Bay?
```

Expected:

- grounded answers appear in the UI;
- citations appear;
- retrieval confidence appears;
- Atlantis Bay refuses safely;
- no hallucinated policy appears;
- existing CLI scripts and FastAPI `/ask` still work.

## Phase 4A Retrieval Quality Hardening Validation

Rebuild the disposable ChromaDB index:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Validate retrieval reranking and dedupe:

```powershell
python rag/scripts/query_vault.py "overnight visitors must present physical ID before access" --top-k 5
python rag/scripts/query_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/query_vault.py "What should the agent do if digital ID is presented instead of physical ID?" --top-k 5
```

Expected:

- Sierra Ridge `post_order` appears in top results for physical ID.
- Monterey `incident` appears in top results for tailgating.
- Sierra Ridge `qa_rule` and/or `post_order` appears in top results for digital ID.
- `Agent Action`, `Summary`, and `Details` are preferred where available.
- `QA Notes` can appear when relevant but should not dominate factual/policy queries.
- `Open Questions`, `Source Input`, and `Change History` are excluded by default.
- duplicate near-identical sources are reduced.

Validate answer citation cleanup:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Expected:

- generated answers cite only useful supporting sources;
- only one `Sources` section appears in CLI/API-rendered output;
- Source IDs in citations match retrieved Source IDs;
- Atlantis Bay refuses safely and does not cite unrelated sources as support.

Validate FastAPI compatibility:

```powershell
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

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

Expected:

- response still includes `status`, `question`, `answer`, `retrieval_confidence`, `confidence_reason`, `sources`, `answer_citations`, `used_ai`, and `warnings`;
- `answer` does not contain a duplicate trailing `Sources:` block;
- `answer_citations` contains only sources cited by the answer;
- Open WebUI pipe compatibility is preserved.

## Phase 4B Primary Workflow Ingestion Validation

Create primary workflow Markdown from the structured sample:

```powershell
python automation/ingestion/ingest_primary_workflow.py
```

Expected:

- files are written to `vault/09_SOPs/`;
- filenames use the `primary-*.md` pattern;
- frontmatter includes `type: "workflow"` and `authority_level: "primary_workflow"`;
- existing files are skipped unless `--force` is passed.

Rebuild the disposable index:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Validate default workflow retrieval:

```powershell
python rag/scripts/query_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
```

Expected:

- retrieves `primary-no-physical-id`;
- answer says "Based on the primary workflow" or "Default workflow says";
- answer says no physical ID means deny entry, subject to higher-authority overrides.

Validate community-specific override behavior:

```powershell
python rag/scripts/query_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Expected:

- Sierra Ridge QA/post order sources outrank primary workflow;
- primary workflow is not treated as equal authority.

Validate default call attempts:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- answer says default is twice;
- answer says to check community post orders for accuracy.

Validate unknown community fallback:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident for Atlantis Bay?" --top-k 5
```

Expected:

- answer says no Atlantis Bay-specific source exists;
- answer may mention primary workflow only as global default guidance;
- answer does not invent Atlantis Bay-specific policy.

## Phase 4B2 Primary Workflow Fallback Confidence Validation

Default workflow fallback:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- does not refuse;
- cites `vault/09_SOPs/primary-call-attempts-by-community.md`;
- says the default workflow is to call the resident twice;
- warns that community post orders may differ.

Unknown community-specific question:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident for Atlantis Bay?" --top-k 5
```

Expected:

- refuses safely;
- says no Atlantis Bay-specific source exists;
- does not invent Atlantis Bay policy.

Higher authority still wins:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Expected:

- Sierra Ridge post order or QA rule remains prioritized;
- primary workflow does not override post orders.

Unrelated unknown community policy:

```powershell
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Expected:

- refuses safely.

## Phase 4C Batch Post Order Refresh Validation

Dry run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
```

Expected:

- parses Clearbrook Main with community code `CBK`;
- parses all `POST ORDER (...)`, `POST ORDERS (...)`, `K&C`, `K & C`, and `K and C` entries;
- maps `C` to concierge, not call center;
- treats the batch as `update_type: partial`;
- prints added, duplicate, superseded, conflict, possible changes/review, missing, and manual review sections;
- skips missing-rule replacement handling because the batch is partial;
- writes no vault files.

Real run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Expected:

- creates active post order Markdown files or identifies duplicates;
- writes near-topic conservative changes as `status: review` instead of silently superseding;
- writes a refresh report under `vault/08_Reports/post-order-refresh/`;
- does not delete old files.

Re-run same batch:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Expected:

- no duplicate active rules are created;
- report says unchanged/duplicate.

Reindex:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Expected:

- new post order lifecycle metadata does not break indexing;
- active post orders are indexed;
- superseded/conflict/review/inactive rules are penalized in retrieval.

Retrieval sanity:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- Sierra Ridge still uses post orders;
- Atlantis Bay still refuses safely;
- default call attempts still uses primary workflow fallback;
- no regression from Phase 4B2.

## Phase 4C1 Lifecycle Retrieval Hardening Validation

Rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Lifecycle and alias tests:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
python rag/scripts/answer_vault.py "What is the CBK rule for physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the emergency code for Clearbrook Main?" --top-k 5
python rag/scripts/query_vault.py "Sierra Ridge physical ID" --top-k 10
```

Expected:

- active lifecycle-managed post orders dominate normal retrieval;
- legacy post-order documents are skipped by default and do not pollute top results;
- Atlantis Bay still refuses safely;
- primary workflow fallback still answers default/base workflow questions;
- `CBK` expands to Clearbrook Main and reduces Sierra Ridge drift;
- Clearbrook emergency code answers from the active code and warns that the newer `pending` code is advisory;
- superseded and archived rules do not outrank active rules.

## Phase 4C2 Legacy Post Order Migration Validation

The user runs this validation manually after reviewing the migration output.

Migration dry run:

```powershell
python automation/ingestion/migrate_legacy_post_orders.py --dry-run
```

Real migration:

```powershell
python automation/ingestion/migrate_legacy_post_orders.py
```

Rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Retrieval and answer checks:

```powershell
python rag/scripts/query_vault.py "Sierra Ridge physical ID" --top-k 10
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- Sierra Ridge physical ID queries retrieve managed active `post_order` sources first;
- the QA rule can still appear as supporting compliance context;
- legacy source files remain preserved;
- duplicate managed rules are skipped by `rule_hash`;
- Atlantis Bay still refuses safely;
- primary workflow fallback still works.

## Phase 4C3 Announcement / Reminder Lifecycle Ingestion Validation

The user runs this validation manually after reviewing the announcement refresh output.

Announcement dry run:

```powershell
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md --dry-run
```

Real announcement refresh:

```powershell
python automation/ingestion/refresh_announcements.py --input automation/ingestion/sample_announcement_batch.md
```

Rebuild:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Retrieval and answer checks:

```powershell
python rag/scripts/query_vault.py "What is the Red Zone Protocol expiration?" --top-k 5
python rag/scripts/query_vault.py "What are the CBK pickleball tournament reminders?" --top-k 5
python rag/scripts/answer_vault.py "What should I know about SR kiosk audio?" --top-k 5
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Expected:

- announcement documents are created under `vault/05_Announcements/`;
- refresh report is created under `vault/08_Reports/announcement-refresh/`;
- `CBK` maps to Clearbrook Main and `SR` maps to Sierra Ridge;
- global reminders retrieve as `community: global`;
- pending or expired announcements are advisory or penalized;
- post orders still outrank announcements for policy questions.

## Phase 4D Operational Query Parser Validation

The user runs this validation manually after reviewing the query intent changes.

Rebuild only if announcement or vault content changed:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Red Zone Protocol topic parsing:

```powershell
python rag/scripts/query_vault.py "What is the Red Zone Protocol reminder?" --top-k 5
python rag/scripts/answer_vault.py "What is the Red Zone Protocol reminder?" --top-k 5
```

Expected:

- intent category is `temporary_protocol` or announcement/reminder-related;
- `Red Zone Protocol` is shown as a topic term, not a missing community;
- expected type includes `announcement`;
- answer uses the global announcement context if indexed.

Unknown community refusal:

```powershell
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
```

Expected:

- Atlantis Bay is treated as a missing community hint;
- the answer refuses safely;
- no Atlantis Bay policy is invented.

Authority and fallback regression checks:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- Sierra Ridge policy still prioritizes managed post orders and supporting QA context;
- primary workflow fallback still answers explicit default workflow questions;
- post orders still outrank announcements and primary workflow.

## Phase 4E OCR Intake Validation

The user runs this validation manually after installing a local OCR engine.

Optional OCR dependencies:

```powershell
pip install paddleocr paddlepaddle pillow
```

Fallback option:

```powershell
pip install pytesseract pillow
```

Tesseract fallback also requires the local Tesseract binary installed on Windows.

Single-image OCR:

```powershell
python automation/ocr/ocr_extract.py --input automation/ocr/sample_images/example.png
```

Folder OCR:

```powershell
python automation/ocr/ocr_extract.py --input-dir automation/ocr/sample_images
```

Expected:

- one raw `.txt` file is written per image under `automation/ocr/output/`;
- one review `.md` file is written per image under `automation/ocr/output/`;
- review Markdown includes source image, created timestamp, OCR engine, confidence when available, extracted text, review notes, and raw OCR text;
- OCR cleanup preserves aliases such as `CBK`, `PBP`, `SR`, `SSR`, and `OPB`;
- OCR does not write to `vault/`;
- OCR does not call announcement or post-order ingestion scripts;
- human review is required before copied OCR text enters an ingestion input.
