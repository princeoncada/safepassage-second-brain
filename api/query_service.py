from __future__ import annotations

import json
import os
from pathlib import Path
from textwrap import shorten
from typing import Any

from api.audit import write_audit_entry
from api.ingest_service import _ingest_response, _ingest_stream_events
from api.schemas import AskRequest, AskResponse, Source
from rag.query_intent import parse_query_intent
from rag.scripts.answer_vault import (
    PROMPT_PATH,
    build_context_packet,
    call_deepseek,
    call_deepseek_stream,
    chunks_by_ids,
    cited_source_ids,
    insufficient_context_answer,
    lifecycle_advisory_note,
    retrieve_chunks,
    strip_sources_section,
)


AMBIGUOUS_ALIASES_PATH = Path(__file__).resolve().parents[1] / "rag" / "config" / "ambiguous_community_aliases.json"
GENERAL_QUERY_SIGNALS = {
    "default",
    "general",
    "regardless",
    "any community",
    "all communities",
    "standard",
    "global",
    "baseline",
}


def chunk_to_source(chunk: dict[str, Any], show_context: bool) -> Source:
    content = str(chunk.get("content", ""))
    return Source(
        source_id=int(chunk.get("source_id", 0)),
        distance=float(chunk.get("distance", 0.0)),
        title=str(chunk.get("title", "")),
        type=str(chunk.get("type", "")),
        authority_level=str(chunk.get("authority_level", "")),
        scope=str(chunk.get("scope", "")),
        status=str(chunk.get("status", "")),
        lifecycle_status=str(chunk.get("lifecycle_status", "")),
        lifecycle_generation=str(chunk.get("lifecycle_generation", "")),
        temporal_state=str(chunk.get("temporal_state", "")),
        temporal_warning=str(chunk.get("temporal_warning", "")),
        temporal_start_date=str(chunk.get("temporal_start_date", "")),
        temporal_start_field=str(chunk.get("temporal_start_field", "")),
        temporal_end_date=str(chunk.get("temporal_end_date", "")),
        temporal_end_field=str(chunk.get("temporal_end_field", "")),
        announcement_id=str(chunk.get("announcement_id", "")),
        announcement_hash=str(chunk.get("announcement_hash", "")),
        category=str(chunk.get("category", "")),
        normalized_announcement=str(chunk.get("normalized_announcement", "")),
        rerank_score=str(chunk.get("rerank_score", "")),
        rerank_delta=str(chunk.get("rerank_delta", "")),
        rerank_reasons=str(chunk.get("rerank_reasons", "")),
        rule_id=str(chunk.get("rule_id", "")),
        rule_hash=str(chunk.get("rule_hash", "")),
        source_batch=str(chunk.get("source_batch", "")),
        source_name=str(chunk.get("source_name", "")),
        effective_date=str(chunk.get("effective_date", "")),
        active_from=str(chunk.get("active_from", "")),
        start_date=str(chunk.get("start_date", "")),
        active_until=str(chunk.get("active_until", "")),
        expires_at=str(chunk.get("expires_at", "")),
        expiry_date=str(chunk.get("expiry_date", "")),
        end_date=str(chunk.get("end_date", "")),
        expires_on=str(chunk.get("expires_on", "")),
        event_dates=str(chunk.get("event_dates", "")),
        source_legacy_file=str(chunk.get("source_legacy_file", "")),
        source_migration=str(chunk.get("source_migration", "")),
        migration_date=str(chunk.get("migration_date", "")),
        supersedes=str(chunk.get("supersedes", "")),
        superseded_by=str(chunk.get("superseded_by", "")),
        community=str(chunk.get("community", "")),
        section=str(chunk.get("section", "")),
        source_file=str(chunk.get("source_file", "")),
        preview=shorten(" ".join(content.split()), width=240, placeholder="..."),
        content=content if show_context else None,
    )


def source_to_dict(source: Source) -> dict[str, Any]:
    if hasattr(source, "model_dump"):
        return source.model_dump()
    return source.dict()


def build_response(
    *,
    status: str,
    request: AskRequest,
    answer: str,
    chunks: list[dict[str, Any]],
    cited_chunks: list[dict[str, Any]],
    assessment: dict[str, Any],
    hints: dict[str, Any],
    used_ai: bool,
    warnings: list[str],
) -> AskResponse:
    answer_citations = [chunk_to_source(chunk, False) for chunk in cited_chunks]
    seen_files: set[str] = set()
    deduped_citations: list[Source] = []
    for source in answer_citations:
        if source.source_file not in seen_files:
            seen_files.add(source.source_file)
            deduped_citations.append(source)

    return AskResponse(
        status=status,
        question=request.question,
        answer=answer,
        retrieval_confidence=str(assessment.get("confidence", "")),
        confidence_reason=str(assessment.get("reason", "")),
        sources=[chunk_to_source(chunk, request.show_context) for chunk in chunks],
        answer_citations=deduped_citations,
        used_ai=used_ai,
        warnings=warnings,
    )


def load_ambiguous_aliases() -> dict:
    if not AMBIGUOUS_ALIASES_PATH.exists():
        return {}
    with AMBIGUOUS_ALIASES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_ambiguous_community(community: str) -> str:
    """Return a clarification message if community is a known ambiguous parent,
    else return empty string."""
    if not community:
        return ""
    ambiguous = load_ambiguous_aliases()
    for parent_community, config in ambiguous.items():
        if community == parent_community:
            return str(config.get("clarification_message", ""))
    return ""


def resolve_community_from_history(history: list[str]) -> tuple[str, str]:
    try:
        for turn in reversed(history[-5:]):
            intent = parse_query_intent(str(turn))
            if intent.community:
                return intent.community, intent.community_alias
    except Exception:
        pass
    return "", ""


def _is_general_query(text: str) -> bool:
    lowered = text.lower()
    return any(signal in lowered for signal in GENERAL_QUERY_SIGNALS)


def run_query(request: AskRequest) -> AskResponse:
    """
    Full RAG retrieval and answer for a non-ingest question.
    """
    question_stripped = request.question.strip()

    _intent_check = parse_query_intent(question_stripped)
    _clarification = check_ambiguous_community(_intent_check.community)
    if _clarification:
        return _ingest_response(request, _clarification)

    retrieval_question = question_stripped
    _current_intent = parse_query_intent(question_stripped)
    if (
        not _current_intent.community
        and request.history
        and not _is_general_query(question_stripped)
    ):
        _hist_community, _hist_alias = resolve_community_from_history(request.history)
        if _hist_community:
            retrieval_question = f"{question_stripped} {_hist_community}"

    warnings: list[str] = []
    try:
        chunks, hints, assessment = retrieve_chunks(
            retrieval_question,
            request.top_k,
            request.include_low_value_sections,
        )
    except SystemExit as error:
        return build_response(
            status="error",
            request=request,
            answer=str(error),
            chunks=[],
            cited_chunks=[],
            assessment={"confidence": "none", "reason": str(error)},
            hints={},
            used_ai=False,
            warnings=[str(error)],
        )

    context_packet = build_context_packet(chunks)

    if assessment.get("confidence") in {"weak", "none"}:
        warnings.append("retrieved context is weak")
    advisory_note = lifecycle_advisory_note(chunks)
    if advisory_note:
        warnings.append("non-current or uncertain temporal lifecycle context is present; active rules remain authoritative")
    for chunk in chunks:
        if chunk.get("temporal_warning"):
            warnings.append(
                f"source {chunk.get('source_id')} temporal warning: {chunk.get('temporal_warning')}"
            )

    if request.no_ai:
        return build_response(
            status="ok",
            request=request,
            answer="AI skipped because no_ai=true. Retrieved context returned in sources.",
            chunks=chunks,
            cited_chunks=[],
            assessment=assessment,
            hints=hints,
            used_ai=False,
            warnings=warnings,
        )

    if assessment.get("refuse"):
        answer = insufficient_context_answer(str(assessment.get("reason", "")))
        write_audit_entry(
            query=request.question,
            hints=hints,
            assessment=assessment,
            cited_chunks=[],
            answer=answer,
            used_ai=False,
            warnings=warnings,
        )
        return build_response(
            status="ok",
            request=request,
            answer=answer,
            chunks=chunks,
            cited_chunks=[],
            assessment=assessment,
            hints=hints,
            used_ai=False,
            warnings=warnings,
        )

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        message = "DEEPSEEK_API_KEY is not set. Set it in the environment or send no_ai=true to validate retrieval only."
        return build_response(
            status="error",
            request=request,
            answer=message,
            chunks=chunks,
            cited_chunks=[],
            assessment=assessment,
            hints=hints,
            used_ai=False,
            warnings=[message],
        )

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    try:
        retrieval_notes = [str(assessment.get("reason", ""))]
        if advisory_note:
            retrieval_notes.append(advisory_note)
        answer = call_deepseek(api_key, request.question, context_packet, prompt, "\n\n".join(retrieval_notes))
    except SystemExit as error:
        return build_response(
            status="error",
            request=request,
            answer=str(error),
            chunks=chunks,
            cited_chunks=[],
            assessment=assessment,
            hints=hints,
            used_ai=False,
            warnings=[str(error)],
        )

    source_ids = cited_source_ids(answer, chunks)
    cited_chunks = chunks_by_ids(chunks, source_ids)
    answer = strip_sources_section(answer)
    if not cited_chunks:
        warnings.append("generated answer did not include explicit source IDs")

    response = build_response(
        status="ok",
        request=request,
        answer=answer,
        chunks=chunks,
        cited_chunks=cited_chunks,
        assessment=assessment,
        hints=hints,
        used_ai=True,
        warnings=warnings,
    )
    write_audit_entry(
        query=request.question,
        hints=hints,
        assessment=assessment,
        cited_chunks=cited_chunks,
        answer=answer,
        used_ai=True,
        warnings=warnings,
    )
    return response


def run_query_stream(request: AskRequest):
    """
    Streaming generator equivalent of run_query.
    """
    question_stripped = request.question.strip()

    _intent_check = parse_query_intent(question_stripped)
    _clarification = check_ambiguous_community(_intent_check.community)
    if _clarification:
        yield from _ingest_stream_events(_clarification, confidence_reason="ambiguous community")
        return

    retrieval_question = question_stripped
    _current_intent = parse_query_intent(question_stripped)
    if (
        not _current_intent.community
        and request.history
        and not _is_general_query(question_stripped)
    ):
        _hist_community, _ = resolve_community_from_history(request.history)
        if _hist_community:
            retrieval_question = f"{question_stripped} {_hist_community}"

    warnings: list[str] = []
    try:
        chunks, hints, assessment = retrieve_chunks(
            retrieval_question,
            request.top_k,
            request.include_low_value_sections,
        )
    except SystemExit as error:
        payload = json.dumps(
            {
                "answer": str(error),
                "retrieval_confidence": "none",
                "confidence_reason": str(error),
                "sources": [],
                "answer_citations": [],
                "warnings": [str(error)],
                "used_ai": False,
            }
        )
        yield f"data: [CITATIONS]{payload}\n\n"
        yield "data: [DONE]\n\n"
        return

    context_packet = build_context_packet(chunks)

    if assessment.get("confidence") in {"weak", "none"}:
        warnings.append("retrieved context is weak")
    advisory_note = lifecycle_advisory_note(chunks)
    if advisory_note:
        warnings.append(
            "non-current or uncertain temporal lifecycle context is present; "
            "active rules remain authoritative"
        )
    for chunk in chunks:
        if chunk.get("temporal_warning"):
            warnings.append(
                f"source {chunk.get('source_id')} temporal warning: "
                f"{chunk.get('temporal_warning')}"
            )

    if request.no_ai:
        payload = json.dumps(
            {
                "answer": "AI skipped because no_ai=true. Retrieved context returned in sources.",
                "retrieval_confidence": assessment.get("confidence", ""),
                "confidence_reason": assessment.get("reason", ""),
                "sources": [source_to_dict(chunk_to_source(c, request.show_context)) for c in chunks],
                "answer_citations": [],
                "warnings": warnings,
                "used_ai": False,
            }
        )
        yield f"data: [CITATIONS]{payload}\n\n"
        yield "data: [DONE]\n\n"
        return

    if assessment.get("refuse"):
        answer = insufficient_context_answer(str(assessment.get("reason", "")))
        write_audit_entry(
            query=request.question,
            hints=hints,
            assessment=assessment,
            cited_chunks=[],
            answer=answer,
            used_ai=False,
            warnings=warnings,
        )
        payload = json.dumps(
            {
                "answer": answer,
                "retrieval_confidence": assessment.get("confidence", ""),
                "confidence_reason": assessment.get("reason", ""),
                "sources": [source_to_dict(chunk_to_source(c, False)) for c in chunks],
                "answer_citations": [],
                "warnings": warnings,
                "used_ai": False,
            }
        )
        yield f"data: [CITATIONS]{payload}\n\n"
        yield "data: [DONE]\n\n"
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        message = (
            "DEEPSEEK_API_KEY is not set. "
            "Set it in the environment or send no_ai=true to validate retrieval only."
        )
        payload = json.dumps(
            {
                "answer": message,
                "retrieval_confidence": assessment.get("confidence", ""),
                "confidence_reason": assessment.get("reason", ""),
                "sources": [],
                "answer_citations": [],
                "warnings": [message],
                "used_ai": False,
            }
        )
        yield f"data: [CITATIONS]{payload}\n\n"
        yield "data: [DONE]\n\n"
        return

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    retrieval_notes = [str(assessment.get("reason", ""))]
    if advisory_note:
        retrieval_notes.append(advisory_note)

    full_answer_parts: list[str] = []
    try:
        for token in call_deepseek_stream(
            api_key,
            request.question,
            context_packet,
            prompt,
            "\n\n".join(retrieval_notes),
        ):
            full_answer_parts.append(token)
            yield f"data: {json.dumps(token)}\n\n"
    except Exception as error:
        message = f"DeepSeek streaming error: {error}"
        payload = json.dumps(
            {
                "answer": message,
                "retrieval_confidence": assessment.get("confidence", ""),
                "confidence_reason": assessment.get("reason", ""),
                "sources": [],
                "answer_citations": [],
                "warnings": [message],
                "used_ai": False,
            }
        )
        yield f"data: [CITATIONS]{payload}\n\n"
        yield "data: [DONE]\n\n"
        return

    full_answer = "".join(full_answer_parts)
    full_answer = strip_sources_section(full_answer)
    source_ids = cited_source_ids(full_answer, chunks)
    cited_chunks = chunks_by_ids(chunks, source_ids)
    if not cited_chunks:
        warnings.append("generated answer did not include explicit source IDs")

    write_audit_entry(
        query=request.question,
        hints=hints,
        assessment=assessment,
        cited_chunks=cited_chunks,
        answer=full_answer,
        used_ai=True,
        warnings=warnings,
    )

    seen_files: set[str] = set()
    deduped_cited: list[dict[str, Any]] = []
    for chunk in cited_chunks:
        src = chunk_to_source(chunk, False)
        if src.source_file not in seen_files:
            seen_files.add(src.source_file)
            deduped_cited.append(source_to_dict(src))

    payload = json.dumps(
        {
            "answer": full_answer,
            "retrieval_confidence": assessment.get("confidence", ""),
            "confidence_reason": assessment.get("reason", ""),
            "sources": [source_to_dict(chunk_to_source(c, request.show_context)) for c in chunks],
            "answer_citations": deduped_cited,
            "warnings": warnings,
            "used_ai": True,
        }
    )
    yield f"data: [CITATIONS]{payload}\n\n"
    yield "data: [DONE]\n\n"
