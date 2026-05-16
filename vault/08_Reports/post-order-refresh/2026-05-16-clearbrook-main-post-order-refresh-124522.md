# Post Order Refresh Report

- Community: Clearbrook Main
- Community Code: CBK
- Batch Date: 2026-05-16
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/sample_post_order_batch.md
- Mode: write

## Added Rules

- none

## Unchanged / Duplicate Rules

- `clearbrook-main-k-marked-vehicles-ask-address-res-name-29df53bffd` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-marked-vehicles-ask-address-res-name-29df53bffd.md`
- `clearbrook-main-k-visitors-vendors-unmarked-vehicles-ask-address-38e406cbf3` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-visitors-vendors-unmarked-vehicles-ask-address-38e406cbf3.md`
- `clearbrook-main-k-you-see-three-cars-stop-processing-a4df4b987c` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-you-see-three-cars-stop-processing-a4df4b987c.md`
- `clearbrook-main-k-bridge-players-be-logged-at-cca-001b952b98` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-bridge-players-be-logged-at-cca-001b952b98.md`
- `clearbrook-main-kc-community-events-add-event-cca-master-10913a6306` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-kc-community-events-add-event-cca-master-10913a6306.md`
- `clearbrook-main-k-all-golfers-between-7-30-am-aa520b8d0d` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-all-golfers-between-7-30-am-aa520b8d0d.md`
- `clearbrook-main-k-residency-confirmation-pending-entry-permitted-o-06b8d7315c` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-residency-confirmation-pending-entry-permitted-o-06b8d7315c.md`
- `clearbrook-main-k-physical-id-only-required-residents-alternativel-2edbb358fd` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-physical-id-only-required-residents-alternativel-2edbb358fd.md`
- `clearbrook-main-kc-immediately-allow-community-approved-vendors-no-d5cb5e7369` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-kc-immediately-allow-community-approved-vendors-no-d5cb5e7369.md`
- `clearbrook-main-kc-open-houses-estate-sales-not-permitted-4d109b3cca` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-kc-open-houses-estate-sales-not-permitted-4d109b3cca.md`
- `clearbrook-main-k-visitors-vendors-who-do-not-speak-4bed833e5a` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-k-visitors-vendors-who-do-not-speak-4bed833e5a.md`
- `clearbrook-main-kc-non-listed-caller-says-they-executor-59048dcdb8` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-kc-non-listed-caller-says-they-executor-59048dcdb8.md`
- `clearbrook-main-c-emergency-code-as-april-3-2026-3db4cf6686` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-c-emergency-code-as-april-3-2026-3db4cf6686.md`
- `clearbrook-main-c-emergency-code-as-may-12-2026-467eeb2c85` duplicates `vault/03_Post_Orders/clearbrook-main-post-order-c-emergency-code-as-may-12-2026-467eeb2c85.md`

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
