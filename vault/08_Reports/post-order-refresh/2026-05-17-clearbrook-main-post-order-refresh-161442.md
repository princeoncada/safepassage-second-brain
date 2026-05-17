# Post Order Refresh Report

- Community: Clearbrook Main
- Community Code: CBK
- Batch Date: 2026-05-17
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_CBK_20260517121441.md
- Mode: write

## Added Rules

- `clearbrook-main-c-emergency-code-as-april-09-2026-6434143dca` (c) Emergency Code as of April 09, 2026 - 9141* -> `vault/03_Post_Orders/clearbrook-main-post-order-c-emergency-code-as-april-09-2026-6434143dca.md`

## Unchanged / Duplicate Rules

- none

## Superseded Rules

- none

## Possible Conflicts

- none

## Possible Changes / Review

- `clearbrook-main-k-only-contact-resident-twice-4b9dfa5ba5` may relate to `clearbrook-main-k-only-contact-resident-twice-confirm-visitor-c726e0cccd`; written as review -> `vault/03_Post_Orders/clearbrook-main-post-order-review-k-only-contact-resident-twice-4b9dfa5ba5.md`

## Missing From Latest Batch

- skipped because update_type is partial

## Manual Review Required

- Review possible conflicts before relying on them operationally.
- Review missing active rules before marking anything inactive.
- Rebuild ChromaDB after accepting a refresh:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```
