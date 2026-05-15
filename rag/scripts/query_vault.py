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
                "Summary": 0.08,
                "Details": 0.06,
                "Agent Action": 0.05,
                "QA Notes": 0.04,
            },
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_section_name(section: str) -> str:
    return re.sub(r"\s+", " ", str(section or "").strip()).lower()


def normalize_preview(document: str) -> str:
    return re.sub(r"\s+", " ", str(document or "").lower()).strip()


def truthy(value: Any) -> bool:
    return str(value).lower() == "true"


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

    candidates = []
    seen_keys: set[tuple[str, str, str]] = set()
    seen_content: set[str] = set()
    for index, document in enumerate(documents):
        metadata = metadatas[index] or {}
        section = str(metadata.get("section", ""))
        normalized_section = normalize_section_name(section)
        if not args.include_low_value_sections and (
            truthy(metadata.get("is_low_value_section")) or normalized_section in low_value_sections
        ):
            continue

        dedupe_key = (
            str(metadata.get("source_file", "")),
            str(metadata.get("title", "")).lower(),
            normalized_section,
        )
        content_key = str(metadata.get("content_fingerprint") or normalize_preview(document))
        if dedupe_key in seen_keys or content_key in seen_content:
            continue
        seen_keys.add(dedupe_key)
        seen_content.add(content_key)

        distance = distances[index] if index < len(distances) else 999.0
        adjusted_distance = float(distance) - section_boosts.get(normalized_section, 0.0)
        candidates.append((adjusted_distance, float(distance), document, metadata))

    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))

    if not candidates:
        print("No chunks returned after filtering and dedupe.")
        print("Re-index with --include-low-value-sections or query with --include-low-value-sections to inspect filtered sections.")
        return 0

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
