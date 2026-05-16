---
title: Clearbrook Main Post Order - You See Three Cars Stop Processing
type: post_order
authority_level: post_order
community: Clearbrook Main
community_code: CBK
scope:
- kiosk
scope_key: k
status: active
rule_id: clearbrook-main-k-you-see-three-cars-stop-processing-a4df4b987c
rule_hash: a4df4b987c0d16d371ff96b5927d5c923f4a337f4cb91e66b3276cf6d1055adc
topic_key: you-see-three-cars-stop-processing
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
normalized_rule: when you see three cars, stop processing your current guest and log
  under 3cp (no address) until the line of cars has been cleared. use term "pre-authorized".
---

# Clearbrook Main Post Order - You See Three Cars Stop Processing

## Rule

When you see three cars, stop processing your current guest and log under 3CP (No Address) until the line of cars has been cleared. Use term "pre-authorized".

## Scope

- Marker: K
- kiosk

## Source

- Batch: automation/ingestion/sample_post_order_batch.md
- Batch Date: 2026-05-16

## Change History

- 2026-05-16T12:43:56+00:00: Created by Phase 4C post order refresh.
