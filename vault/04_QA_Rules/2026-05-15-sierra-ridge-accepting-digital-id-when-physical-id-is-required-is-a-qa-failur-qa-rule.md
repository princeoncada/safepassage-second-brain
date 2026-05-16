---
title: "Accepting Digital Id When Physical Id Is Required Is A Qa Failure"
type: "qa_rule"
community: "Sierra Ridge"
priority: "high"
effective_date: "2026-05-15"
source: "manual_test"
status: "needs_review"
tags: ["qa_rule", "sierra-ridge", "phase-2-minimal-pow"]
last_updated: "2026-05-15T09:53:17.154Z"
version: "1.0"
human_review_required: true
---

# Accepting Digital Id When Physical Id Is Required Is A Qa Failure

## Summary

Accepting digital ID when physical ID is required is a QA failure.

## Details

This rule ensures that when a process explicitly requires a physical form of identification, presenting a digital version (e.g., a photo or scanned copy on a device) does not satisfy the requirement. The failure occurs because digital IDs may lack the security features, verification mechanisms, or legal acceptance of physical IDs, potentially compromising identity verification integrity.

## Agent Action

Reject digital ID and request physical ID. If user cannot provide physical ID, escalate to supervisor or follow alternative verification procedures as defined by policy.

## QA Notes

Verify that the agent did not accept a digital ID when physical ID was required. Check if the agent offered alternatives or escalated appropriately. Ensure the agent documented the reason for rejection.

## Open Questions

- What specific security features distinguish physical IDs from digital versions in this context?
- Are there any exceptions where digital ID is acceptable (e.g., government-issued digital ID apps)?
- What is the escalation path if the user cannot provide physical ID?

## Source Input

Accepting digital ID when physical ID is required is a QA failure.

## Change History

- 2026-05-15: Created by Phase 2 Minimal POW ingestion workflow.
