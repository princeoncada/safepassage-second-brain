from __future__ import annotations

import json

from api.ingest import (
    get_wizard_step,
    handle_announcements_command,
    handle_confirm_no,
    handle_confirm_yes,
    handle_keep_new,
    handle_keep_old,
    handle_post_orders_command,
    handle_wizard_community,
    handle_wizard_text,
    has_pending_wizard,
)
from api.schemas import AskRequest, AskResponse


def handle_ingest_turn(question: str) -> str | None:
    """
    Check if the question is a slash command, wizard reply, or
    confirmation (YES/NO/KEEP NEW/KEEP OLD).
    Returns the ingest response text if handled, or None if this
    is a normal RAG query.
    """
    question_upper = question.upper()

    if has_pending_wizard():
        step = get_wizard_step()
        if step == "awaiting_community":
            return handle_wizard_community(question)
        if step == "awaiting_text":
            return handle_wizard_text(question)

    if question_upper == "KEEP NEW":
        return handle_keep_new()
    if question_upper == "KEEP OLD":
        return handle_keep_old()

    if question.lower().startswith("/post-orders"):
        return handle_post_orders_command(question)
    if question.lower().startswith("/announcements"):
        return handle_announcements_command(question)

    if question_upper == "YES":
        return handle_confirm_yes()
    if question_upper == "NO":
        return handle_confirm_no()

    return None


def _ingest_response(request: AskRequest, answer_text: str) -> AskResponse:
    return AskResponse(
        status="ok",
        question=request.question,
        answer=answer_text,
        retrieval_confidence="1.0",
        confidence_reason="Open WebUI slash command handled by deterministic ingestion flow.",
        sources=[],
        answer_citations=[],
        used_ai=False,
        warnings=[],
    )


def _ingest_stream_events(answer_text: str, confidence_reason: str = "slash command"):
    payload = json.dumps(
        {
            "answer": answer_text,
            "retrieval_confidence": "1.0",
            "confidence_reason": confidence_reason,
            "sources": [],
            "answer_citations": [],
            "warnings": [],
            "used_ai": False,
        }
    )
    yield f"data: [CITATIONS]{payload}\n\n"
    yield "data: [DONE]\n\n"
