# Post Order Refresh Report

- Community: Heritage Palms South
- Community Code: HPS
- Batch Date: 2026-05-17
- Update Type: partial
- Supersede Mode: conservative
- Input File: automation/ingestion/temp_HPS_20260517122405.md
- Mode: write

## Added Rules

- `heritage-palms-south-kc-res-confirmation-add-alert-res-confirmation-8d70014abf` (kc) Res confirmation, add alert: Res confirmation pending XX/XX/XX for Name | alert effective for 7 days - can add guest during this time | For denials: Residency denied for Name on XX/XX/XX | Deny after 7 days or if HOA disapproves. -> `vault/03_Post_Orders/heritage-palms-south-post-order-kc-res-confirmation-add-alert-res-confirmation-8d70014abf.md`
- `heritage-palms-south-kc-non-listed-caller-says-they-power-d99350267b` (kc) Non-listed caller says they are the 'Power of Attorney' (POA). We submit a 'POA Confirmation' ticket requesting they be added as a POA Resident. As we await confirmation, the person can add a guest for up to 3 days. -> `vault/03_Post_Orders/heritage-palms-south-post-order-kc-non-listed-caller-says-they-power-d99350267b.md`
- `heritage-palms-south-k-open-house-estate-sales-can-only-48ecd81082` (k) Open house and/or Estate Sales can only happen on Saturday and Sunday between the hours of 8AM to 5PM. -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-open-house-estate-sales-can-only-48ecd81082.md`
- `heritage-palms-south-k-events-code-will-be-provided-event-98a50e4bee` (k) For Events, a code will be provided by the Event Manager Antonia Torres (contact) 760-797-8641, atorres@heritagepalms.org -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-events-code-will-be-provided-event-98a50e4bee.md`
- `heritage-palms-south-kc-remote-gate-access-feature-has-been-c26e87e023` (kc) The remote gate access feature has been approved by Chris Banks. Please process remote gate access requests from residents who wish to use this feature without requesting approval from Chris Banks or Lori Pillatzke. -> `vault/03_Post_Orders/heritage-palms-south-post-order-kc-remote-gate-access-feature-has-been-c26e87e023.md`
- `heritage-palms-south-kc-visitor-not-speaking-english-spanish-taking-75418a0f64` (kc) For visitor not speaking English or Spanish or taking longer than 90 seconds to respond, proceed to deny the entry. -> `vault/03_Post_Orders/heritage-palms-south-post-order-kc-visitor-not-speaking-english-spanish-taking-75418a0f64.md`
- `heritage-palms-south-k-physical-id-passport-id-required-no-2424a58ddf` (k) A physical ID or passport (ID) is required, no digital IDs. If the guest does not have an ID, please contact the resident for approval. If there is no response, proceed with denying entry. -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-physical-id-passport-id-required-no-2424a58ddf.md`
- `heritage-palms-south-kc-after-granting-access-first-responder-call-a0d7284084` (kc) After granting access to a first responder, call Ruby at 760-899-0299 or Joe at 562-230-783. Both are available 24/7. -> `vault/03_Post_Orders/heritage-palms-south-post-order-kc-after-granting-access-first-responder-call-a0d7284084.md`
- `heritage-palms-south-k-realtors-allowed-entry-m-f-deny-3fc5bd84c5` (k) Realtors allowed entry M-F. Deny entry if they can't provide an address, a physical ID & realtor's license. Clients may go in with them. -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-realtors-allowed-entry-m-f-deny-3fc5bd84c5.md`
- `heritage-palms-south-k-outside-work-repair-vendors-such-as-1870e246f2` (k) Outside work or repair vendors, such as roofers, contractors, and maintenance, only allowed M-F 6am-6pm and Sat 9am-3:30pm. No vendors allowed on Sun. Vendors: Plumbing, Utility, Electric, A/C, Special deliveries are allowed anytime. -> `vault/03_Post_Orders/heritage-palms-south-post-order-k-outside-work-repair-vendors-such-as-1870e246f2.md`
- `heritage-palms-south-c-emergency-code-as-may-12-2026-d82786fc5e` (c) Emergency Code as of May 12, 2026 - 9142* (Pending) -> `vault/03_Post_Orders/heritage-palms-south-post-order-c-emergency-code-as-may-12-2026-d82786fc5e.md`

## Unchanged / Duplicate Rules

- `heritage-palms-south-k-only-contact-resident-twice-confirm-visitor-c726e0cccd` duplicates `vault/03_Post_Orders/heritage-palms-south-post-order-k-only-contact-resident-twice-confirm-visitor-c726e0cccd.md`
- `heritage-palms-south-c-emergency-code-as-april-09-2026-6434143dca` duplicates `vault/03_Post_Orders/heritage-palms-south-post-order-c-emergency-code-as-april-09-2026-6434143dca.md`

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
