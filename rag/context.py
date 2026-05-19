from __future__ import annotations

from typing import Any


def build_context_packet(chunks: list[dict[str, Any]]) -> str:
    blocks = []
    for chunk in chunks:
        blocks.append(
            "\n".join(
                [
                    f"[Source {chunk['source_id']}]",
                    f"Title: {chunk['title']}",
                    f"Type: {chunk['type']}",
                    f"Authority Level: {chunk.get('authority_level', '')}",
                    f"Scope: {chunk.get('scope', '')}",
                    f"Status: {chunk.get('status', '')}",
                    f"Lifecycle Generation: {chunk.get('lifecycle_generation', '')}",
                    f"Temporal State: {chunk.get('temporal_state', '')}",
                    f"Temporal Warning: {chunk.get('temporal_warning', '')}",
                    f"Temporal Start: {chunk.get('temporal_start_date', '')} ({chunk.get('temporal_start_field', '')})",
                    f"Temporal End: {chunk.get('temporal_end_date', '')} ({chunk.get('temporal_end_field', '')})",
                    f"Category: {chunk.get('category', '')}",
                    f"Rerank Score: {chunk.get('rerank_score', '')}",
                    f"Rerank Reasons: {chunk.get('rerank_reasons', '')}",
                    f"Announcement ID: {chunk.get('announcement_id', '')}",
                    f"Rule ID: {chunk.get('rule_id', '')}",
                    f"Community: {chunk['community']}",
                    f"Section: {chunk['section']}",
                    f"Source File: {chunk['source_file']}",
                    "Content:",
                    chunk["content"],
                ]
            )
        )
    return "\n\n".join(blocks)
