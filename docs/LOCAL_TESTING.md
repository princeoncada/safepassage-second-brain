# Local Testing

## Purpose

This guide covers local validation for the Phase 2 ingestion workflow. These steps must be run by a human in the local environment before Phase 2 can be marked complete.

## Validate JSON Files

```powershell
Get-Content workflows/n8n/phase_2_ingestion_workflow.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/test_webhook_payload.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/ingestion_contract.json | ConvertFrom-Json | Out-Null
Get-Content automation/ingestion/routing_rules.json | ConvertFrom-Json | Out-Null
```

## Validate Helper Scripts

Run from the repository root:

```powershell
node automation/scripts/sanitize_filename.js "Sierra Ridge: After Hours Visitor ID.md"
```

Expected:

```text
sierra-ridge-after-hours-visitor-id.md
```

Validate a sample canonical payload:

```powershell
Get-Content docs/examples/ingestion_payload.json | node automation/scripts/validate_payload.js
```

The existing example has empty required fields, so it should fail. Use this to confirm validation catches incomplete payloads.

## Test Webhook Payloads

Use examples from:

```text
automation/ingestion/test_webhook_payload.json
```

Recommended order:

1. Unknown input
2. Automation planning note
3. Post order update
4. Incident report

## Manual Webhook Test

In n8n:

1. Import `workflows/n8n/phase_2_ingestion_workflow.json`.
2. Open the workflow.
3. Start a manual test execution.
4. Copy the test webhook URL from the webhook node.
5. Send one example body from `automation/ingestion/test_webhook_payload.json`.

Example shape:

```json
{
  "input_text": "Need to remember the thing from yesterday before the next shift.",
  "source": "manual_webhook_test",
  "community": "",
  "received_at": "2026-05-14T15:00:00-04:00"
}
```

## Validate Results

After a test execution, confirm:

- The classifier returns one supported document type or `unknown`.
- The router selects the expected target folder.
- The normalizer returns Markdown with required YAML frontmatter.
- The QA checker returns `requires_human_review`.
- Review-required items write to `vault/00_Inbox`.
- Non-review items write to their routed folder.
- Git commit and push only run after the Markdown write succeeds.

## Do Not Claim Completion Yet

Do not mark Phase 2 complete until local testing confirms:

- n8n imports the workflow successfully.
- DeepSeek API calls work using `DEEPSEEK_API_KEY`.
- Markdown writes succeed.
- Git commits and pushes succeed on `master`.
- No secrets are written to the vault.
