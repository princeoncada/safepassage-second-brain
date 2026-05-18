from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.dashboard import router as dashboard_router
from api.schemas import AskRequest, AskResponse
from api.service import answer_question, stream_answer_question


app = FastAPI(
    title="SafePassage Second Brain Local API",
    version="0.1.0",
    description="Local-first API wrapper for the Phase 3 RAG answer pipeline.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
# Open WebUI slash command ingestion is routed inside api.service.answer_question().


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return answer_question(request)


@app.post("/ask/stream")
def ask_stream(request: AskRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_answer_question(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
