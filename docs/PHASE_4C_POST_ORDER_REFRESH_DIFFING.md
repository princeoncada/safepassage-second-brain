# Phase 4C Post Order Refresh Diffing

Phase 4C adds deterministic local batch refresh for post orders.

Post orders are the highest authority operational memory:

```text
post_order
announcement
primary_workflow
```

Higher authority overrides lower authority. Phase 4C does not add agents, n8n changes, Open WebUI logic, or AI-based diffing.

## Input Format

Use a Markdown or TXT batch file:

```text
# Post Order Batch
community: Sierra Ridge
community_code: SR
batch_date: 2026-05-16
update_type: partial
supersede_mode: conservative

POST ORDER (K): Overnight visitors must present physical ID before access.

POST ORDER (K&C): Do not accept digital ID when physical ID is required.

POST ORDER (C): Call resident twice before denying unregistered visitor.
```

Scope markers:

- `K`: kiosk
- `C`: concierge
- `K&C`: kiosk and concierge
- `K & C`: also accepted and normalized to `K&C`
- `K and C`: also accepted and normalized to `K&C`

The sample batch uses `Clearbrook Main` with the letter code `CBK`. Numeric client codes are not required or stored by the refresh script.

`update_type: partial` means the batch is not treated as a full replacement. Existing active rules that are absent from a partial batch are not listed as missing from the latest batch.

`supersede_mode: conservative` means the script only supersedes when community, scope, and deterministic topic key clearly match. Near matches are written as `status: review` and listed under possible changes instead of silently superseding active rules.

Sample:

```text
automation/ingestion/sample_post_order_batch.md
```

## Commands

Dry run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
```

Real run:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Re-run the same batch:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Reindex:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

## Metadata Schema

Generated post order Markdown includes:

- `title`
- `type: post_order`
- `authority_level: post_order`
- `community`
- `community_code`
- `scope`
- `scope_key`
- `status`
- `rule_id`
- `rule_hash`
- `topic_key`
- `source_batch`
- `batch_date`
- `update_type`
- `supersede_mode`
- `effective_date`
- `supersedes`
- `superseded_by`
- `created_at`
- `last_updated`
- `tags`
- `normalized_rule`

## Duplicate Detection

The script normalizes each rule and hashes the normalized text with SHA-256.

If an incoming `rule_hash` already exists on an active rule for the same community and scope, the script does not create a duplicate active rule. The update report lists it as unchanged/duplicate.

## Supersede Handling

In conservative mode, if an incoming rule has the same community, scope, and `topic_key` as an existing active managed rule but a different hash, the script:

- marks the existing rule as `superseded`;
- creates a new `active` rule;
- sets old `superseded_by` to the new `rule_id`;
- sets new `supersedes` to the old `rule_id`;
- preserves the old Markdown file.

If an incoming rule looks related but does not clearly share the same topic key, the script writes it as `status: review` and reports it as a possible change. This avoids destructive mistakes during partial post order refreshes.

## Conflict Handling

Conflict detection is deterministic and conservative. It checks simple known patterns:

- different resident call counts;
- `save tags` vs `do not save tags`;
- physical ID required vs digital ID accepted.

If a conflict is detected, the new rule is written with `status: conflict` and the report lists the warning. The script does not silently choose a winner.

## Missing From Latest Batch

If an active managed rule for the same community and scope is not present in the latest batch, it is listed as missing from latest batch. The script does not delete it or mark it inactive.

For `update_type: partial`, this missing-rule check is skipped because the batch is not intended to replace all community post orders.

## Reports

Real runs write reports to:

```text
vault/08_Reports/post-order-refresh/
```

Reports include:

- community;
- batch date;
- input file;
- added rules;
- unchanged rules;
- superseded rules;
- possible conflicts;
- missing from latest batch;
- manual review reminders;
- ChromaDB rebuild reminder.

## Index Behavior

`rag/scripts/index_vault.py` preserves lifecycle metadata including `community_code`, `rule_id`, `rule_hash`, `source_batch`, `update_type`, `supersede_mode`, `supersedes`, and `superseded_by`.

Generated managed post orders include `lifecycle_generation: managed`. Older freeform post-order documents without rule lifecycle metadata are treated as `lifecycle_generation: legacy` by the indexer.

Retrieval prefers:

- `authority_level: post_order`;
- `status: active`;
- matching community;
- matching scope where query context supports it.

Superseded, conflict, review, and inactive items are still indexable, but they receive retrieval penalties so active rules stay ahead.

Phase 4C1 makes this stricter: legacy post-order documents are skipped by default during retrieval, active managed rules dominate, pending rules are advisory only, and archived rules are skipped by default.

Phase 4C2 adds deterministic legacy post-order migration. Eligible old `type: post_order` files can be copied into managed active post-order documents with lifecycle metadata while preserving the old files. QA rules are not migrated into post orders.

Phase 4C3 extends lifecycle ingestion to announcements and reminders. Announcements are separate `type: announcement` documents under `vault/05_Announcements/`; they are lower authority than post orders and higher authority than primary workflow.

## Validation

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the vehicle policy for Atlantis Bay?" --top-k 5
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected:

- dry run writes no vault files;
- first real run creates or reports active rules;
- second real run reports unchanged/duplicate rules;
- no old rules are deleted;
- active post orders remain highest authority;
- Atlantis Bay still refuses safely;
- primary workflow fallback still answers default questions.
