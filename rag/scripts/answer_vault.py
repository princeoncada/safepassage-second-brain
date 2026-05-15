from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from textwrap import shorten
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "safepassage_vault_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"
CONFIG_PATH = REPO_ROOT / "rag" / "config" / "retrieval_config.json"
PROMPT_PATH = REPO_ROOT / "rag" / "prompts" / "answer_from_context.md"


def load_retrieval_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {
            "low_value_sections": ["Change History", "Open Questions", "Source Input"],
            "section_boosts": {
                "Summary": 0.14,
                "Details": 0.12,
                "Agent Action": 0.1,
                "QA Notes": 0.06,
            },
            "weak_context_distance_threshold": 0.95,
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_section_name(section: str) -> str:
    return re.sub(r"\s+", " ", str(section or "").strip()).lower()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def truthy(value: Any) -> bool:
    return str(value).lower() == "true"


def token_set(value: str) -> set[str]:
    return {token for token in normalize_key(value).split() if len(token) > 2}


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def extract_query_hints(query: str, config: dict[str, Any], candidate_communities: set[str]) -> dict[str, Any]:
    normalized_query = normalize_key(query)
    communities = {normalize_key(community): community for community in config.get("known_communities", [])}
    communities.update({normalize_key(community): community for community in candidate_communities if community})
    community_hint = ""
    missing_community_hint = ""
    for normalized_community, original in communities.items():
        if normalized_community and normalized_community in normalized_query:
            community_hint = original
            break
    if not community_hint:
        proper_phrases = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", query)
        ignored = {"What", "Source Input", "Open Questions", "Change History", "Agent Action"}
        for phrase in proper_phrases:
            if phrase not in ignored:
                missing_community_hint = phrase
                break

    expected_types: set[str] = set()
    if any(term in normalized_query for term in ["post order", "rule", "policy"]):
        expected_types.update({"post_order", "qa_rule"})
    if any(term in normalized_query for term in ["incident", "happened", "tailgating", "tailgate"]):
        expected_types.add("incident")
    if any(term in normalized_query for term in ["visitor log", "tag", "vendor"]):
        expected_types.add("visitor_log")

    return {
        "community": community_hint,
        "missing_community": missing_community_hint,
        "expected_types": expected_types,
    }


def retrieval_assessment(chunks: list[dict[str, Any]], hints: dict[str, Any], threshold: float) -> dict[str, Any]:
    if not chunks:
        return {"confidence": "none", "refuse": True, "reason": "no chunks returned"}
    best_distance = min(float(chunk["distance"]) for chunk in chunks)
    if hints["missing_community"]:
        return {
            "confidence": "weak",
            "refuse": True,
            "reason": f"no indexed source matched community hint '{hints['missing_community']}'",
        }
    if hints["community"] and all(normalize_key(chunk["community"]) != normalize_key(hints["community"]) for chunk in chunks):
        return {
            "confidence": "weak",
            "refuse": True,
            "reason": f"no retrieved source matched community hint '{hints['community']}'",
        }
    if best_distance > threshold:
        return {
            "confidence": "weak",
            "refuse": True,
            "reason": f"best distance {best_distance:.4f} is above threshold {threshold}",
        }
    if hints["expected_types"] and not any(chunk["type"] in hints["expected_types"] for chunk in chunks):
        return {
            "confidence": "weak",
            "refuse": True,
            "reason": f"no retrieved source matched expected types {', '.join(sorted(hints['expected_types']))}",
        }
    return {
        "confidence": "strong",
        "refuse": False,
        "reason": f"best distance {best_distance:.4f} is within threshold {threshold}",
    }


def retrieve_chunks(query: str, top_k: int, include_low_value_sections: bool) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if not CHROMA_DIR.exists():
        raise SystemExit("Chroma index does not exist. Run: python rag/scripts/index_vault.py")

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()[0]

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        raise SystemExit("Chroma collection is missing. Run: python rag/scripts/index_vault.py") from error

    fetch_count = max(top_k * 4, 20)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_count,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    config = load_retrieval_config()
    section_boosts = {
        normalize_section_name(section): float(boost)
        for section, boost in config.get("section_boosts", {}).items()
    }
    low_value_sections = {normalize_section_name(section) for section in config.get("low_value_sections", [])}
    low_value_penalty = float(config.get("low_value_section_penalty", 0.35))
    community_match_boost = float(config.get("community_match_boost", 0.18))
    community_mismatch_penalty = float(config.get("community_mismatch_penalty", 0.45))
    type_match_boost = float(config.get("type_match_boost", 0.1))
    type_mismatch_penalty = float(config.get("type_mismatch_penalty", 0.18))
    weak_threshold = float(config.get("weak_context_distance_threshold", 0.95))
    near_duplicate_threshold = float(config.get("near_duplicate_similarity_threshold", 0.9))
    candidate_communities = {str(metadata.get("community", "")) for metadata in metadatas if metadata}
    hints = extract_query_hints(query, config, candidate_communities)

    candidates: list[tuple[float, float, str, dict[str, Any]]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    seen_content: set[str] = set()
    seen_near_duplicates: list[dict[str, str]] = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] or {}
        section = str(metadata.get("section", ""))
        normalized_section = normalize_section_name(section)
        normalized_community = normalize_key(str(metadata.get("community", "")))
        normalized_type = normalize_key(str(metadata.get("type", "")))
        if not include_low_value_sections and (
            truthy(metadata.get("is_low_value_section")) or normalized_section in low_value_sections
        ):
            continue

        dedupe_key = (
            str(metadata.get("source_file", "")),
            str(metadata.get("normalized_title") or normalize_key(str(metadata.get("title", "")))),
            normalized_section,
        )
        content_key = str(metadata.get("content_fingerprint") or normalize_text(document))
        if dedupe_key in seen_keys or content_key in seen_content:
            continue
        near_duplicate = False
        for existing in seen_near_duplicates:
            if existing["community"] != normalized_community:
                continue
            if existing["type"] != normalized_type:
                continue
            if existing["section"] != normalized_section:
                continue
            if jaccard_similarity(existing["document"], str(document)) >= near_duplicate_threshold:
                near_duplicate = True
                break
        if near_duplicate:
            continue
        seen_keys.add(dedupe_key)
        seen_content.add(content_key)
        seen_near_duplicates.append(
            {
                "community": normalized_community,
                "type": normalized_type,
                "section": normalized_section,
                "document": str(document),
            }
        )

        distance = float(distances[index]) if index < len(distances) else 999.0
        adjusted_distance = distance - section_boosts.get(normalized_section, 0.0)
        if include_low_value_sections and normalized_section in low_value_sections:
            adjusted_distance += low_value_penalty
        if hints["community"]:
            if normalized_community == normalize_key(hints["community"]):
                adjusted_distance -= community_match_boost
            else:
                adjusted_distance += community_mismatch_penalty
        if hints["expected_types"]:
            if str(metadata.get("type", "")) in hints["expected_types"]:
                adjusted_distance -= type_match_boost
            else:
                adjusted_distance += type_mismatch_penalty
        candidates.append((adjusted_distance, distance, str(document), metadata))

    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))

    chunks: list[dict[str, Any]] = []
    for source_id, (_adjusted, distance, document, metadata) in enumerate(candidates[:top_k], start=1):
        chunks.append(
            {
                "source_id": source_id,
                "distance": distance,
                "title": str(metadata.get("title", "")),
                "type": str(metadata.get("type", "")),
                "community": str(metadata.get("community", "")),
                "section": str(metadata.get("section", "")),
                "source_file": str(metadata.get("source_file", "")),
                "content": document,
            }
        )
    assessment = retrieval_assessment(chunks, hints, weak_threshold)
    return chunks, hints, assessment


def build_context_packet(chunks: list[dict[str, Any]]) -> str:
    blocks = []
    for chunk in chunks:
        blocks.append(
            "\n".join(
                [
                    f"[Source {chunk['source_id']}]",
                    f"Title: {chunk['title']}",
                    f"Type: {chunk['type']}",
                    f"Community: {chunk['community']}",
                    f"Section: {chunk['section']}",
                    f"Source File: {chunk['source_file']}",
                    "Content:",
                    chunk["content"],
                ]
            )
        )
    return "\n\n".join(blocks)


def print_sources(chunks: list[dict[str, Any]], title: str = "Retrieved Sources") -> None:
    print(f"{title}:")
    if not chunks:
        print("- none")
        return
    for chunk in chunks:
        preview = shorten(" ".join(chunk["content"].split()), width=180, placeholder="...")
        print(
            f"[{chunk['source_id']}] distance={chunk['distance']} "
            f"type={chunk['type']} community={chunk['community']} "
            f"section={chunk['section']} source={chunk['source_file']}"
        )
        print(f"    {preview}")


def print_citations(chunks: list[dict[str, Any]], title: str = "Citations") -> None:
    print(f"{title}:")
    if not chunks:
        print("- none")
        return
    for chunk in chunks:
        print(f"[{chunk['source_id']}] {chunk['source_file']} — {chunk['section']}")


def cited_source_ids(answer: str, chunks: list[dict[str, Any]]) -> list[int]:
    valid_ids = {int(chunk["source_id"]) for chunk in chunks}
    found = []
    for raw_id in re.findall(r"\[(\d+)\]", answer):
        source_id = int(raw_id)
        if source_id in valid_ids and source_id not in found:
            found.append(source_id)
    return found


def chunks_by_ids(chunks: list[dict[str, Any]], source_ids: list[int]) -> list[dict[str, Any]]:
    lookup = {int(chunk["source_id"]): chunk for chunk in chunks}
    return [lookup[source_id] for source_id in source_ids if source_id in lookup]


def insufficient_context_answer(reason: str) -> str:
    return "\n".join(
        [
            "The vault does not contain enough information to answer this safely.",
            "",
            f"Reason: {reason}",
        ]
    )


def call_deepseek(api_key: str, question: str, context_packet: str, prompt: str) -> str:
    payload = {
        "model": DEEPSEEK_MODEL,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": "\n\n".join(
                    [
                        f"Question:\n{question}",
                        f"Retrieved context:\n{context_packet}",
                        "Return a concise grounded answer with Sources.",
                    ]
                ),
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
    if hints["community"]:
        print(f"Community Hint: {hints['community']}")
    if hints["missing_community"]:
        print(f"Community Hint: {hints['missing_community']} (not found in indexed metadata)")
    if hints["expected_types"]:
        print(f"Expected Types: {', '.join(sorted(hints['expected_types']))}")
    print()
    print_sources(chunks)

    if assessment["confidence"] != "strong":
        print()
        print("Warning: retrieved context is weak.")

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
    answer = call_deepseek(api_key, args.question, context_packet, prompt)

    print()
    print("Generated Answer:")
    print(answer)
    print()
    source_ids = cited_source_ids(answer, chunks)
    cited_chunks = chunks_by_ids(chunks, source_ids)
    if cited_chunks:
        print_citations(cited_chunks, title="Answer Citations")
    else:
        print("Answer Citations:")
        print("- no explicit source IDs found in generated answer")
        print()
        print_sources(chunks, title="Retrieved Sources For Review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
