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


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def truthy(value: Any) -> bool:
    return str(value).lower() == "true"


def retrieve_chunks(query: str, top_k: int, include_low_value_sections: bool) -> list[dict[str, Any]]:
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

    candidates: list[tuple[float, float, str, dict[str, Any]]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    seen_content: set[str] = set()

    for index, document in enumerate(documents):
        metadata = metadatas[index] or {}
        section = str(metadata.get("section", ""))
        normalized_section = normalize_section_name(section)
        if not include_low_value_sections and (
            truthy(metadata.get("is_low_value_section")) or normalized_section in low_value_sections
        ):
            continue

        dedupe_key = (
            str(metadata.get("source_file", "")),
            str(metadata.get("title", "")).lower(),
            normalized_section,
        )
        content_key = str(metadata.get("content_fingerprint") or normalize_text(document))
        if dedupe_key in seen_keys or content_key in seen_content:
            continue
        seen_keys.add(dedupe_key)
        seen_content.add(content_key)

        distance = float(distances[index]) if index < len(distances) else 999.0
        adjusted_distance = distance - section_boosts.get(normalized_section, 0.0)
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
    return chunks


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


def print_sources(chunks: list[dict[str, Any]]) -> None:
    print("Retrieved Sources:")
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


def print_citations(chunks: list[dict[str, Any]]) -> None:
    print("Citations:")
    if not chunks:
        print("- none")
        return
    for chunk in chunks:
        print(f"[{chunk['source_id']}] {chunk['source_file']} — {chunk['section']}")


def context_warning(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "Warning: no retrieved context was available."
    best_distance = min(float(chunk["distance"]) for chunk in chunks)
    if best_distance > 1.0:
        return f"Warning: retrieved context may be weak. Best distance: {best_distance}"
    return ""


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

    chunks = retrieve_chunks(args.question, args.top_k, args.include_low_value_sections)
    context_packet = build_context_packet(chunks)

    print(f"Question: {args.question}")
    print()
    print_sources(chunks)

    warning = context_warning(chunks)
    if warning:
        print()
        print(warning)

    if args.show_context:
        print()
        print("Context Packet:")
        print(context_packet or "[empty]")

    if args.no_ai:
        print()
        print("AI skipped because --no-ai was used.")
        print_citations(chunks)
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
    print_citations(chunks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
