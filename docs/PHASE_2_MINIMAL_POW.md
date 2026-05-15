# Phase 2 Minimal Proof of Work

## Purpose

This workflow is a deterministic, cheap ingestion proof of work for SafePassage operational notes. It validates and routes input with JavaScript first, uses DeepSeek at most once for optional Markdown body cleanup, and always falls back to deterministic Markdown if DeepSeek is unavailable.

Import this workflow into n8n:

```text
workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json
```

## Command Prefix Usage

Put a command prefix at the start of `input_text` to override keyword classification:

| Prefix | Classification | Target folder |
|---|---|---|
| `/post` | `post_order` | `vault/03_Post_Orders` |
| `/incident` | `incident` | `vault/06_Incidents` |
| `/qa` | `qa_rule` | `vault/04_QA_Rules` |
| `/log` | `visitor_log` | `vault/07_Visitor_Logs` |
| `/automation` | `automation` | `vault/10_Automations` |
| `/workflow` | `workflow` | `vault/10_Automations` |
| `/help` | `help_response` | No file write |

Prefixes reduce AI usage because classification, routing, priority, review status, filename generation, YAML frontmatter, validation, and file writing are handled by deterministic JavaScript. DeepSeek is only asked to clean the body sections of Markdown and is never allowed to classify, route, or generate frontmatter.

## Manual Setup

1. Import `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json` into n8n.
2. Open `HTTP - Optional DeepSeek Markdown Cleanup`.
3. Replace `Bearer REPLACE_WITH_DEEPSEEK_API_KEY` with a real DeepSeek API key.
4. Confirm the n8n container or host can write to `/data/vault`.

Do not configure credentials or environment expressions for this proof of work. The placeholder key must be replaced manually in the HTTP node.

## Curl Tests

Use the production webhook URL after the workflow is active:

```bash
curl -sS -X POST http://localhost:5678/webhook/phase-2-minimal-pow-ingest \
  -H "Content-Type: application/json" \
  -d '{"input_text":"/post For Sierra Ridge, all overnight visitors must present physical ID before access is granted.","source":"manual_test","community":"Sierra Ridge"}'
```

```bash
curl -sS -X POST http://localhost:5678/webhook/phase-2-minimal-pow-ingest \
  -H "Content-Type: application/json" \
  -d '{"input_text":"/qa Always follow physical ID requirements. Digital ID should not be accepted when post order requires physical ID.","source":"manual_test","community":"global"}'
```

```bash
curl -sS -X POST http://localhost:5678/webhook/phase-2-minimal-pow-ingest \
  -H "Content-Type: application/json" \
  -d '{"input_text":"/incident A vehicle tailgated through the resident lane at Monterey.","source":"manual_test","community":"Monterey"}'
```

```bash
curl -sS -X POST http://localhost:5678/webhook/phase-2-minimal-pow-ingest \
  -H "Content-Type: application/json" \
  -d '{"input_text":"/log tag: ABC123 resident: John Doe visitor: Uber Eats","source":"manual_test","community":"Sierra Ridge"}'
```

```bash
curl -sS -X POST http://localhost:5678/webhook/phase-2-minimal-pow-ingest \
  -H "Content-Type: application/json" \
  -d '{"input_text":"/help","source":"manual_test","community":"global"}'
```

For manual test executions inside the editor, use:

```text
http://localhost:5678/webhook-test/phase-2-minimal-pow-ingest
```

## Expected Folder Output

| Input | Expected folder |
|---|---|
| `/post ...` | `/data/vault/03_Post_Orders` |
| keyword post order | `/data/vault/03_Post_Orders` |
| `/qa ...` | `/data/vault/04_QA_Rules` |
| `/incident ...` | `/data/vault/06_Incidents` |
| `/log ...` | `/data/vault/07_Visitor_Logs` |
| unknown input | `/data/vault/00_Inbox` |
| `/help` | No file write |

Filenames use:

```text
yyyy-mm-dd-community-short-topic-classification.md
```

If a file already exists, the workflow appends `hhmmss` before `.md`.

## DeepSeek Fallback

The HTTP node has `continueOnFail` enabled. If DeepSeek fails, returns malformed data, or returns JSON that cannot be parsed, the workflow builds deterministic fallback sections from `input_text` and still writes Markdown.

DeepSeek must return JSON only:

```json
{
  "summary": "",
  "details": "",
  "agent_action": "",
  "qa_notes": "",
  "open_questions": []
}
```

DeepSeek must not generate YAML frontmatter. The Code node always builds the final Markdown and validates that all required YAML fields exist before writing.
