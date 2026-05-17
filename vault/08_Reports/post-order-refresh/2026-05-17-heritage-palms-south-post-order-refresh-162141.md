# Post Order Refresh Report

- Community: Heritage Palms South
- Community Code: HPS
- Batch Date: 2026-05-17
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_HPS_20260517122141.md
- Mode: write

## Added Rules

- `heritage-palms-south-k-only-contact-resident-twice-confirm-visitor-c726e0cccd` (k) Only contact the resident twice to confirm visitor access. -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-only-contact-resident-twice-confirm-visitor-c726e0cccd.md`
- `heritage-palms-south-c-emergency-code-as-april-09-2026-6434143dca` (c) Emergency Code as of April 09, 2026 - 9141* -> `vault/03_Post_Orders/heritage-palms-south-post-order-c-emergency-code-as-april-09-2026-6434143dca.md`

## Unchanged / Duplicate Rules

- none

## Superseded Rules

- none

## Possible Conflicts

- none

## Possible Changes / Review

- none

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
