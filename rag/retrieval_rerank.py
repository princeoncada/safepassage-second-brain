from __future__ import annotations

import re
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


def normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def token_set(value: Any) -> set[str]:
    return {token for token in normalize_key(value).split() if len(token) > 2 and token not in STOPWORDS}


def overlap_ratio(left: Any, right: Any) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def phrase_present(phrase: str, value: Any) -> bool:
    normalized_phrase = normalize_key(phrase)
    normalized_value = normalize_key(value)
    return bool(normalized_phrase) and re.search(rf"\b{re.escape(normalized_phrase)}\b", normalized_value) is not None


def topic_terms(hints: dict[str, Any]) -> list[str]:
    terms = [str(term) for term in hints.get("topic_terms", []) if str(term).strip()]
    if hints.get("intent_category") and hints.get("intent_category") != "unknown":
        terms.append(str(hints["intent_category"]).replace("_", " "))
    return terms


def metadata_text(metadata: dict[str, Any], *keys: str) -> str:
    return " ".join(str(metadata.get(key, "")) for key in keys if metadata.get(key, ""))


def resolve_scope_key(metadata: dict[str, Any]) -> str:
    scope_key = str(metadata.get("scope_key", "")).strip().lower()
    if scope_key in {"k", "c", "kc"}:
        return scope_key
    scope_raw = metadata.get("scope", "")
    if isinstance(scope_raw, list):
        values = {str(value).strip().lower() for value in scope_raw}
    else:
        values = {
            value.strip().lower().strip("'\"[]")
            for value in str(scope_raw).split(",")
            if value.strip()
        }
    if "kiosk" in values and "concierge" in values:
        return "kc"
    if "kiosk" in values:
        return "k"
    if "concierge" in values:
        return "c"
    return ""


def rerank_adjustment(
    *,
    query: str,
    document: str,
    metadata: dict[str, Any],
    hints: dict[str, Any],
    config: dict[str, Any],
) -> tuple[float, list[str]]:
    adjustment = 0.0
    reasons: list[str] = []
    title = str(metadata.get("title", ""))
    category = str(metadata.get("category", ""))
    section = str(metadata.get("section", ""))
    doc_type = str(metadata.get("type", ""))
    normalized_announcement = str(metadata.get("normalized_announcement", ""))
    title_and_body = " ".join([title, normalized_announcement, document])

    section_penalties = {
        str(name).lower(): float(value)
        for name, value in config.get("section_penalties", {}).items()
    }
    penalty = section_penalties.get(normalize_key(section), 0.0)
    if penalty:
        adjustment += penalty
        reasons.append(f"section_penalty:{normalize_key(section)}:+{penalty:.2f}")

    section_boosts = {
        str(name).lower(): float(value)
        for name, value in config.get("direct_answer_section_boosts", {}).items()
    }
    boost = section_boosts.get(normalize_key(section), 0.0)
    if boost:
        adjustment -= boost
        reasons.append(f"section_boost:{normalize_key(section)}:-{boost:.2f}")

    title_overlap = overlap_ratio(query, title)
    if title_overlap:
        weighted = min(title_overlap * float(config.get("title_overlap_boost", 0.22)), 0.3)
        adjustment -= weighted
        reasons.append(f"title_overlap:{title_overlap:.2f}:-{weighted:.2f}")

    body_overlap = overlap_ratio(query, title_and_body)
    if body_overlap:
        weighted = min(body_overlap * float(config.get("keyword_overlap_boost", 0.16)), 0.22)
        adjustment -= weighted
        reasons.append(f"keyword_overlap:{body_overlap:.2f}:-{weighted:.2f}")

    for topic in topic_terms(hints):
        normalized_topic = normalize_key(topic)
        if phrase_present(topic, title):
            boost = float(config.get("exact_topic_title_boost", 0.45))
            adjustment -= boost
            reasons.append(f"exact_topic_title:{normalized_topic}:-{boost:.2f}")
        elif phrase_present(topic, normalized_announcement):
            boost = float(config.get("exact_topic_body_boost", 0.35))
            adjustment -= boost
            reasons.append(f"exact_topic_body:{normalized_topic}:-{boost:.2f}")
        elif phrase_present(topic, document):
            boost = float(config.get("exact_topic_chunk_boost", 0.25))
            adjustment -= boost
            reasons.append(f"exact_topic_chunk:{normalized_topic}:-{boost:.2f}")

    intent_category = normalize_key(str(hints.get("intent_category", "")))
    if intent_category and intent_category != "unknown":
        category_key = normalize_key(category)
        if intent_category == category_key:
            boost = float(config.get("category_match_boost", 0.18))
            adjustment -= boost
            reasons.append(f"category_match:{category_key}:-{boost:.2f}")

    if doc_type == "announcement" and normalize_key(section) == "announcement":
        boost = float(config.get("announcement_body_section_boost", 0.12))
        adjustment -= boost
        reasons.append(f"announcement_body_section:-{boost:.2f}")

    scope_hint = str(hints.get("scope_hint", "")).strip().lower()
    scope_key = resolve_scope_key(metadata)
    if scope_hint == "kiosk" and scope_key in {"k", "kc"}:
        boost = float(config.get("scope_match_boost", 0.20))
        adjustment -= boost
        reasons.append(f"scope_match:{scope_key}:-{boost:.2f}")
    elif scope_hint == "concierge" and scope_key in {"c", "kc"}:
        boost = float(config.get("scope_match_boost", 0.20))
        adjustment -= boost
        reasons.append(f"scope_match:{scope_key}:-{boost:.2f}")
    elif scope_hint == "kiosk" and scope_key == "c":
        penalty = float(config.get("scope_mismatch_penalty", 0.15))
        adjustment += penalty
        reasons.append(f"scope_mismatch:{scope_key}:+{penalty:.2f}")
    elif scope_hint == "concierge" and scope_key == "k":
        penalty = float(config.get("scope_mismatch_penalty", 0.15))
        adjustment += penalty
        reasons.append(f"scope_mismatch:{scope_key}:+{penalty:.2f}")

    return adjustment, reasons
