# Post Order Refresh Report

- Community: The Glen (Tamiment)
- Community Code: GLEN
- Batch Date: 2026-05-17
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_GLEN_20260517122527.md
- Mode: write

## Added Rules

- `the-glen-tamiment-k-we-only-contact-resident-twice-confirm-597f569130` (k) We only contact the resident TWICE to confirm visitor access. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-k-we-only-contact-resident-twice-confirm-597f569130.md`
- `the-glen-tamiment-kc-res-confirmation-add-alert-res-confirmation-8d70014abf` (kc) Res confirmation, add alert: Res confirmation pending XX/XX/XX for Name | alert effective for 7 days - can add guest during this time | For denials: Residency denied for Name on XX/XX/XX | Deny after 7 days or if HOA disapproves. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-kc-res-confirmation-add-alert-res-confirmation-8d70014abf.md`
- `the-glen-tamiment-c-emergency-code-as-february-5-2026-dc86f1f7a2` (c) Emergency Code as of February 5, 2026 - 3152* -> `vault/03_Post_Orders/the-glen-tamiment-post-order-c-emergency-code-as-february-5-2026-dc86f1f7a2.md`
- `the-glen-tamiment-k-all-medical-service-providers-be-granted-301d1e5479` (k) All medical service providers must be granted entry. This includes nurses, hospice workers, caregivers, therapists, and medical delivery personnel. Log the entry under Medical Services on the Community Approved List. ID NOT REQUIRED. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-k-all-medical-service-providers-be-granted-301d1e5479.md`
- `the-glen-tamiment-kc-visitor-not-speaking-english-spanish-taking-3aff5de775` (kc) For visitor not speaking English or Spanish or taking longer than 90 seconds to respond, allow a one-time entry and log them at Community Approved List on the No English tile. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-kc-visitor-not-speaking-english-spanish-taking-3aff5de775.md`
- `the-glen-tamiment-k-physical-id-passport-id-required-guest-a5af3c9511` (k) A physical ID or passport (ID) is required. If the guest does not have an ID or has a digital ID, please deny entry. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-k-physical-id-passport-id-required-guest-a5af3c9511.md`
- `the-glen-tamiment-c-emergency-code-as-april-3-2026-cc365a689a` (c) Emergency Code as of April 3, 2026 - 3153* (Pending) -> `vault/03_Post_Orders/the-glen-tamiment-post-order-c-emergency-code-as-april-3-2026-cc365a689a.md`
- `the-glen-tamiment-k-anyone-attending-open-house-allowed-should-37756eaf4d` (k) Anyone attending an Open house are allowed in and should be logged under Open house Event tile on the pre-approved list. -> `vault/03_Post_Orders/the-glen-tamiment-post-order-k-anyone-attending-open-house-allowed-should-37756eaf4d.md`
- `the-glen-tamiment-c-emergency-code-as-april-3-2026-20f7182613` (c) Emergency Code as of April 3, 2026 - 3153* -> `vault/03_Post_Orders/the-glen-tamiment-post-order-c-emergency-code-as-april-3-2026-20f7182613.md`
- `the-glen-tamiment-c-emergency-code-as-may-12-2026-123d298d77` (c) Emergency Code as of May 12, 2026 - 3154* (Pending) -> `vault/03_Post_Orders/the-glen-tamiment-post-order-c-emergency-code-as-may-12-2026-123d298d77.md`

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
