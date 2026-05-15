from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from typing import Any

import chromadb
import yaml
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "safepassage_vault_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_DIR = REPO_ROOT / "vault"
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)
    if not match:
        return {}, markdown

    raw_frontmatter = match.group(1)
    body = markdown[match.end() :]
    parsed = yaml.safe_load(raw_frontmatter) or {}
    if not isinstance(parsed, dict):
        return {}, body
    return parsed, body


def normalize_metadata_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def split_sections(body: str) -> list[tuple[str, str]]:
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(body))
    sections: list[tuple[str, str]] = []

    if not matches:
        content = body.strip()
        return [("Document", content)] if content else []

    intro = body[: matches[0].start()].strip()
    if intro:
        sections.append(("Document", intro))

    for index, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        if content:
            sections.append((heading, content))

    return sections


def stable_chunk_id(relative_path: str, section: str) -> str:
    digest = hashlib.sha256(f"{relative_path}::{section}".encode("utf-8")).hexdigest()
    return digest[:32]


def iter_markdown_files(include_archive: bool) -> list[Path]:
    files = sorted(VAULT_DIR.rglob("*.md"))
    if include_archive:
        return files
    return [path for path in files if "99_Archive" not in path.relative_to(VAULT_DIR).parts]


def build_chunks(include_archive: bool) -> tuple[list[str], list[str], list[dict[str, str]]]:
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []

    for markdown_path in iter_markdown_files(include_archive):
        raw = markdown_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw)
        relative_path = markdown_path.relative_to(REPO_ROOT).as_posix()
        title = normalize_metadata_value(frontmatter.get("title")) or markdown_path.stem
        doc_type = normalize_metadata_value(frontmatter.get("type")) or "unknown"
        community = normalize_metadata_value(frontmatter.get("community")) or "global"
        priority = normalize_metadata_value(frontmatter.get("priority"))
        tags = normalize_metadata_value(frontmatter.get("tags"))
        status = normalize_metadata_value(frontmatter.get("status"))

        for section, content in split_sections(body):
            chunk_text = "\n".join(
                [
                    f"Title: {title}",
                    f"Section: {section}",
                    f"Type: {doc_type}",
                    f"Community: {community}",
                    "",
                    content,
                ]
            ).strip()

            ids.append(stable_chunk_id(relative_path, section))
            documents.append(chunk_text)
            metadatas.append(
                {
                    "title": title,
                    "section": section,
                    "source_file": relative_path,
                    "type": doc_type,
                    "community": community,
                    "priority": priority,
                    "tags": tags,
                    "status": status,
                }
            )

    return ids, documents, metadatas


def main() -> int:
    parser = argparse.ArgumentParser(description="Index SafePassage Markdown vault chunks into local ChromaDB.")
    parser.add_argument("--include-archive", action="store_true", help="Include vault/99_Archive markdown files.")
    args = parser.parse_args()

    if not VAULT_DIR.exists():
        raise SystemExit(f"Vault directory not found: {VAULT_DIR}")

    ids, documents, metadatas = build_chunks(include_archive=args.include_archive)
    if not documents:
        raise SystemExit("No Markdown chunks found to index.")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    indexed_files = len(set(metadata["source_file"] for metadata in metadatas))
    print(f"Indexed {len(documents)} chunks from {indexed_files} files.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Chroma path: {CHROMA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
