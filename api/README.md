# SafePassage Local API

Phase 3D exposes the existing RAG answer pipeline through a local FastAPI server.

This is only an interface wrapper. It does not add Open WebUI, n8n integration, agents, autonomous memory editing, Git auto-commit, dashboards, voice, or Phase 4 automations.

## Install

```powershell
pip install -r rag/requirements.txt
```

## Start Server

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

## Ask With AI

Set the key:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Call the local API:

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

## Retrieval Only

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

## Response Shape

```json
{
  "status": "ok",
  "question": "",
  "answer": "",
  "retrieval_confidence": "",
  "confidence_reason": "",
  "sources": [],
  "answer_citations": [],
  "used_ai": true,
  "warnings": []
}
```

If `DEEPSEEK_API_KEY` is missing and `no_ai` is false, the API returns `status: "error"` with a clear message suggesting `no_ai: true`.
