---
title: "The Glen Tamiment QA Tip - Registered Tag Access Full Name Only"
type: qa_rule
authority_level: qa_rule
community: The Glen (Tamiment)
community_code: GLEN
scope:
  - kiosk
scope_key: k
status: active
lifecycle_generation: managed
rule_id: the-glen-tamiment-qa-tip-k-registered-tag-access-fullname-only
tags:
  - qa_rule
  - the-glen-tamiment
  - glen
  - scope-k
  - registered-tag
  - access-tip
source: QA Team Advisory
effective_date: "2026-05-19"
last_updated: "2026-05-19"
---

# The Glen Tamiment QA Tip — Registered Tag Access Full Name Only

## QA Tip

At The Glen, if a vehicle's license plate or RFID tag is already registered in the system under the driver's name but the driver is unable to auto-enter through the gate, access can be granted using only the driver's full name. Physical ID verification is not required in this specific case.

This aligns with the global kiosk basics registered-tag exception. At GLEN, use this tip to avoid unnecessary ID denial denials for drivers with known registered tags who arrive at the kiosk.

## Scope

- Marker: K (Kiosk only)

## When This Applies

- Vehicle's tag or license plate is confirmed registered in the system
- Driver is at the kiosk and cannot auto-enter through the gate
- Physical ID is not available or not presented

## Advisory Note

This is a QA team advisory tip. It is not verified against the formal GLEN post orders. If a formal post order for GLEN is updated to explicitly address registered-tag access, defer to the post order over this tip.

## Source

- Source: QA Team Advisory (unverified against formal post orders)
