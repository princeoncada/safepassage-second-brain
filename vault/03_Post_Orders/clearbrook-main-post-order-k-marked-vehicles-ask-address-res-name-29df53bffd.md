---
title: Clearbrook Main Post Order - Marked Vehicles Ask Address Res Name
type: post_order
authority_level: post_order
community: Clearbrook Main
community_code: CBK
scope:
- kiosk
scope_key: k
status: active
lifecycle_generation: managed
rule_id: clearbrook-main-k-marked-vehicles-ask-address-res-name-29df53bffd
rule_hash: 29df53bffda353509de1dfbd2891aba32c732ac3d5362e99162a07ee80b65d3d
topic_key: marked-vehicles-ask-address-res-name
source_batch: automation/ingestion/sample_post_order_batch.md
batch_date: '2026-05-16'
update_type: partial
supersede_mode: conservative
effective_date: '2026-05-16'
supersedes: ''
superseded_by: ''
created_at: '2026-05-16T12:43:56+00:00'
last_updated: '2026-05-16T12:43:56+00:00'
tags:
- post_order
- clearbrook-main
- cbk
- scope-k
- phase-4c
normalized_rule: for marked vehicles, ask address, res name & see if the vendor is
  listed on the res address, if not found or no address is provided log on community
  approved list under "marked vendor vehicles." include the vendor name and plate.
---

# Clearbrook Main Post Order - Marked Vehicles Ask Address Res Name

## Rule

For marked vehicles, ask address, res name & see if the vendor is listed on the res address, if not found or no address is provided log on Community Approved List under "Marked Vendor Vehicles." Include the vendor name and plate.

## Scope

- Marker: K
- kiosk

## Source

- Batch: automation/ingestion/sample_post_order_batch.md
- Batch Date: 2026-05-16

## Change History

- 2026-05-16T12:43:56+00:00: Created by Phase 4C post order refresh.
