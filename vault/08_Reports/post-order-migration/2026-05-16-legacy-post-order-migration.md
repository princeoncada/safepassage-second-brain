# Legacy Post Order Migration Report

- Migration Date: 2026-05-16
- Mode: initial managed conversion
- Scanned Post Order Files: 3 Sierra Ridge legacy files targeted
- Converted Files: 2
- Duplicate Managed Rules: 1
- Skipped / Needs Review: 0
- Old legacy files were preserved.

## Converted

- `vault/03_Post_Orders/2026-05-15-sierra-ridge-for-sierra-ridge-all-overnight-visitors-must-present-physical-id-post-order.md` -> `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-all-overnight-visitors-present-b89b46db47.md`
- `vault/03_Post_Orders/2026-05-15-sierra-ridge-for-sierra-ridge-visitors-must-present-physical-id-before-access-post-order.md` -> `vault/03_Post_Orders/sierra-ridge-managed-post-order-k-sierra-ridge-visitors-present-physical-id-32e4f9f24f.md`

## Duplicate Managed Rules

- `vault/03_Post_Orders/2026-05-15-sierra-ridge-for-sierra-ridge-all-overnight-visitors-must-present-physical-id-post-order-095244.md` skipped: same normalized rule as the converted overnight visitor physical ID post order

## Skipped / Needs Review

- none

## Reminder

- Rebuild ChromaDB after accepting migration output.
- Confirm migrated managed rules before operational reliance.
