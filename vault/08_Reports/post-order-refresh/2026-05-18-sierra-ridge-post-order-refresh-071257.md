# Post Order Refresh Report

- Community: Sierra Ridge
- Community Code: SR
- Batch Date: 2026-05-18
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_SR_20260518031247.md
- Mode: write

## Added Rules

- `sierra-ridge-c-emergency-code-as-may-12-2026-9a15edf576` (c) Emergency Code as of May 12, 2026 - 0715* (Pending) -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-may-12-2026-9a15edf576.md`
- `sierra-ridge-c-emergency-code-as-april-3-2026-efb8cf3049` (c) Emergency Code as of April 3, 2026 - 0714* -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-april-3-2026-efb8cf3049.md`
- `sierra-ridge-c-emergency-code-as-april-3-2026-6d3afb83e9` (c) Emergency Code as of April 3, 2026 - 0714* (Pending) -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-april-3-2026-6d3afb83e9.md`

## Unchanged / Duplicate Rules

- `sierra-ridge-kc-visitors-vendors-allowed-1-hour-max-e37dcf9664` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-kc-visitors-vendors-allowed-1-hour-max-e37dcf9664.md`
- `sierra-ridge-kc-res-hosting-events-contact-prop-mngt-4f7cd7cda0` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-kc-res-hosting-events-contact-prop-mngt-4f7cd7cda0.md`
- `sierra-ridge-kc-individuals-pending-residency-confirmation-one-t-d6767ab17c` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-kc-individuals-pending-residency-confirmation-one-t-d6767ab17c.md`
- `sierra-ridge-k-physical-id-required-at-all-times-83654ab9db` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-k-physical-id-required-at-all-times-83654ab9db.md`
- `sierra-ridge-kc-visitor-not-speaking-english-spanish-taking-75418a0f64` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-kc-visitor-not-speaking-english-spanish-taking-75418a0f64.md`
- `sierra-ridge-kc-dont-add-tags-vis-res-it-8359e52b0e` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-kc-dont-add-tags-vis-res-it-8359e52b0e.md`
- `sierra-ridge-k-barrier-arm-has-5-second-delay-995446b44d` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-k-barrier-arm-has-5-second-delay-995446b44d.md`
- `sierra-ridge-c-following-features-have-been-disabled-mobile-024453a894` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-c-following-features-have-been-disabled-mobile-024453a894.md`
- `sierra-ridge-k-contact-resident-twice-access-there-s-70f53c8e61` duplicates `vault/03_Post_Orders/sierra-ridge-post-order-k-contact-resident-twice-access-there-s-70f53c8e61.md`

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
