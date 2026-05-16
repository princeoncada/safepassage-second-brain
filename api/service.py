from __future__ import annotations

import os
from textwrap import shorten
from typing import Any

from api.schemas import AskRequest, AskResponse, Source
from rag.scripts.answer_vault import (
    PROMPT_PATH,
    build_context_packet,
    call_deepseek,
    chunks_by_ids,
    cited_source_ids,
    insufficient_context_answer,
    retrieve_chunks,
    strip_sources_section,
)


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
        rule_id=str(chunk.get("rule_id", "")),
        rule_hash=str(chunk.get("rule_hash", "")),
        source_batch=str(chunk.get("source_batch", "")),
        supersedes=str(chunk.get("supersedes", "")),
        superseded_by=str(chunk.get("superseded_by", "")),
        community=str(chunk.get("community", "")),
        section=str(chunk.get("section", "")),
        source_file=str(chunk.get("source_file", "")),
        preview=shorten(" ".join(content.split()), width=240, placeholder="..."),
        content=content if show_context else None,
    )


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
    return AskResponse(
        status=status,
        question=request.question,
        answer=answer,
        retrieval_confidence=str(assessment.get("confidence", "")),
        confidence_reason=str(assessment.get("reason", "")),
        sources=[chunk_to_source(chunk, request.show_context) for chunk in chunks],
        answer_citations=[chunk_to_source(chunk, False) for chunk in cited_chunks],
        used_ai=used_ai,
        warnings=warnings,
    )


def answer_question(request: AskRequest) -> AskResponse:
    warnings: list[str] = []
    try:
        chunks, hints, assessment = retrieve_chunks(
            request.question,
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
        answer = call_deepseek(api_key, request.question, context_packet, prompt, str(assessment.get("reason", "")))
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

    return build_response(
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
