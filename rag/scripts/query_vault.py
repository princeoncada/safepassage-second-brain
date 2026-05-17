from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from textwrap import shorten
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import chromadb
from sentence_transformers import SentenceTransformer

from rag.lifecycle import temporal_lifecycle
from rag.query_intent import expand_query_with_intent, parse_query_intent


COLLECTION_NAME = "safepassage_vault_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"
CONFIG_PATH = REPO_ROOT / "rag" / "config" / "retrieval_config.json"
ALIASES_PATH = REPO_ROOT / "rag" / "config" / "community_aliases.json"


def load_retrieval_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {
            "low_value_sections": ["Change History", "Open Questions", "Source Input"],
            "section_boosts": {
                "Agent Action": 0.18,
                "Summary": 0.16,
                "Details": 0.14,
                "Rule": 0.12,
                "Policy": 0.12,
                "QA Notes": 0.06,
            },
            "weak_context_distance_threshold": 0.95,
            "primary_workflow_default_threshold": 1.1,
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_community_aliases() -> dict[str, str]:
    if not ALIASES_PATH.exists():
        return {}
    with ALIASES_PATH.open("r", encoding="utf-8") as file:
        parsed = json.load(file)
    return {str(key).upper(): str(value) for key, value in parsed.items()}


def normalize_section_name(section: str) -> str:
    return re.sub(r"\s+", " ", str(section or "").strip()).lower()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def alias_tokens(query: str) -> list[str]:
    tokens = re.findall(r"\b[A-Za-z]{2,6}\d*\b", query)
    return [re.match(r"[A-Za-z]+", token).group(0).upper() for token in tokens if re.match(r"[A-Za-z]+", token)]


def alias_community_hint(query: str) -> tuple[str, str]:
    aliases = load_community_aliases()
    for token in alias_tokens(query):
        if token in aliases:
            return aliases[token], token
    return "", ""


def expand_query_with_alias(query: str) -> tuple[str, str, str]:
    community, alias = alias_community_hint(query)
    if not community:
        return query, "", ""
    return f"{query} {community}", community, alias


def normalize_preview(document: str) -> str:
    return re.sub(r"\s+", " ", str(document or "").lower()).strip()


def normalized_preview_key(document: str, word_count: int) -> str:
    words = normalize_preview(document).split()
    return " ".join(words[:word_count])


def truthy(value: Any) -> bool:
    return str(value).lower() == "true"


def authority_level(metadata: dict[str, Any]) -> str:
    explicit = str(metadata.get("authority_level", "")).strip()
    if explicit:
        return explicit
    doc_type = str(metadata.get("type", "")).strip()
    if doc_type in {"post_order", "announcement"}:
        return doc_type
    if doc_type == "workflow":
        return "primary_workflow"
    return ""


def temporal_state(metadata: dict[str, Any]) -> str:
    explicit = str(metadata.get("temporal_state", "")).strip()
    if explicit:
        return explicit
    return temporal_lifecycle(metadata).temporal_state


def is_default_workflow_query(query: str) -> bool:
    normalized = normalize_key(query)
    return any(term in normalized for term in ["default", "base workflow", "primary workflow", "by default"])


def has_global_primary_workflow(candidates: list[tuple[float, float, str, dict[str, Any]]]) -> bool:
    return any(
        authority_level(candidate[3]) == "primary_workflow"
        and normalize_key(str(candidate[3].get("community", ""))) == "global"
        for candidate in candidates
    )


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
    alias_community, alias = alias_community_hint(query)
    communities = {normalize_key(community): community for community in config.get("known_communities", [])}
    communities.update({normalize_key(community): community for community in candidate_communities if community})
    community_hint = alias_community
    missing_community_hint = ""
    if not community_hint:
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
    if any(term in normalized_query for term in ["post order", "rule", "policy", "physical id", "digital id"]):
        expected_types.update({"post_order", "qa_rule"})
    if any(term in normalized_query for term in ["incident", "happened", "tailgating", "tailgate"]):
        expected_types.add("incident")
    if any(term in normalized_query for term in ["visitor log", "tag", "vendor"]):
        expected_types.add("visitor_log")
    if any(
        term in normalized_query
        for term in ["announcement", "reminder", "red zone", "nvr", "gate issue", "kiosk audio", "pickleball", "pre authorized", "preauthorized"]
    ):
        expected_types.add("announcement")

    return {
        "community": community_hint,
        "community_alias": alias,
        "missing_community": missing_community_hint,
        "expected_types": expected_types,
    }


def retrieval_confidence(
    best_distance: float | None,
    has_mismatch: bool,
    threshold: float,
    primary_workflow_default_threshold: float,
    has_primary_workflow: bool,
    is_default_query: bool,
) -> tuple[str, str]:
    if best_distance is None:
        return "none", "no chunks returned"
    if has_mismatch:
        return "weak", "query metadata did not match retrieved metadata"
    if best_distance <= threshold:
        return "strong", f"best distance {best_distance:.4f} is within threshold {threshold}"
    if is_default_query and has_primary_workflow and best_distance <= primary_workflow_default_threshold:
        return (
            "fallback",
            f"best distance {best_distance:.4f} is above standard threshold {threshold} "
            f"but within primary workflow default threshold {primary_workflow_default_threshold}",
        )
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

    config = load_retrieval_config()
    initial_intent = parse_query_intent(args.query, set(config.get("known_communities", [])))
    expanded_query = expand_query_with_intent(initial_intent)
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([expanded_query], normalize_embeddings=True).tolist()[0]

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        raise SystemExit("Chroma collection is missing. Run: python rag/scripts/index_vault.py") from error

    fetch_count = max(args.top_k * 20, 100)
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
    authority_boosts = {
        str(level): float(boost)
        for level, boost in config.get("authority_boosts", {}).items()
    }
    status_boosts = {str(status): float(boost) for status, boost in config.get("status_boosts", {}).items()}
    status_penalties = {str(status): float(penalty) for status, penalty in config.get("status_penalties", {}).items()}
    temporal_boosts = {str(state): float(boost) for state, boost in config.get("temporal_state_boosts", {}).items()}
    temporal_penalties = {str(state): float(penalty) for state, penalty in config.get("temporal_state_penalties", {}).items()}
    lifecycle_boosts = {
        str(generation): float(boost)
        for generation, boost in config.get("lifecycle_generation_boosts", {}).items()
    }
    lifecycle_penalties = {
        str(generation): float(penalty)
        for generation, penalty in config.get("lifecycle_generation_penalties", {}).items()
    }
    skip_legacy = bool(config.get("skip_legacy_lifecycle_by_default", True))
    skip_archived = bool(config.get("skip_archived_by_default", True))
    primary_specific_community_penalty = float(config.get("primary_workflow_specific_community_penalty", 0.12))
    primary_default_boost = float(config.get("primary_workflow_default_query_boost", 0.1))
    weak_threshold = float(config.get("weak_context_distance_threshold", 0.95))
    primary_workflow_default_threshold = float(config.get("primary_workflow_default_threshold", 1.1))
    near_duplicate_threshold = float(config.get("near_duplicate_similarity_threshold", 0.9))
    candidate_communities = {str(metadata.get("community", "")) for metadata in metadatas if metadata}
    known_communities = set(config.get("known_communities", [])) | candidate_communities
    intent = parse_query_intent(args.query, known_communities)
    hints = intent.as_hints()
    if hints["community"]:
        try:
            community_results = collection.get(
                where={"community": hints["community"]},
                include=["documents", "metadatas"],
            )
            seen = {
                (str(metadata.get("source_file", "")), str(metadata.get("section", "")))
                for metadata in metadatas
                if metadata
            }
            for document, metadata in zip(
                community_results.get("documents", []),
                community_results.get("metadatas", []),
            ):
                key = (str(metadata.get("source_file", "")), str(metadata.get("section", "")))
                if key in seen:
                    continue
                documents.append(document)
                metadatas.append(metadata)
                distances.append(1.25)
                seen.add(key)
        except Exception:
            pass

    raw_candidates = []
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
        status = str(metadata.get("status", ""))
        lifecycle_generation = str(metadata.get("lifecycle_generation", ""))
        if skip_archived and status == "archived":
            continue
        if skip_legacy and lifecycle_generation == "legacy":
            continue
        temporal = temporal_state(metadata)

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
        authority = authority_level(metadata)
        adjusted_distance -= authority_boosts.get(authority, 0.0)
        adjusted_distance -= status_boosts.get(status, 0.0)
        adjusted_distance += status_penalties.get(status, 0.0)
        adjusted_distance -= temporal_boosts.get(temporal, 0.0)
        adjusted_distance += temporal_penalties.get(temporal, 0.0)
        adjusted_distance -= lifecycle_boosts.get(lifecycle_generation, 0.0)
        adjusted_distance += lifecycle_penalties.get(lifecycle_generation, 0.0)
        if authority == "primary_workflow" and hints["community"]:
            adjusted_distance += primary_specific_community_penalty
        if authority == "primary_workflow" and hints.get("is_default_workflow_query"):
            adjusted_distance -= primary_default_boost
        raw_candidates.append((adjusted_distance, float(distance), str(document), metadata))

    raw_candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
    if hints["expected_types"]:
        type_matched = [
            candidate for candidate in raw_candidates if str(candidate[3].get("type", "")) in hints["expected_types"]
        ]
        if type_matched:
            raw_candidates = type_matched
    if hints["community"]:
        community_matched = [
            candidate
            for candidate in raw_candidates
            if normalize_key(str(candidate[3].get("community", ""))) == normalize_key(hints["community"])
        ]
        if community_matched:
            raw_candidates = community_matched

    preview_words = int(config.get("content_preview_dedupe_words", 32))
    candidates = []
    seen_identity_keys: set[tuple[str, str, str, str]] = set()
    seen_preview_keys: set[tuple[str, str, str, str]] = set()
    seen_near_duplicates: list[dict[str, str]] = []
    for adjusted_distance, distance, document, metadata in raw_candidates:
        normalized_title = str(metadata.get("normalized_title") or normalize_key(str(metadata.get("title", ""))))
        normalized_community = normalize_key(str(metadata.get("community", "")))
        normalized_type = normalize_key(str(metadata.get("type", "")))
        normalized_section = normalize_section_name(str(metadata.get("section", "")))
        identity_key = (normalized_title, normalized_community, normalized_type, normalized_section)
        preview_key = (
            normalized_community,
            normalized_type,
            normalized_section,
            normalized_preview_key(document, preview_words),
        )
        if identity_key in seen_identity_keys or preview_key in seen_preview_keys:
            continue

        if any(
            existing["community"] == normalized_community
            and existing["type"] == normalized_type
            and existing["section"] == normalized_section
            and jaccard_similarity(existing["document"], document) >= near_duplicate_threshold
            for existing in seen_near_duplicates
        ):
            continue

        seen_identity_keys.add(identity_key)
        seen_preview_keys.add(preview_key)
        seen_near_duplicates.append(
            {
                "community": normalized_community,
                "type": normalized_type,
                "section": normalized_section,
                "document": document,
            }
        )
        candidates.append((adjusted_distance, distance, document, metadata))

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
    confidence, reason = retrieval_confidence(
        best_distance,
        has_mismatch,
        weak_threshold,
        primary_workflow_default_threshold,
        has_global_primary_workflow(candidates),
        bool(hints.get("is_default_workflow_query")),
    )
    print(f"Retrieval Confidence: {confidence}")
    print(f"Confidence Reason: {reason}")
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
    print("-" * 80)

    for index, (_adjusted_distance, distance, document, metadata) in enumerate(candidates[: args.top_k], start=1):
        preview = shorten(" ".join(str(document).split()), width=320, placeholder="...")

        print(f"Rank: {index}")
        print(f"Distance: {distance}")
        print(f"Title: {metadata.get('title', '')}")
        print(f"Type: {metadata.get('type', '')}")
        print(f"Authority: {authority_level(metadata)}")
        print(f"Status: {metadata.get('status', '')}")
        print(f"Lifecycle Generation: {metadata.get('lifecycle_generation', '')}")
        print(f"Temporal State: {temporal_state(metadata)}")
        if metadata.get("temporal_warning", ""):
            print(f"Temporal Warning: {metadata.get('temporal_warning', '')}")
        if metadata.get("temporal_start_date", ""):
            print(f"Temporal Start: {metadata.get('temporal_start_date', '')} ({metadata.get('temporal_start_field', '')})")
        if metadata.get("temporal_end_date", ""):
            print(f"Temporal End: {metadata.get('temporal_end_date', '')} ({metadata.get('temporal_end_field', '')})")
        print(f"Category: {metadata.get('category', '')}")
        print(f"Announcement ID: {metadata.get('announcement_id', '')}")
        print(f"Rule ID: {metadata.get('rule_id', '')}")
        print(f"Community: {metadata.get('community', '')}")
        print(f"Section: {metadata.get('section', '')}")
        print(f"Source: {metadata.get('source_file', '')}")
        print(f"Preview: {preview}")
        print("-" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
