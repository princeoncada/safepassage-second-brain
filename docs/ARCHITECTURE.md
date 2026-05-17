# System Architecture

## Purpose
This project is a local-first AI-powered operational second brain for SafePassage-style kiosk operations, workflows, SOPs, post orders, QA rules, incidents, scripts, and compliance memory.

## Source of Truth
Markdown files inside the `vault/` folder are the canonical source of truth.

## Artifact Outputs
DOCX and PDF files are generated exports only. They are not the source of truth.

## Main Components

### Obsidian Vault
Stores human-readable Markdown documents.

### GitHub
Provides version history, rollback, audit trail, and collaboration safety.

### n8n
Handles the current stable Phase 2 Minimal POW ingestion webhook.

Current working ingestion flow:

```text
n8n webhook
-> deterministic classification/routing
-> optional DeepSeek Markdown cleanup
-> deterministic YAML/frontmatter creation
-> safe local vault write
```

The stable ingestion workflow is `workflows/n8n/phase_2_minimal_pow_ingestion_workflow.json`.

### DeepSeek API
Used optionally in Phase 2 Minimal POW to clean Markdown sections, with deterministic fallback when unavailable.

For Phase 3B, DeepSeek is used only for final answer generation from retrieved vault context. It must not retrieve, edit memory, or invent unsupported policy.

### ChromaDB
Used for local semantic retrieval and metadata-aware search.

ChromaDB is a local disposable index under `rag/chroma/`. It is rebuilt from Markdown in `vault/` and is not a source of truth.

### Open WebUI
Open WebUI is the Phase 3E conversational presentation layer only. It calls the local FastAPI `/ask` endpoint and is not the storage layer, retrieval layer, embedding layer, memory layer, or business-logic layer.

## Current Working Flow

### Ingestion

```text
n8n webhook
-> deterministic classification/routing
-> optional DeepSeek Markdown cleanup
-> deterministic YAML/frontmatter creation
-> safe local vault write
```

### Retrieval

```text
vault Markdown
-> section-based chunking
-> deterministic query intent parsing
-> local embeddings
-> ChromaDB
-> query_vault.py retrieval
-> heuristic dedupe/reranking
```

### Answering

```text
question
-> retrieve top chunks
-> deterministic confidence/refusal checks
-> DeepSeek answer generation
-> cite actually used source file + section
-> refuse when context is insufficient
```

Phase 3C adds heuristic quality hardening only: dedupe, reranking, citation cleanup, and conservative insufficient-context detection. It does not add new databases or UI layers.

### Local API

```text
HTTP request
-> FastAPI /ask endpoint
-> existing RAG retrieval/answer logic
-> JSON response with answer, citations, confidence, and retrieved sources
```

Phase 3D exposes local HTTP access only. FastAPI does not store memory, edit the vault, or replace the Markdown source of truth.

### Open WebUI

```text
Open WebUI
-> FastAPI /ask endpoint
-> retrieval
-> grounded answering
-> citations/refusal/confidence
```

Phase 3E uses Open WebUI only as the conversational presentation layer. Open WebUI must not own retrieval, embeddings, ChromaDB, ingestion, memory, or operational business logic.

### Phase 4A Retrieval Quality Hardening

```text
question
-> ChromaDB candidate retrieval
-> metadata-aware reranking
-> section weighting
-> near-duplicate suppression
-> selected context packet
-> grounded answer
-> answer citations only for used sources
```

Phase 4A keeps the same architecture and improves quality inside the retrieval and answer-selection layer. It does not add agents, new databases, n8n changes, Open WebUI custom UI changes, automatic memory editing, or workflow automation.

Section weighting prefers operationally useful sections in this order:

```text
Agent Action
Summary
Details
Rule
Policy
QA Notes
```

Low-value sections such as `Open Questions`, `Source Input`, and `Change History` remain excluded by default. When included for debugging, they are penalized so they do not dominate operational answers.

The API keeps retrieved `sources` separate from `answer_citations`. This lets Open WebUI render a single clean Sources section and avoids duplicated source lists in chat output.

### Phase 4B Primary Workflow Authority Layer

```text
primary workflow input
-> deterministic primary workflow ingester
-> vault/09_SOPs/primary-*.md
-> ChromaDB index
-> retrieval as default/base fallback
```

Primary workflow documents represent the base kiosk workflow. They are global default guidance and are lower authority than community-specific post orders and announcements.

Authority hierarchy:

```text
post_order
announcement
primary_workflow
```

When a question mentions a community, retrieval should prefer matching community post orders first, matching community announcements second, and global primary workflow only as fallback. If no community-specific source exists, the answer may use primary workflow only when it is clearly labeled as default guidance.

### Phase 4B2 Primary Workflow Fallback Confidence

Phase 4B2 keeps the global refusal threshold conservative and adds a separate fallback threshold for explicit default/base workflow questions.

Primary workflow fallback can be treated as usable only when:

- the query asks for default, base, or primary workflow guidance;
- retrieved context includes global `authority_level: primary_workflow`;
- no community-specific higher-authority source is being overridden;
- the best distance is within `primary_workflow_default_threshold`.

Unknown community-specific questions still refuse when no indexed community source exists. Global primary workflow must not be converted into community-specific policy.

### Phase 4C Batch Post Order Refresh

```text
post order batch input
-> deterministic parser
-> normalized atomic rules
-> SHA-256 rule hashes
-> duplicate/supersede/conflict/missing detection
-> post order Markdown lifecycle updates
-> refresh report
-> ChromaDB rebuild
```

Phase 4C starts lifecycle handling with `post_order` only because post orders are highest authority. It does not use AI for diffing and never deletes old rules.

Post order lifecycle metadata includes `rule_id`, `rule_hash`, `source_batch`, `batch_date`, `supersedes`, and `superseded_by`. Retrieval prefers `status: active` and penalizes `superseded`, `conflict`, `review`, and `inactive` documents if they are indexed.

### Phase 4C1 Lifecycle Retrieval Hardening

```text
question
-> deterministic community alias expansion
-> ChromaDB candidate retrieval
-> lifecycle-aware filtering
-> metadata-aware reranking
-> grounded answer with active/pending awareness
```

Lifecycle priority is:

```text
active
pending
review / needs_review
superseded
archived
```

Active managed post orders dominate normal retrieval. Pending rules do not override active operational rules; they are advisory context and should trigger a warning when relevant. Superseded and archived rules are not allowed to outrank active rules.

Post-order documents with `lifecycle_generation: managed` are the operational retrieval source of truth. Legacy freeform post-order documents are skipped by default during query and answer retrieval, but remain in the vault for history.

Community aliases are configured in `rag/config/community_aliases.json`. Letter prefixes such as `CBK`, `SR`, `MON`, and `OPB` expand to deterministic community names before semantic retrieval. Numeric client-code portions are ignored.

### Phase 4C2 Legacy Post Order Migration

```text
legacy post_order Markdown
-> deterministic migration parser
-> managed active post_order copy
-> original legacy file preserved
-> migration report
-> ChromaDB rebuild
```

Phase 4C2 converts eligible older post-order notes into lifecycle-managed post-order documents. It does not migrate QA rules into post orders, does not delete legacy files, and does not use AI or semantic diffing.

Generated managed migration documents include `source_legacy_file`, `source_migration: legacy_post_order`, `migration_date`, `rule_id`, and `rule_hash`. These managed documents become the operational retrieval source of truth while the old files remain historical source material.

### Phase 4C3 Announcement Lifecycle Ingestion

```text
clean pasted announcement text
-> deterministic announcement parser
-> managed announcement Markdown
-> announcement refresh report
-> ChromaDB rebuild
```

Announcements are the middle authority layer:

```text
post_order
announcement
primary_workflow
```

Announcements can provide reminders, temporary protocols, event notices, gate issues, NVR issues, approved vendor notes, and operational warnings. They do not override active post orders. Active announcements can answer relevant questions, pending announcements are advisory, and expired or archived announcements are penalized or skipped by normal retrieval.

Phase 4C3 expects cleaned pasted text only. OCR and screenshot parsing are deferred to a later phase.

### Phase 4D Operational Query Intent Parsing

```text
question
-> deterministic QueryIntent parser
-> community alias and known community matching
-> operational topic detection
-> expected document type hints
-> ChromaDB retrieval and authority/lifecycle reranking
```

Phase 4D prevents operational proper nouns from being treated as missing communities. For example, `Red Zone Protocol`, `Support Room`, `Community Approved List`, `Physical ID`, `Pickleball Tournament`, and `Emergency Code` are parsed as topics, protocols, or policies before semantic retrieval.

Community extraction is intentionally strict. A phrase is treated as a community only when it matches a configured alias, a known community name, or a narrow unknown-community pattern such as `policy for Atlantis Bay`. This keeps unknown-community refusals conservative without blocking global announcement topics.

The query parser is deterministic and does not use an LLM. It does not replace authority scoring, lifecycle scoring, primary workflow fallback, or insufficient-context refusal checks.

### Phase 4G Temporal Expiry / Activation Engine

```text
vault Markdown
-> frontmatter lifecycle/date parsing
-> deterministic temporal state
-> ChromaDB metadata
-> authority + lifecycle + temporal reranking
-> grounded answer warnings/refusal
```

Phase 4G adds deterministic temporal interpretation without mutating source memory. It reads lifecycle and date metadata such as `status`, `lifecycle_status`, `effective_date`, `active_from`, `start_date`, `expires_at`, `expiry_date`, `active_until`, `end_date`, `expires_on`, `superseded_by`, and authority/document type fields.

Temporal states are:

```text
active
pending
not_yet_active
expired
superseded
archived
review
unknown
```

Retrieval still follows the authority hierarchy:

```text
post_order
announcement
primary_workflow
```

Temporal scoring is layered on top of existing community, topic, authority, lifecycle generation, and static status scoring. It strongly prefers currently active records, downgrades pending and not-yet-active records, downgrades expired records, and keeps superseded, archived, review, and unknown-temporal records below active operational memory. If only non-current temporal sources are retrieved, the answer path is conservative and may refuse.

The temporal report utility writes review reports under `vault/08_Reports/temporal-lifecycle/`. These reports are derived review artifacts only. They do not update ChromaDB, run ingestion scripts, rewrite source Markdown, or create operational truth.

### Phase 4G1 Announcement Retrieval Precision Hardening

```text
query
-> deterministic parser
-> community/topic extraction
-> vector retrieval
-> deterministic reranking
   -> authority
   -> lifecycle
   -> temporal state
   -> title/topic/category overlap
   -> section weighting
-> grounded answer or safe refusal
```

Phase 4G1 adds a deterministic precision layer for operational announcements. It was added after the Red Zone Protocol reminder query showed that correct parser intent and safe refusal were not enough when nearby reminders shared dense operational language.

The reranking layer supplements embeddings; it does not replace them. It uses exact topic phrase matches, normalized title overlap, keyword overlap, category match, direct answer section weighting, existing authority hierarchy, lifecycle status, and temporal state. `Announcement` sections are preferred for announcement questions. Metadata-heavy sections such as `Operational Notes`, `Source`, and migration notes are penalized for direct operational questions but remain available for traceability/debugging.

Announcement chunks preserve title, category, and normalized announcement topic text in indexed metadata so exact operational topics such as `Red Zone Protocol`, `Pickleball Tournament`, `NVR`, and `Support Room` can be ranked deterministically without LLM reranking or semantic rewriting.

Phase 4G1 does not lower refusal thresholds globally, create fallback answers, rewrite vault documents, update ChromaDB automatically, or allow announcements to override post orders.

### Phase 4E OCR Intake Layer

```text
image screenshot
-> local OCR extraction
-> raw OCR text
-> review Markdown artifact
-> human review/edit
-> existing deterministic ingestion pipeline
-> vault Markdown
-> ChromaDB rebuild
```

Phase 4E is intake-only. It helps convert reminder screenshots, Discord screenshots, post-order screenshots, and operational dashboard screenshots into reviewable text.

OCR output is not operational memory. It must not write directly to `vault/`, call post-order or announcement refresh scripts, update lifecycle state, or rebuild ChromaDB. Human review is required before any extracted text enters the existing ingestion pipeline.

The validated OCR backend is local pytesseract. PaddleOCR is deferred as experimental because it did not pass Windows/Paddle runtime validation. The OCR layer does not use cloud OCR, OpenAI OCR, or LLM cleanup.

### Phase 4F OCR Review + Ingestion Bridge

```text
image screenshot
-> local OCR extraction
-> raw OCR text
-> review Markdown artifact
-> human review/edit
-> approved review bridge
-> reviewed OCR staging input
-> user manually runs existing ingestion script
-> vault Markdown
-> user manually rebuilds ChromaDB
```

Phase 4F adds queue folders under `automation/ocr/review_queue/` and a deterministic bridge that writes only to `automation/ingestion/reviewed_ocr_inputs/`.

The bridge requires explicit review metadata: `review_status: approved`, `approved_for_ingestion: true`, and `target_ingestion_type: announcement` or `post_order`. It preserves reviewed text as-is. It does not write to `vault/`, call ingestion scripts, update ChromaDB, infer policy, rewrite OCR text, or bypass human review.

## Phase 3A Retrieval Flow

Markdown files in `vault/`
-> deterministic section chunking
-> local sentence-transformers embeddings
-> local ChromaDB collection `safepassage_vault_chunks`
-> retrieval-only CLI query results

Phase 3A did not generate answers. It validated retrieval quality before Phase 3B added grounded answer generation.

## Phase 3B Answer Flow

User question
-> local sentence-transformers query embedding
-> ChromaDB retrieves top vault chunks
-> compact context packet is built
-> DeepSeek generates a grounded answer from retrieved context only
-> answer cites source file and section

If retrieved context is insufficient, the answer must say the vault does not contain enough information to answer safely.

## Historical Phase 1 Data Flow

```text
User input
-> n8n webhook
-> DeepSeek classification/normalization
-> Markdown file created in vault
-> Git commit
-> Optional DOCX export later
```
