from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from textwrap import shorten
from typing import Any

import requests


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def print_sources(chunks: list[dict[str, Any]], title: str = "Retrieved Sources") -> None:
    print(f"{title}:")
    if not chunks:
        print("- none")
        return
    for chunk in chunks:
        preview = shorten(" ".join(chunk["content"].split()), width=180, placeholder="...")
        print(
            f"[{chunk['source_id']}] distance={chunk['distance']} "
            f"type={chunk['type']} authority={chunk.get('authority_level', '')} "
            f"status={chunk.get('status', '')} community={chunk['community']} "
            f"lifecycle={chunk.get('lifecycle_generation', '')} "
            f"temporal={chunk.get('temporal_state', '')} "
            f"category={chunk.get('category', '')} "
            f"rerank={chunk.get('rerank_score', '')} "
            f"section={chunk['section']} source={chunk['source_file']}"
        )
        print(f"    {preview}")


def print_citations(chunks: list[dict[str, Any]], title: str = "Citations") -> None:
    print(f"{title}:")
    if not chunks:
        print("- none")
        return
    for chunk in chunks:
        print(f"[{chunk['source_id']}] {chunk['source_file']} - {chunk['section']}")


def cited_source_ids(answer: str, chunks: list[dict[str, Any]]) -> list[int]:
    valid_ids = {int(chunk["source_id"]) for chunk in chunks}
    found = []
    for raw_id in re.findall(r"\[(?:Source )?(\d+)\]", answer):
        source_id = int(raw_id)
        if source_id in valid_ids and source_id not in found:
            found.append(source_id)
    return found


def chunks_by_ids(chunks: list[dict[str, Any]], source_ids: list[int]) -> list[dict[str, Any]]:
    lookup = {int(chunk["source_id"]): chunk for chunk in chunks}
    return [lookup[source_id] for source_id in source_ids if source_id in lookup]


def strip_sources_section(answer: str) -> str:
    """Remove a model-generated trailing Sources block so callers render one citation list."""
    cleaned = re.sub(
        r"\n+\s*Sources:\s*\n(?:\s*\[\d+\][^\n]*(?:\n|$))+\s*$",
        "\n",
        str(answer or "").strip(),
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or str(answer or "").strip()


def insufficient_context_answer(reason: str) -> str:
    return "\n".join(
        [
            "The vault does not contain enough information to answer this safely.",
            "",
            f"Reason: {reason}",
        ]
    )


def lifecycle_advisory_note(chunks: list[dict[str, Any]]) -> str:
    pending = [
        chunk
        for chunk in chunks
        if str(chunk.get("status", "")) == "pending" or str(chunk.get("temporal_state", "")) in {"pending", "not_yet_active"}
    ]
    expired = [chunk for chunk in chunks if str(chunk.get("temporal_state", "")) == "expired"]
    unknown = [chunk for chunk in chunks if str(chunk.get("temporal_state", "")) == "unknown"]
    if not pending and not expired and not unknown:
        return ""
    active = [chunk for chunk in chunks if str(chunk.get("temporal_state", "")) == "active"]
    if not active:
        lines = ["Temporal advisory: retrieved sources are not confirmed active by temporal metadata."]
        for chunk in pending + expired + unknown:
            lines.append(
                f"- Source {chunk['source_id']}: temporal_state={chunk.get('temporal_state', '')} "
                f"{chunk['title']} ({chunk['source_file']} - {chunk['section']})"
            )
        return "\n".join(lines)
    pending_lines = [
        f"- Non-current Source {chunk['source_id']}: temporal_state={chunk.get('temporal_state', '')} "
        f"{chunk['title']} ({chunk['source_file']} - {chunk['section']})"
        for chunk in pending
    ]
    expired_lines = [
        f"- Expired Source {chunk['source_id']}: {chunk['title']} ({chunk['source_file']} - {chunk['section']})"
        for chunk in expired
    ]
    unknown_lines = [
        f"- Unknown Temporal Source {chunk['source_id']}: {chunk['title']} ({chunk['source_file']} - {chunk['section']})"
        for chunk in unknown
    ]
    active_lines = [
        f"- Active Source {chunk['source_id']}: {chunk['title']} ({chunk['source_file']} - {chunk['section']})"
        for chunk in active[:3]
    ]
    return "\n".join(
        [
            "Lifecycle advisory: active rules outrank pending rules.",
            "If a pending, not-yet-active, expired, or unknown-temporal source is operationally relevant, warn and do not treat it as active.",
            "Active context:",
            *active_lines,
            "Non-current or uncertain context:",
            *pending_lines,
            *expired_lines,
            *unknown_lines,
        ]
    )


def call_deepseek(api_key: str, question: str, context_packet: str, prompt: str, retrieval_note: str = "") -> str:
    user_parts = [f"Question:\n{question}"]
    if retrieval_note:
        user_parts.append(f"Retrieval note:\n{retrieval_note}")
    user_parts.extend(
        [
            f"Retrieved context:\n{context_packet}",
            "Return a concise grounded answer with Sources.",
        ]
    )
    payload = {
        "model": DEEPSEEK_MODEL,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": "\n\n".join(user_parts),
            },
        ],
    }
    request = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"DeepSeek request failed with HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"DeepSeek request failed: {error.reason}") from error

    parsed = json.loads(response_body)
    return str(parsed["choices"][0]["message"]["content"]).strip()


def call_deepseek_stream(
    api_key: str,
    question: str,
    context_packet: str,
    prompt: str,
    retrieval_note: str = "",
):
    """Call DeepSeek with stream=True. Yields token strings as they arrive."""
    user_parts = [f"Question:\n{question}"]
    if retrieval_note:
        user_parts.append(f"Retrieval note:\n{retrieval_note}")
    user_parts.extend(
        [
            f"Retrieved context:\n{context_packet}",
            "Return a concise grounded answer with Sources.",
        ]
    )
    payload = {
        "model": DEEPSEEK_MODEL,
        "temperature": 0.1,
        "stream": True,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": "\n\n".join(user_parts),
            },
        ],
    }
    with requests.post(
        DEEPSEEK_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8") if isinstance(line, bytes) else line
            if not decoded.startswith("data:"):
                continue
            data_str = decoded[len("data:"):].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                delta = chunk["choices"][0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    yield token
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
