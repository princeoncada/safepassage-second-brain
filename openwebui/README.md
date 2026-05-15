# Phase 3E Open WebUI Integration

Open WebUI is the presentation layer only.

The operational brain remains:

```text
Open WebUI
-> local FastAPI /ask endpoint
-> RAG retrieval
-> grounded answering
-> citations/refusal/confidence
```

Do not move retrieval, embeddings, ChromaDB, memory, ingestion, or business logic into Open WebUI.

## Prerequisites

1. ChromaDB index has been built.
2. FastAPI is running locally.
3. `DEEPSEEK_API_KEY` is set if using AI mode.
4. Open WebUI can reach the FastAPI host.

Install and start the local API:

```powershell
pip install -r rag/requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

Test the API directly before configuring Open WebUI:

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

## Recommended Open WebUI Connection

Use a minimal Open WebUI connector or Pipe that forwards the latest user question to:

```text
POST http://localhost:8000/ask
```

If Open WebUI runs in Docker and FastAPI runs on the host, use:

```text
POST http://host.docker.internal:8000/ask
```

Request body:

```json
{
  "question": "<latest user message>",
  "top_k": 5,
  "show_context": false,
  "no_ai": false
}
```

Display these response fields in the chat answer:

- `answer`
- `retrieval_confidence`
- `confidence_reason`
- `answer_citations`
- `warnings`

This connector is only a presentation bridge. It should not add Open WebUI tool calling, agents, direct ChromaDB access, or vault writes.

## Suggested UI Formatting

Use a concise answer layout:

```text
<answer>

Confidence: <retrieval_confidence>
Reason: <confidence_reason>

Sources:
[1] <source_file> - <section>
[2] <source_file> - <section>

Warnings:
- <warning>
```

Do not hide insufficient-context refusals. They are an expected safety behavior.

## Example Prompts

- `What are Sierra Ridge overnight visitor ID rules?`
- `What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?`
- `What happened with tailgating at Monterey?`
- `What is the vehicle policy for Atlantis Bay?`

Expected:

- Sierra Ridge questions answer from post order or QA rule sources.
- Monterey question answers from incident sources.
- Atlantis Bay refuses because no matching source exists.

## Operational Boundaries

Open WebUI should not:

- directly modify `vault/`;
- directly write memory;
- bypass FastAPI;
- bypass retrieval safeguards;
- call ChromaDB directly;
- store operational source of truth;
- trigger workflow automation;
- perform Git operations.

## Future Work Deferred

- agents;
- autonomous memory;
- auto-updating vaults;
- automatic SOP generation;
- proactive workflows;
- automation triggers;
- direct vault editing from chat.

## Validation

Open WebUI integration passes when:

- the UI can call the local FastAPI backend;
- grounded answers appear in chat;
- citations appear;
- retrieval confidence appears;
- Atlantis Bay refuses safely;
- existing CLI and `/ask` API still work.
