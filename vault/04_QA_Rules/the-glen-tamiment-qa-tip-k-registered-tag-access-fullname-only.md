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

At The Glen, if a visitor is already confirmed in SP Guard with active
access but is unable to auto-enter and ends up at the kiosk, access can
be granted using only the visitor's full name. Physical ID verification
is not required — the visitor's identity was already confirmed when
access was originally granted.

Use this tip to avoid unnecessary ID denial for visitors who are already
in the system with confirmed access.

## Scope

- Marker: K (Kiosk only)

## When This Applies

- Visitor is already confirmed in SP Guard with active access
- Visitor is at the kiosk and cannot auto-enter through the gate
- Physical ID is not available or not presented

## Advisory Note

This is a QA team advisory tip. It is not verified against the formal GLEN post orders. If a formal post order for GLEN is updated to explicitly address registered-tag access, defer to the post order over this tip.

## Source

- Source: QA Team Advisory (unverified against formal post orders)
