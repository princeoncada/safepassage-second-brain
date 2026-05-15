from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from textwrap import shorten
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "safepassage_vault_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"
CONFIG_PATH = REPO_ROOT / "rag" / "config" / "retrieval_config.json"


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


def normalize_preview(document: str) -> str:
    return re.sub(r"\s+", " ", str(document or "").lower()).strip()


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


def retrieval_confidence(best_distance: float | None, has_mismatch: bool, threshold: float) -> tuple[str, str]:
    if best_distance is None:
        return "none", "no chunks returned"
    if has_mismatch:
        return "weak", "query metadata did not match retrieved metadata"
    if best_distance <= threshold:
        return "strong", f"best distance {best_distance:.4f} is within threshold {threshold}"
    return "weak", f"best distance {best_distance:.4f} is above threshold {threshold}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve Markdown chunks from the local SafePassage ChromaDB index.")
    parser.add_argument("query", help="Question or search phrase to retrieve against the vault index.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve. Default: 5.")
    parser.add_argument(
        "--include-low-value-sections",
        action="store_true",
        help="Allow low-value sections such as Change History, Open Questions, and Source Input in query results.",
    )
    args = parser.parse_args()

    if not CHROMA_DIR.exists():
        raise SystemExit("Chroma index does not exist. Run: python rag/scripts/index_vault.py")

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([args.query], normalize_embeddings=True).tolist()[0]

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        raise SystemExit("Chroma collection is missing. Run: python rag/scripts/index_vault.py") from error

    fetch_count = max(args.top_k * 4, 20)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_count,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        print("No chunks returned.")
        return 0

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
    hints = extract_query_hints(args.query, config, candidate_communities)

    candidates = []
    seen_keys: set[tuple[str, str, str]] = set()
    seen_content: set[str] = set()
    seen_near_duplicates: list[dict[str, str]] = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] or {}
        section = str(metadata.get("section", ""))
        normalized_section = normalize_section_name(section)
        normalized_community = normalize_key(str(metadata.get("community", "")))
        normalized_type = normalize_key(str(metadata.get("type", "")))
        if not args.include_low_value_sections and (
            truthy(metadata.get("is_low_value_section")) or normalized_section in low_value_sections
        ):
            continue

        dedupe_key = (
            str(metadata.get("source_file", "")),
            str(metadata.get("normalized_title") or normalize_key(str(metadata.get("title", "")))),
            normalized_section,
        )
        content_key = str(metadata.get("content_fingerprint") or normalize_preview(document))
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

        distance = distances[index] if index < len(distances) else 999.0
        adjusted_distance = float(distance) - section_boosts.get(normalized_section, 0.0)
        if args.include_low_value_sections and normalized_section in low_value_sections:
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
        candidates.append((adjusted_distance, float(distance), document, metadata))

    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))

    if not candidates:
        print("No chunks returned after filtering and dedupe.")
        print("Re-index with --include-low-value-sections or query with --include-low-value-sections to inspect filtered sections.")
        return 0

    best_distance = candidates[0][1] if candidates else None
    has_mismatch = bool(hints["missing_community"]) or (
        bool(hints["community"])
        and all(normalize_key(str(candidate[3].get("community", ""))) != normalize_key(hints["community"]) for candidate in candidates)
    ) or (
        bool(hints["expected_types"])
        and all(str(candidate[3].get("type", "")) not in hints["expected_types"] for candidate in candidates)
    )
    confidence, reason = retrieval_confidence(best_distance, has_mismatch, weak_threshold)
    print(f"Retrieval Confidence: {confidence}")
    print(f"Confidence Reason: {reason}")
    if hints["community"]:
        print(f"Community Hint: {hints['community']}")
    if hints["missing_community"]:
        print(f"Community Hint: {hints['missing_community']} (not found in indexed metadata)")
    if hints["expected_types"]:
        print(f"Expected Types: {', '.join(sorted(hints['expected_types']))}")
    print("-" * 80)

    for index, (_adjusted_distance, distance, document, metadata) in enumerate(candidates[: args.top_k], start=1):
        preview = shorten(" ".join(str(document).split()), width=320, placeholder="...")

        print(f"Rank: {index}")
        print(f"Distance: {distance}")
        print(f"Title: {metadata.get('title', '')}")
        print(f"Type: {metadata.get('type', '')}")
        print(f"Community: {metadata.get('community', '')}")
        print(f"Section: {metadata.get('section', '')}")
        print(f"Source: {metadata.get('source_file', '')}")
        print(f"Preview: {preview}")
        print("-" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
