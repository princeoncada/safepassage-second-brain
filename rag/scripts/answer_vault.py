from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rag.answer import (
    call_deepseek,
    call_deepseek_stream,
    chunks_by_ids,
    cited_source_ids,
    insufficient_context_answer,
    lifecycle_advisory_note,
    print_citations,
    print_sources,
    strip_sources_section,
)
from rag.context import build_context_packet
from rag.retrieval import (
    ALIASES_PATH,
    CHROMA_DIR,
    COLLECTION_NAME,
    MODEL_NAME,
    _EMBEDDING_MODEL,
    alias_community_hint,
    alias_tokens,
    authority_level,
    expand_query_with_alias,
    extract_query_hints,
    has_global_primary_workflow,
    has_higher_authority_community_match,
    is_default_workflow_query,
    jaccard_similarity,
    load_community_aliases,
    load_retrieval_config,
    normalize_key,
    normalize_section_name,
    normalize_text,
    normalized_preview_key,
    retrieval_assessment,
    retrieve_chunks,
    scope_sort_group,
    temporal_state,
    temporal_warning,
    token_set,
    truthy,
)


PROMPT_PATH = REPO_ROOT / "rag" / "prompts" / "answer_from_context.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Answer questions using only retrieved SafePassage vault context.")
    parser.add_argument("question", help="Operational question to answer from retrieved vault context.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve. Default: 5.")
    parser.add_argument("--show-context", action="store_true", help="Print the compact context packet.")
    parser.add_argument(
        "--include-low-value-sections",
        action="store_true",
        help="Allow low-value sections such as Change History, Open Questions, and Source Input.",
    )
    parser.add_argument("--no-ai", action="store_true", help="Print retrieved context and skip DeepSeek.")
    args = parser.parse_args()

    chunks, hints, assessment = retrieve_chunks(args.question, args.top_k, args.include_low_value_sections)
    context_packet = build_context_packet(chunks)

    print(f"Question: {args.question}")
    print()
    print(f"Retrieval Confidence: {assessment['confidence']}")
    print(f"Confidence Reason: {assessment['reason']}")
    print(f"Intent Category: {hints.get('intent_category', '')}")
    if hints["community"]:
        print(f"Community Hint: {hints['community']}")
    if hints.get("community_alias"):
        print(f"Community Alias: {hints['community_alias']} -> {hints['community']}")
    if hints["missing_community"]:
        print(f"Community Hint: {hints['missing_community']} (not found in indexed metadata)")
    if hints["expected_types"]:
        print(f"Expected Types: {', '.join(sorted(hints['expected_types']))}")
    if hints.get("topic_terms"):
        print(f"Topic Terms: {', '.join(hints['topic_terms'])}")
    if hints.get("scope_hint"):
        print(f"Scope Hint: {hints['scope_hint']}")
    print()

    if assessment["confidence"] in {"weak", "none"}:
        print()
        print("Warning: retrieved context is weak.")
    advisory_note = lifecycle_advisory_note(chunks)
    if advisory_note:
        print()
        print("Warning: non-current or uncertain temporal lifecycle context is present.")
    temporal_warnings = [
        f"Source {chunk['source_id']}: {chunk.get('temporal_warning')}"
        for chunk in chunks
        if chunk.get("temporal_warning")
    ]
    if temporal_warnings:
        print()
        print("Temporal Metadata Warnings:")
        for warning in temporal_warnings:
            print(f"- {warning}")

    if args.show_context:
        print()
        print("Context Packet:")
        print(context_packet or "[empty]")

    if args.no_ai:
        print()
        print("AI skipped because --no-ai was used.")
        print_citations(chunks, title="Retrieved Context Citations")
        return 0

    if assessment["refuse"]:
        print()
        print("Generated Answer:")
        print(insufficient_context_answer(str(assessment["reason"])))
        print()
        print_sources(chunks, title="Closest Retrieved Sources")
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print()
        print("DEEPSEEK_API_KEY is not set. Set it before running AI answer generation.")
        print('PowerShell: $env:DEEPSEEK_API_KEY="your_key_here"')
        print("Use --no-ai to validate retrieval only.")
        return 1

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    retrieval_notes = [str(assessment["reason"])]
    if advisory_note:
        retrieval_notes.append(advisory_note)
    answer = call_deepseek(api_key, args.question, context_packet, prompt, "\n\n".join(retrieval_notes))
    source_ids = cited_source_ids(answer, chunks)
    cited_chunks = chunks_by_ids(chunks, source_ids)
    cleaned_answer = strip_sources_section(answer)

    print()
    print("Generated Answer:")
    print(cleaned_answer)
    print()
    if cited_chunks:
        print_citations(cited_chunks, title="Sources")
    else:
        print("Sources:")
        print("- no explicit source IDs found in generated answer")
        print()
        print_sources(chunks, title="Retrieved Sources For Review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
