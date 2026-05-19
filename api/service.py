from __future__ import annotations

from api.ingest_service import _ingest_response, _ingest_stream_events, handle_ingest_turn
from api.query_service import run_query, run_query_stream
from api.schemas import AskRequest, AskResponse


def answer_question(request: AskRequest) -> AskResponse:
    answer_text = handle_ingest_turn(request.question.strip())
    if answer_text is not None:
        return _ingest_response(request, answer_text)
    return run_query(request)


def stream_answer_question(request: AskRequest):
    """
    Generator for /ask/stream. Yields SSE-formatted strings.

    Slash command and ingest flows are handled before normal RAG
    streaming and return a single synthetic SSE response.
    """
    answer_text = handle_ingest_turn(request.question.strip())
    if answer_text is not None:
        yield from _ingest_stream_events(answer_text)
        return
    yield from run_query_stream(request)
