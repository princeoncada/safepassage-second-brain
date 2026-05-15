from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import shorten

import chromadb
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "safepassage_vault_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve Markdown chunks from the local SafePassage ChromaDB index.")
    parser.add_argument("query", help="Question or search phrase to retrieve against the vault index.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve. Default: 5.")
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
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=args.top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        print("No chunks returned.")
        return 0

    for index, document in enumerate(documents, start=1):
        metadata = metadatas[index - 1] or {}
        distance = distances[index - 1] if index - 1 < len(distances) else None
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
