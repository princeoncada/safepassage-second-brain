from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ALIASES_PATH = REPO_ROOT / "rag" / "config" / "community_aliases.json"
TOPICS_PATH = REPO_ROOT / "rag" / "config" / "query_topics.json"

NON_COMMUNITY_TOPICS = {
    "red zone protocol",
    "support room",
    "community approved list",
    "physical id",
    "digital id",
    "pickleball tournament",
    "emergency code",
    "gate issue",
    "nvr issue",
    "id viewer",
    "resident call",
    "voicemail",
    "marked vendor vehicles",
    "pre authorized",
    "preauthorized",
}

UNKNOWN_COMMUNITY_CONTEXTS = [
    "for",
    "at",
    "in",
    "community",
    "policy for",
    "rule for",
    "rules for",
    "vehicle policy for",
    "access rules for",
]

IGNORED_PROPER_PHRASES = {
    "what",
    "source input",
    "open questions",
    "change history",
    "agent action",
    "red zone protocol",
    "support room",
    "community approved list",
    "physical id",
    "digital id",
    "pickleball tournament",
    "emergency code",
}

KIOSK_SCOPE_PHRASES = {
    "for kiosk",
    "kiosk only",
    "kiosk agent",
    "kiosk post orders",
    "kiosk specifically",
    "kiosk rules",
}

CONCIERGE_SCOPE_PHRASES = {
    "for concierge",
    "concierge only",
    "concierge agent",
    "concierge post orders",
    "concierge specifically",
    "concierge rules",
}

REQUESTED_ALL_PHRASES = {
    "complete list",
    "all post orders",
    "all kiosk",
    "all concierge",
    "full list",
    "every post order",
    "list all",
    "all rules",
    "all the post orders",
    "give me all",
    "show me all",
    "all active",
    "full post order",
    "relevant to kiosk",
    "for kiosk agents",
    "relevant to concierge",
    "for concierge agents",
    "kiosk post orders",
    "concierge post orders",
    "all kiosk post orders",
    "all concierge post orders",
}


@dataclass
class QueryIntent:
    original_query: str
    normalized_query: str
    community: str = ""
    community_alias: str = ""
    missing_community: str = ""
    expected_types: set[str] = field(default_factory=set)
    intent_category: str = "unknown"
    topic_terms: list[str] = field(default_factory=list)
    scope_hint: str = ""
    requested_all: bool = False
    is_default_workflow_query: bool = False
    is_global_query: bool = False
    warnings: list[str] = field(default_factory=list)

    def as_hints(self) -> dict[str, Any]:
        return {
            "community": self.community,
            "community_alias": self.community_alias,
            "missing_community": self.missing_community,
            "expected_types": self.expected_types,
            "intent_category": self.intent_category,
            "topic_terms": self.topic_terms,
            "scope_hint": self.scope_hint,
            "requested_all": self.requested_all,
            "is_default_workflow_query": self.is_default_workflow_query,
            "is_global_query": self.is_global_query,
            "warnings": self.warnings,
        }


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        parsed = json.load(file)
    return parsed if isinstance(parsed, dict) else {}


def load_community_aliases() -> dict[str, str]:
    return {str(key).upper(): str(value) for key, value in load_json(ALIASES_PATH).items()}


def load_query_topics() -> dict[str, dict[str, Any]]:
    topics = load_json(TOPICS_PATH)
    return {normalize_key(key): value for key, value in topics.items() if isinstance(value, dict)}


def alias_tokens(query: str) -> list[str]:
    tokens = re.findall(r"\b[A-Za-z]{2,20}\d*\b", query)
    output: list[str] = []
    for token in tokens:
        match = re.match(r"[A-Za-z]+", token)
        if match:
            output.append(match.group(0).upper())
    return output


def known_community_map(known_communities: set[str]) -> dict[str, str]:
    aliases = load_community_aliases()
    communities = {normalize_key(community): community for community in known_communities if community}
    communities.update({normalize_key(community): community for community in aliases.values() if community})
    return communities


def detect_topic(intent: QueryIntent) -> None:
    topics = load_query_topics()
    for topic, metadata in topics.items():
        if topic and topic in intent.normalized_query:
            intent.topic_terms.append(topic)
            intent.expected_types.update(str(item) for item in metadata.get("expected_types", []))
            if intent.intent_category == "unknown":
                intent.intent_category = str(metadata.get("intent_category", "unknown"))
            if metadata.get("is_global_allowed"):
                intent.is_global_query = True


def detect_keyword_intent(intent: QueryIntent) -> None:
    query = intent.normalized_query
    if any(term in query for term in ["default", "by default", "base workflow", "primary workflow"]):
        intent.is_default_workflow_query = True
        intent.is_global_query = True
        intent.intent_category = "default_workflow"
        intent.expected_types.update({"primary_workflow", "workflow"})
    if any(term in query for term in ["reminder", "announcement"]):
        intent.expected_types.add("announcement")
        if intent.intent_category == "unknown":
            intent.intent_category = "reminder"
    if any(term in query for term in ["event", "tournament"]):
        intent.expected_types.add("announcement")
        intent.intent_category = "event"
    if any(term in query for term in ["gate issue", "kiosk audio", "barrier arm"]):
        intent.expected_types.add("announcement")
        intent.intent_category = "gate_issue"
    if "nvr" in query:
        intent.expected_types.add("announcement")
        intent.intent_category = "nvr_issue"
    if any(term in query for term in ["post order", "rule", "policy", "physical id", "digital id"]):
        intent.expected_types.update({"post_order", "qa_rule"})
        if intent.intent_category == "unknown":
            intent.intent_category = "policy"
    if any(term in query for term in ["incident", "happened", "tailgating", "tailgate"]):
        intent.expected_types.add("incident")
        intent.intent_category = "incident"
    if any(term in query for term in ["visitor log", "tag", "vendor"]):
        intent.expected_types.add("visitor_log")
        if intent.intent_category == "unknown":
            intent.intent_category = "visitor_log"
    if "emergency code" in query:
        intent.expected_types.update({"post_order", "announcement"})
        intent.intent_category = "emergency_code"


def detect_scope(intent: QueryIntent) -> None:
    query = intent.normalized_query
    if any(phrase in query for phrase in KIOSK_SCOPE_PHRASES):
        intent.scope_hint = "kiosk"
        return
    if any(phrase in query for phrase in CONCIERGE_SCOPE_PHRASES):
        intent.scope_hint = "concierge"
        return
    if any(term in query for term in ["kiosk", "gate", "visitor", "vendor", "access"]):
        intent.scope_hint = "kiosk"
    if any(term in query for term in ["concierge", "caller", "call resident"]):
        intent.scope_hint = "concierge"


def detect_requested_all(intent: QueryIntent) -> None:
    if any(phrase in intent.normalized_query for phrase in REQUESTED_ALL_PHRASES):
        intent.requested_all = True
    if intent.scope_hint and intent.community and "post_order" in intent.expected_types:
        intent.requested_all = True


def phrase_is_operational_topic(phrase: str) -> bool:
    normalized = normalize_key(phrase)
    if normalized in NON_COMMUNITY_TOPICS:
        return True
    return any(topic in normalized or normalized in topic for topic in NON_COMMUNITY_TOPICS)


def unknown_community_phrase(query: str, known_communities: set[str]) -> str:
    normalized_query = normalize_key(query)
    proper_phrases = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", query)
    known = known_community_map(known_communities)
    for phrase in proper_phrases:
        normalized_phrase = normalize_key(phrase)
        if normalized_phrase in IGNORED_PROPER_PHRASES or phrase_is_operational_topic(phrase):
            continue
        if normalized_phrase in known:
            continue
        for context in UNKNOWN_COMMUNITY_CONTEXTS:
            if re.search(rf"\b{re.escape(context)}\s+{re.escape(normalized_phrase)}\b", normalized_query):
                return phrase
    return ""


def parse_query_intent(query: str, known_communities: set[str] | None = None) -> QueryIntent:
    known_communities = known_communities or set()
    intent = QueryIntent(original_query=query, normalized_query=normalize_key(query))
    aliases = load_community_aliases()
    for token in alias_tokens(query):
        if token in aliases:
            intent.community = aliases[token]
            intent.community_alias = token
            break

    if not intent.community:
        sorted_names = sorted(
            aliases.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )
        for alias_key, community_name in sorted_names:
            normalized_name = normalize_key(community_name)
            if normalized_name and normalized_name in intent.normalized_query:
                intent.community = community_name
                intent.community_alias = alias_key
                break

    communities = known_community_map(known_communities)
    if not intent.community:
        for normalized_community, original in communities.items():
            if normalized_community and re.search(rf"\b{re.escape(normalized_community)}\b", intent.normalized_query):
                intent.community = original
                break

    detect_topic(intent)
    detect_keyword_intent(intent)
    detect_requested_all(intent)
    detect_scope(intent)
    if intent.scope_hint and intent.community and "post_order" in intent.expected_types:
        intent.requested_all = True

    if not intent.community:
        intent.missing_community = unknown_community_phrase(query, known_communities)

    if not intent.community and not intent.missing_community and intent.is_global_query:
        intent.community = ""

    return intent


def expand_query_with_intent(intent: QueryIntent) -> str:
    if intent.community:
        topic_suffix = " ".join(intent.topic_terms)
        return " ".join(part for part in [intent.original_query, intent.community, topic_suffix] if part)
    if intent.topic_terms:
        return f"{intent.original_query} {' '.join(intent.topic_terms)}"
    return intent.original_query
