# Post Order Refresh Expected Results

## Dry Run

Command:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md --dry-run
```

Expected:

- parses community `Clearbrook Main`;
- parses community code `CBK`;
- parses batch date `2026-05-16`;
- parses `update_type: partial`;
- parses `supersede_mode: conservative`;
- parses fourteen rules, including `Post Order`, `POST ORDER`, `POST ORDERS`, `K&C`, `K & C`, and `K and C` variants;
- maps `C` to concierge, not call center;
- prints added, duplicate, superseded, conflict, possible changes/review, and missing sections;
- skips missing-rule replacement handling because the batch is partial;
- writes no vault files.

## First Real Run

Command:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Expected:

- creates active post order Markdown for new rules or reports duplicates when matching active hashes already exist;
- writes possible near-topic changes as `status: review` instead of superseding unless the topic match is clear;
- writes a report under `vault/08_Reports/post-order-refresh/`;
- does not delete old rules.

## Second Real Run

Command:

```powershell
python automation/ingestion/refresh_post_orders.py --input automation/ingestion/sample_post_order_batch.md
```

Expected:

- does not create duplicate active rules;
- reports unchanged/duplicate rules.

## Retrieval

After reindexing:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

Expected:

- active post orders are indexed;
- lifecycle metadata does not break indexing;
- superseded/conflict/review items are penalized if indexed.
