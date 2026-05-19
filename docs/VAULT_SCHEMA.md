# Vault Schema

This document defines the frontmatter fields used by SafePassage vault Markdown files and OCR review artifacts. The vault remains the source of truth; ChromaDB stores selected frontmatter values as derived metadata for retrieval, dashboard grouping, citations, and audit context.

## Document Types

| Type | Folder | Meaning |
| --- | --- | --- |
| `post_order` | `vault/03_Post_Orders/` | Community-specific operational rule. Highest authority. Managed post orders include lifecycle fields, rule hashes, scope, and source batch metadata. |
| `announcement` | `vault/05_Announcements/` | Managed reminder, issue, event, temporary protocol, approved-vendor notice, or compliance warning. Lower than post orders and higher than primary workflow. |
| `qa_rule` | `vault/04_QA_Rules/` | QA/compliance guidance or advisory note. Supports answers but must not override post orders. |
| `workflow` | `vault/09_SOPs/` and older routed workflow folders | Primary workflow or SOP-style guidance. When `authority_level: primary_workflow`, it is global default guidance. |
| `incident` | `vault/06_Incidents/` | Incident record or operational event history. Dashboard currently excludes incidents from shift briefing sections. |
| `visitor_log` | `vault/07_Visitor_Logs/` | Visitor/tag/vendor log record. Dashboard currently excludes visitor logs. |
| `unknown` | `vault/00_Inbox/` | Unclassified input requiring human review. Not trusted as operational guidance. |
| `briefing` | `vault/01_Daily_Briefings/` | Daily briefing or shift summary from the Phase 2 routing contract. Dashboard excludes daily briefings. |
| `community_profile` | `vault/02_Communities/` | Community profile or reference record from the Phase 2 routing contract. |
| `script` | `vault/05_Scripts/` | Scripted operator wording from the Phase 2 routing contract. Current primary scripts mostly live as `workflow` SOPs. |
| `training` | `vault/08_Training/` | Training reference material from the Phase 2 routing contract. |
| `sop` | `vault/09_SOPs/` | SOP classification from the routing contract. Current SOP files generally use `type: workflow`. |
| `automation` | `vault/10_Automations/` | Automation note or workflow documentation from the Phase 2 routing contract. |
| `code_snippet` | `vault/11_Code_Snippets/` | Code reference from the Phase 2 routing contract. |
| `archived` | `vault/99_Archive/` | Archived routed item. Not current operational guidance. |

## Authority Hierarchy

| authority_level | Meaning | Retrieval effect |
| --- | --- | --- |
| `post_order` | Active community post order. | Highest boost. Overrides announcements and primary workflow. |
| `announcement` | Managed operational reminder or notice. | Medium boost. Can supplement post orders but cannot override them. |
| `primary_workflow` | Global default workflow/SOP. | Lowest operational authority. Used when no higher community-specific source applies or when the user asks for default workflow. |
| `qa_rule` | Advisory QA or compliance guidance. | Supporting context only. Must not supersede post orders. |

Required hierarchy:

```text
post_order > announcement > primary_workflow
```

## Status Values

| status | Meaning | Retrieval effect |
| --- | --- | --- |
| `active` | Current usable source. | Boosted and preferred. |
| `pending` | Future or not-yet-active instruction. | Included with warning/advisory treatment; does not override active. |
| `superseded` | Replaced by a newer managed rule. | Heavily penalized or skipped. |
| `archived` | Preserved for history, not current. | Skipped by default indexing/retrieval paths unless archive inclusion is requested. |
| `conflict` | Ingestion found possible contradictory rules. | Penalized; requires manual review before reliance. |
| `review` | Needs human review due to ambiguous or multi-community parsing. | Penalized and excluded from dashboard. |
| `needs_review` | Legacy or inbox-style item needing review. | Penalized; not trusted as active operational guidance. |
| `expired` | Time-bounded item is no longer current. | Penalized/refusal-prone when no active source exists. |

Lifecycle priority:

```text
active > pending > superseded/archived/expired/unknown
```

## Field Reference

| Field | Type | Required | Valid values / examples | Used by | Controls |
| --- | --- | --- | --- | --- | --- |
| `title` | string | Required for indexed vault docs | Human-readable title | All vault document types | Indexed title, citations, dashboard labels, chunk text. |
| `type` | string | Required | See Document Types | All vault document types | Folder meaning, authority inference, expected-type filtering, dashboard grouping. |
| `community` | string | Required | Canonical community name or `global` | All operational docs | Community filtering, alias matching, refusal for missing community matches. |
| `community_code` | string | Optional | `SR`, `CBK`, `GLEN`, blank for global | Managed post orders, announcements, QA rules | Tags, operator traceability, source metadata. |
| `scope` | list or string | Optional | `kiosk`, `concierge`, both | Post orders, QA rules, workflow | Scope display and scoped retrieval support. |
| `scope_key` | string | Required for managed scoped rules | `k`, `c`, `kc` | Post orders, QA rules | Kiosk/concierge filtering and ordering. |
| `authority_level` | string | Required for managed docs; inferred for some legacy docs | `post_order`, `announcement`, `primary_workflow`, `qa_rule` | Post orders, announcements, workflows, QA rules | Authority scoring and conflict hierarchy. |
| `status` | string | Required | `active`, `pending`, `superseded`, `archived`, `conflict`, `review`, `needs_review`, `expired` | All vault document types | Retrieval boosts/penalties, dashboard inclusion, lifecycle warnings. |
| `lifecycle_generation` | string | Required for managed lifecycle docs | `managed`, `legacy`, `archived` | Post orders, announcements, QA rules | Managed-source boost; legacy skip by default; archival treatment. |
| `lifecycle_status` | string | Optional | Freeform lifecycle label | Indexed docs | API source metadata and dashboard display. |
| `rule_id` | string | Required for managed post orders and rule-like QA tips | Slug with community/scope/topic/hash | Post orders, QA rules | Supersede links, citations, ingestion diffing. |
| `rule_hash` | string | Required for managed post orders | SHA-256 hash | Post orders | Duplicate detection and lifecycle diffing. |
| `topic_key` | string | Required for managed post orders | Slug from normalized rule tokens | Post orders | Same-topic supersede detection and conflict scanning. |
| `normalized_rule` | string | Required for managed post orders | Lowercase normalized rule text | Post orders | Duplicate/conflict detection and review reports. |
| `announcement_id` | string | Required for managed announcements | Slug with community/category/hash | Announcements | Identity in reports and source metadata. |
| `announcement_hash` | string | Required for managed announcements | SHA-256 hash | Announcements | Duplicate detection. |
| `normalized_announcement` | string | Required for managed announcements | Lowercase normalized announcement text | Announcements | Reranking, dashboard scoring, duplicate review. |
| `source_batch` | string | Required for managed ingestion output | `automation/ingestion/...md` | Post orders, announcements | Traceability to pasted batch/staging input. |
| `source_name` | string | Optional | `Daily Reminders` | Announcements | Source traceability and API metadata. |
| `batch_date` | date string | Required for managed ingestion output | `YYYY-MM-DD` | Post orders, announcements | Effective default, reports, traceability. |
| `update_type` | string | Optional | `partial`, `full` | Post orders, announcements | Refresh report behavior and traceability. |
| `supersede_mode` | string | Optional | `conservative` | Post orders | Controls whether possible same-topic changes become review items. |
| `supersedes` | string | Optional | Prior `rule_id` or blank | Managed post orders | Links replacement rule to old rule. |
| `superseded_by` | string | Optional | Newer `rule_id` or blank | Managed post orders | Marks old rule as replaced. |
| `source_legacy_file` | string | Optional | `vault/...md` | Migrated post orders | Links managed copy to preserved legacy source. |
| `source_migration` | string | Optional | Migration report path/name | Migrated post orders | Audit trail for migration. |
| `migration_date` | date string | Optional | `YYYY-MM-DD` | Migrated post orders | Migration audit metadata. |
| `temporal_state` | string | Derived or optional explicit | `active`, `pending`, `not_yet_active`, `expired`, `superseded`, `archived`, `review`, `unknown` | Indexed metadata | Retrieval lifecycle assessment and dashboard exclusion. |
| `effective_date` | date string | Optional but common | `YYYY-MM-DD` | All operational docs | Temporal start date and source freshness. |
| `active_from` | date string | Optional | `YYYY-MM-DD` | Time-bounded docs | Temporal start date. |
| `start_date` | date string | Optional | `YYYY-MM-DD` | Time-bounded docs | Temporal start date. |
| `expiry_date` | date string | Optional | `YYYY-MM-DD` | Time-bounded docs | Temporal end date and expiring-soon dashboard logic. |
| `active_until` | date string | Optional | `YYYY-MM-DD` | Time-bounded docs | Temporal end date. |
| `expires_at` | date/datetime string | Optional | ISO date or datetime | Time-bounded docs | Temporal end date. |
| `expires_on` | date string | Optional | `YYYY-MM-DD` or blank | Announcements | Expiry/lifecycle and dashboard expiring-soon grouping. |
| `end_date` | date string | Optional | `YYYY-MM-DD` | Time-bounded docs | Temporal end date. |
| `event_dates` | list of dates | Optional | `["2026-05-13"]` | Event announcements | Event context and source metadata. |
| `temporal_warning` | string | Derived or optional explicit | Warning text | Indexed metadata | API warnings when temporal metadata is missing, stale, or uncertain. |
| `category` | string | Required for announcements; optional elsewhere | `approved_vendor`, `event`, `gate_issue`, `nvr_issue`, `temporary_protocol`, `traffic_handling`, `compliance_warning`, `community_announcement`, `global_reminder` | Announcements, dashboard | Reranking, dashboard grouping, priority scoring. |
| `priority` | string | Optional | `low`, `medium`, `high`, `critical` | Legacy/routed docs | Indexed metadata and future prioritization. |
| `tags` | list | Optional but common | `post_order`, community slug, phase tag | All vault document types | Search metadata and human organization. |
| `created` | date/datetime string | Optional | ISO date/datetime | Legacy docs | Human audit trail. |
| `created_at` | datetime string | Optional but common for managed docs | ISO datetime | Managed post orders, announcements, OCR reviews | Human audit trail; not central to retrieval scoring. |
| `updated` | date/datetime string | Optional | ISO date/datetime | Legacy docs | Human audit trail. |
| `last_updated` | date/datetime string | Optional but common | ISO date/datetime | Vault docs | Human audit trail; updated during supersede operations. |
| `version` | string | Optional | `1.0` | Legacy/routed docs | Document schema/version traceability. |
| `source_file` | string | Derived by indexer | `vault/...md` | ChromaDB metadata/API sources | Citation path and audit source list. |
| `approved_for_ingestion` | boolean | Required for OCR review bridge | `true`, `false` | OCR review Markdown | Must be `true` before bridge staging. |
| `review_status` | string | Required for OCR review bridge | `pending_review`, `approved`, `rejected` | OCR review Markdown | Must be `approved` before bridge staging. |
| `target_ingestion_type` | string | Required for OCR review bridge | `announcement`, `post_order`, `none` | OCR review Markdown | Selects reviewed OCR staging output. |
| `reviewed_by` | string | Optional | Reviewer name/initials | OCR review Markdown | Human audit metadata. |
| `reviewed_at` | date/datetime string | Optional | ISO date/datetime | OCR review Markdown | Human audit metadata. |
| `review_notes` | string | Optional | Freeform notes | OCR review Markdown | Human review notes; not used by retrieval. |

## Retrieval Notes

The indexer stores only selected fields as ChromaDB metadata. It also derives `source_file`, normalized title/community/section fields, temporal lifecycle fields, low-value section flags, preferred-section flags, and content fingerprints.

Low-value sections such as `Change History`, `Open Questions`, and `Source Input` are skipped by default during indexing. `Source`, `Migration Notes`, and `Operational Notes` may be penalized during reranking for direct answer questions.

Malformed or missing frontmatter can produce weak retrieval, wrong filtering, or missing dashboard items. Future schema hardening should validate these fields before ingestion writes any vault Markdown.
