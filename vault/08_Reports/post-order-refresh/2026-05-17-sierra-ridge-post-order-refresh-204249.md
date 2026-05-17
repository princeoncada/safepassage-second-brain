# Post Order Refresh Report

- Community: Sierra Ridge
- Community Code: SR
- Batch Date: 2026-05-17
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_SR_20260517164210.md
- Mode: write

## Added Rules

- `sierra-ridge-k-contact-resident-twice-access-there-s-70f53c8e61` (k) Contact the resident twice for access. If there's no response, deny entry. -> `vault/03_Post_Orders/sierra-ridge-post-order-k-contact-resident-twice-access-there-s-70f53c8e61.md`
- `sierra-ridge-c-following-features-have-been-disabled-mobile-024453a894` (c) The following features have been disabled in the mobile app by the HOA: adding a visitor, adding a tag, and one-time entry. Please do not ask visitors for a code. -> `vault/03_Post_Orders/sierra-ridge-post-order-c-following-features-have-been-disabled-mobile-024453a894.md`
- `sierra-ridge-k-barrier-arm-has-5-second-delay-995446b44d` (k) Barrier arm has a 5 second delay after pressing open gate. LPR on the visitor's lane is disabled. -> `vault/03_Post_Orders/sierra-ridge-post-order-k-barrier-arm-has-5-second-delay-995446b44d.md`
- `sierra-ridge-kc-dont-add-tags-vis-res-it-8359e52b0e` (kc) Dont add tags for vis. For res, it needs to be approved by property management. If approved, add vis tile for plate with access limits. For denied, add alert to the account: Denied Tag number: [TAG#] - [Res Name]. -> `vault/03_Post_Orders/sierra-ridge-post-order-kc-dont-add-tags-vis-res-it-8359e52b0e.md`
- `sierra-ridge-kc-visitor-not-speaking-english-spanish-taking-75418a0f64` (kc) For visitor not speaking English or Spanish or taking longer than 90 seconds to respond, proceed to deny the entry. -> `vault/03_Post_Orders/sierra-ridge-post-order-kc-visitor-not-speaking-english-spanish-taking-75418a0f64.md`
- `sierra-ridge-c-emergency-code-as-april-3-2026-6d3afb83e9` (c) Emergency Code as of April 3, 2026 - 0714* (Pending) -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-april-3-2026-6d3afb83e9.md`
- `sierra-ridge-k-physical-id-required-at-all-times-83654ab9db` (k) A physical ID is required at all times, except for marked pre-approved vendors. Residents are not permitted to use security questions must present a valid physical ID. -> `vault/03_Post_Orders/sierra-ridge-post-order-k-physical-id-required-at-all-times-83654ab9db.md`
- `sierra-ridge-kc-individuals-pending-residency-confirmation-one-t-d6767ab17c` (kc) For individuals with pending residency confirmation, one-time entries and requests for guest access are not permitted. If the individual does not have access, call the listed resident for approval. -> `vault/03_Post_Orders/sierra-ridge-post-order-kc-individuals-pending-residency-confirmation-one-t-d6767ab17c.md`
- `sierra-ridge-kc-res-hosting-events-contact-prop-mngt-4f7cd7cda0` (kc) Res hosting events must contact Prop Mngt two days in advance & provide list of guest. Prop Mngt is required to submit list Safe Passage. If a guest is not listed, the res must be contacted for each guest. -> `vault/03_Post_Orders/sierra-ridge-post-order-kc-res-hosting-events-contact-prop-mngt-4f7cd7cda0.md`
- `sierra-ridge-kc-visitors-vendors-allowed-1-hour-max-e37dcf9664` (kc) Visitors & Vendors allowed 1 hour max of access. -> `vault/03_Post_Orders/sierra-ridge-post-order-kc-visitors-vendors-allowed-1-hour-max-e37dcf9664.md`
- `sierra-ridge-c-emergency-code-as-april-3-2026-efb8cf3049` (c) Emergency Code as of April 3, 2026 - 0714* -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-april-3-2026-efb8cf3049.md`
- `sierra-ridge-c-emergency-code-as-may-12-2026-9a15edf576` (c) Emergency Code as of May 12, 2026 - 0715* (Pending) -> `vault/03_Post_Orders/sierra-ridge-post-order-c-emergency-code-as-may-12-2026-9a15edf576.md`

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
