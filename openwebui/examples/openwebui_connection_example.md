# Open WebUI Connection Example

This is an example of the logic an Open WebUI connector or Pipe should perform. Keep the real RAG logic in FastAPI and do not add tool calling, agents, direct ChromaDB access, or vault writes.

## Endpoint

If Open WebUI is running directly on the host:

```text
http://localhost:8000/ask
```

If Open WebUI is running in Docker and FastAPI is running on the host:

```text
http://host.docker.internal:8000/ask
```

## Request

```json
{
  "question": "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?",
  "top_k": 5,
  "show_context": false,
  "no_ai": false
}
```

## Response Fields To Render

```json
{
  "status": "ok",
  "question": "...",
  "answer": "...",
  "retrieval_confidence": "strong",
  "confidence_reason": "...",
  "sources": [],
  "answer_citations": [],
  "used_ai": true,
  "warnings": []
}
```

## Suggested Render Template

```text
{{ answer }}

Confidence: {{ retrieval_confidence }}
Reason: {{ confidence_reason }}

Sources:
{{ for source in answer_citations }}
[{{ source.source_id }}] {{ source.source_file }} - {{ source.section }}
{{ end }}

Warnings:
{{ for warning in warnings }}
- {{ warning }}
{{ end }}
```

## No-AI Retrieval Check

```json
{
  "question": "What are Sierra Ridge overnight visitor ID rules?",
  "top_k": 5,
  "show_context": true,
  "no_ai": true
}
```

Use this first to confirm Open WebUI can reach the backend before enabling DeepSeek answer generation.
