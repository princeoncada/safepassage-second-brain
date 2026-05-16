from __future__ import annotations

import argparse
import hashlib
import json
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
CONFIG_PATH = REPO_ROOT / "rag" / "config" / "retrieval_config.json"


DEFAULT_LOW_VALUE_SECTIONS = {"change history", "open questions", "source input"}
DEFAULT_PREFERRED_SECTIONS = {"summary", "details", "agent action", "qa notes"}
DEFAULT_NEAR_DUPLICATE_SIMILARITY_THRESHOLD = 0.9
DEFAULT_AUTHORITY_BY_TYPE = {
    "post_order": "post_order",
    "announcement": "announcement",
    "workflow": "primary_workflow",
}


def load_retrieval_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {
            "low_value_sections": sorted(DEFAULT_LOW_VALUE_SECTIONS),
            "preferred_sections": sorted(DEFAULT_PREFERRED_SECTIONS),
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_section_name(section: str) -> str:
    return re.sub(r"\s+", " ", section.strip()).lower()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def token_set(value: str) -> set[str]:
    return {token for token in normalize_key(value).split() if len(token) > 2}


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    markdown = markdown.lstrip("\ufeff")
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


def content_fingerprint(doc_type: str, community: str, section: str, content: str) -> str:
    normalized = " ".join(content.lower().split())
    basis = f"{doc_type.lower()}::{community.lower()}::{section.lower()}::{normalized}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def is_near_duplicate(
    existing_chunks: list[dict[str, str]],
    doc_type: str,
    community: str,
    section: str,
    content: str,
    threshold: float,
) -> bool:
    normalized_type = normalize_key(doc_type)
    normalized_community = normalize_key(community)
    normalized_section = normalize_key(section)
    for existing in existing_chunks:
        if existing["normalized_type"] != normalized_type:
            continue
        if existing["normalized_community"] != normalized_community:
            continue
        if existing["normalized_section"] != normalized_section:
            continue
        if jaccard_similarity(existing["content"], content) >= threshold:
            return True
    return False


def iter_markdown_files(include_archive: bool) -> list[Path]:
    files = sorted(VAULT_DIR.rglob("*.md"))
    if include_archive:
        return files
    return [path for path in files if "99_Archive" not in path.relative_to(VAULT_DIR).parts]


def build_chunks(include_archive: bool, include_low_value_sections: bool) -> tuple[list[str], list[str], list[dict[str, str]]]:
    config = load_retrieval_config()
    low_value_sections = {normalize_section_name(section) for section in config.get("low_value_sections", [])}
    preferred_sections = {normalize_section_name(section) for section in config.get("preferred_sections", [])}
    near_duplicate_threshold = float(
        config.get("near_duplicate_similarity_threshold", DEFAULT_NEAR_DUPLICATE_SIMILARITY_THRESHOLD)
    )
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []
    seen_fingerprints: set[str] = set()
    seen_semantic_chunks: list[dict[str, str]] = []
    skipped_low_value = 0
    skipped_duplicates = 0

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
        authority_level = normalize_metadata_value(frontmatter.get("authority_level"))
        if not authority_level:
            authority_level = DEFAULT_AUTHORITY_BY_TYPE.get(normalize_key(doc_type).replace(" ", "_"), "")
        scope = normalize_metadata_value(frontmatter.get("scope"))
        scope_key = normalize_metadata_value(frontmatter.get("scope_key"))
        community_code = normalize_metadata_value(frontmatter.get("community_code"))
        announcement_id = normalize_metadata_value(frontmatter.get("announcement_id"))
        announcement_hash = normalize_metadata_value(frontmatter.get("announcement_hash"))
        category = normalize_metadata_value(frontmatter.get("category"))
        rule_id = normalize_metadata_value(frontmatter.get("rule_id"))
        rule_hash = normalize_metadata_value(frontmatter.get("rule_hash"))
        source_batch = normalize_metadata_value(frontmatter.get("source_batch"))
        source_name = normalize_metadata_value(frontmatter.get("source_name"))
        batch_date = normalize_metadata_value(frontmatter.get("batch_date"))
        effective_date = normalize_metadata_value(frontmatter.get("effective_date"))
        expires_on = normalize_metadata_value(frontmatter.get("expires_on"))
        event_dates = normalize_metadata_value(frontmatter.get("event_dates"))
        update_type = normalize_metadata_value(frontmatter.get("update_type"))
        supersede_mode = normalize_metadata_value(frontmatter.get("supersede_mode"))
        supersedes = normalize_metadata_value(frontmatter.get("supersedes"))
        superseded_by = normalize_metadata_value(frontmatter.get("superseded_by"))
        topic_key = normalize_metadata_value(frontmatter.get("topic_key"))
        source_legacy_file = normalize_metadata_value(frontmatter.get("source_legacy_file"))
        source_migration = normalize_metadata_value(frontmatter.get("source_migration"))
        migration_date = normalize_metadata_value(frontmatter.get("migration_date"))
        lifecycle_generation = normalize_metadata_value(frontmatter.get("lifecycle_generation"))
        if not lifecycle_generation and normalize_key(doc_type).replace(" ", "_") == "post_order":
            lifecycle_generation = "managed" if rule_id or rule_hash or source_batch else "legacy"

        for section, content in split_sections(body):
            normalized_section = normalize_section_name(section)
            is_low_value = normalized_section in low_value_sections
            if is_low_value and not include_low_value_sections:
                skipped_low_value += 1
                continue

            fingerprint = content_fingerprint(doc_type, community, section, content)
            if fingerprint in seen_fingerprints:
                skipped_duplicates += 1
                continue
            if is_near_duplicate(seen_semantic_chunks, doc_type, community, section, content, near_duplicate_threshold):
                skipped_duplicates += 1
                continue
            seen_fingerprints.add(fingerprint)
            seen_semantic_chunks.append(
                {
                    "normalized_type": normalize_key(doc_type),
                    "normalized_community": normalize_key(community),
                    "normalized_section": normalize_key(section),
                    "content": content,
                }
            )

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
                    "authority_level": authority_level,
                    "scope": scope,
                    "scope_key": scope_key,
                    "community_code": community_code,
                    "announcement_id": announcement_id,
                    "announcement_hash": announcement_hash,
                    "category": category,
                    "rule_id": rule_id,
                    "rule_hash": rule_hash,
                    "source_batch": source_batch,
                    "source_name": source_name,
                    "batch_date": batch_date,
                    "effective_date": effective_date,
                    "expires_on": expires_on,
                    "event_dates": event_dates,
                    "update_type": update_type,
                    "supersede_mode": supersede_mode,
                    "supersedes": supersedes,
                    "superseded_by": superseded_by,
                    "topic_key": topic_key,
                    "source_legacy_file": source_legacy_file,
                    "source_migration": source_migration,
                    "migration_date": migration_date,
                    "lifecycle_generation": lifecycle_generation,
                    "tags": tags,
                    "status": status,
                    "is_low_value_section": str(is_low_value).lower(),
                    "is_preferred_section": str(normalized_section in preferred_sections).lower(),
                    "content_fingerprint": fingerprint,
                    "normalized_title": normalize_key(title),
                    "normalized_community": normalize_key(community),
                    "normalized_section": normalize_key(section),
                }
            )

    print(f"Skipped low-value sections: {skipped_low_value}")
    print(f"Skipped duplicate chunks: {skipped_duplicates}")
    return ids, documents, metadatas


def main() -> int:
    parser = argparse.ArgumentParser(description="Index SafePassage Markdown vault chunks into local ChromaDB.")
    parser.add_argument("--include-archive", action="store_true", help="Include vault/99_Archive markdown files.")
    parser.add_argument(
        "--include-low-value-sections",
        action="store_true",
        help="Index low-value sections such as Change History, Open Questions, and Source Input.",
    )
    args = parser.parse_args()

    if not VAULT_DIR.exists():
        raise SystemExit(f"Vault directory not found: {VAULT_DIR}")

    ids, documents, metadatas = build_chunks(
        include_archive=args.include_archive,
        include_low_value_sections=args.include_low_value_sections,
    )
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
