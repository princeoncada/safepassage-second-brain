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
  "question": "do you have any information on SR?",
  "top_k": 5,
  "show_context": false,
  "no_ai": false,
  "history": [
    "/post-orders SR 5/17/2026 Post Order (K): Contact the resident twice for access."
  ]
}
```

## Conversation Context

The `history` field is optional. Omit it or pass `[]` for stateless queries.

Pass up to 5 prior user turn strings. Include questions only, not assistant answers.

The backend uses history only to resolve community/topic context when the current question is ambiguous. It does not send history to DeepSeek.

In an Open WebUI Pipe, build history from `messages[:-1]` (all turns except the current one), extracting only `role=user` content strings:

```python
history = [m["content"] for m in body.get("messages", [])[:-1] if m.get("role") == "user"]
history = history[-5:]
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

## Streaming Pipe (Recommended)

For live token streaming (ChatGPT/Claude-style), install the pipe at
`openwebui/pipe.py` instead of a manual connector.

Install steps:
1. Open WebUI > Workspace > Pipes > New Pipe
2. Paste the contents of `openwebui/pipe.py`
3. Set BASE_URL in Valves to your FastAPI host
4. Save and enable the pipe

The pipe calls `/ask/stream` and yields tokens live. Citations, confidence,
and warnings appear at the end of each response.

The non-streaming `/ask` endpoint remains available for API clients
and validation scripts.
