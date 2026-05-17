# SafePassage Second Brain - Versioning Reference

## Purpose

This file is the authoritative versioning reference for all AI agents and human contributors working on this project. Read this file before making any changes to phase documentation.

## Version Format

PHASE-[MAJOR].[MINOR].[PATCH]-[STATE]

Components:
- MAJOR: increments when a phase adds a new capability layer
- MINOR: increments when a fix or improvement is applied within a phase
- PATCH: increments for targeted bug fixes within a minor version
- STATE: one of alpha, beta, rc, or stable

## State Definitions

alpha
  Implemented but not yet manually tested.
  Do not rely on operationally.
  Codex has finished implementation. User has not yet run validation.

beta
  Partially validated. Known issues remain.
  Use with caution during testing only.
  At least one validation pass completed but failures or gaps exist.

rc (release candidate)
  All known bugs fixed. All validation commands passed.
  Awaiting user commit to master.
  Safe to test operationally but not yet committed.

stable
  Committed to master. Production ready.
  Full validation passed. User has committed. Safe to rely on.

## Promotion Rules

alpha -> beta
  Trigger: first partial validation pass completed
  Action: update STATE from alpha to beta in all four versioning locations
  Note: document which tests passed and which failed

beta -> rc
  Trigger: all known bugs fixed AND all validation commands pass
  Action: update STATE from beta to rc, increment PATCH if bugs were fixed
  Note: document the patch notes and which fixes were applied

rc -> stable
  Trigger: user manually commits to master
  Action: update STATE from rc to stable in all four versioning locations
  Note: add validation record with date and summary

stable -> patch (regression)
  Trigger: new bug found in a stable phase
  Action: create new PATCH version (e.g. 4.8.1-stable -> 4.8.2-beta)
  Note: document the regression, root cause, and fix

## Four Versioning Locations

Every version change must be applied consistently across all four locations. Partial updates are not acceptable.

1. docs/VERSIONING.md (this file)
   - Current version table at the top
   - Complete version history table

2. docs/AI_HANDOFF.md
   - ## Current Version line at the very top
   - Current Phase line with version tag
   - Inline version tags in the full phase history list

3. docs/PHASE_LOG.md
   - Version History table at the very top of the file
   - Version tag in each phase section heading
   - Patch notes section within each phase entry
   - Validation record section within each validated phase entry

4. README.md
   - Version Status table near the top

## Current Version

| Field | Value |
| --- | --- |
| Version | 4.8.2-stable |
| Phase | Phase 4I-lite |
| State | stable |
| Date | 2026-05-17 |
| Commit | master |
| Summary | DATE_PATTERN word boundary fix - VALIDATED |

## Complete Version History

| Version | Phase | State | Date | Summary |
| --- | --- | --- | --- | --- |
| 4.8.2-stable | Phase 4I-lite | stable | 2026-05-17 | DATE_PATTERN word boundary fix - VALIDATED |
| 4.8.1-stable | Phase 4I-lite | stable | 2026-05-17 | top_k fix + name match - VALIDATED |
| 4.8.1-rc | Phase 4I-lite | rc | 2026-05-17 | top_k fix + name match fix |
| 4.8.0-beta | Phase 4I-lite | beta | 2026-05-17 | slash commands, scope rerank partial |
| 4.7.0-stable | Phase UX-1 | stable | 2026-05-17 | dashboard + alias expansion |
| 4.6.0-stable | Phase 4J-lite | stable | 2026-05-17 | operational dashboard |
| 4.5.1-stable | Phase 4G1 | stable | 2026-05-17 | retrieval precision hardening |
| 4.5.0-stable | Phase 4G | stable | 2026-05-17 | temporal lifecycle engine |
| 4.4.1-stable | Phase 4F | stable | 2026-05-17 | OCR review bridge |
| 4.4.0-stable | Phase 4E | stable | 2026-05-17 | OCR intake layer |
| 4.3.0-stable | Phase 4D | stable | 2026-05-17 | query intent parser |
| 4.2.3-stable | Phase 4C3 | stable | 2026-05-17 | announcement ingestion |
| 4.2.2-stable | Phase 4C2 | stable | 2026-05-17 | legacy post order migration |
| 4.2.1-stable | Phase 4C1 | stable | 2026-05-17 | lifecycle retrieval hardening |
| 4.2.0-stable | Phase 4C | stable | 2026-05-17 | batch post order refresh |
| 4.1.1-stable | Phase 4B2 | stable | 2026-05-17 | fallback confidence fix |
| 4.1.0-stable | Phase 4B | stable | 2026-05-17 | primary workflow ingestion |
| 4.0.0-stable | Phase 4A | stable | 2026-05-17 | retrieval quality hardening |
| 3.4.0-stable | Phase 3E | stable | 2026-05-17 | Open WebUI integration |
| 3.3.0-stable | Phase 3D | stable | 2026-05-17 | FastAPI local wrapper |
| 3.2.0-stable | Phase 3C | stable | 2026-05-17 | RAG quality hardening |
| 3.1.0-stable | Phase 3B | stable | 2026-05-17 | grounded answering |
| 3.0.0-stable | Phase 3A | stable | 2026-05-17 | retrieval POW |
| 2.0.0-stable | Phase 2 | stable | 2026-05-17 | minimal POW ingestion |

## Rules for AI Agents

When continuing this project, an AI agent MUST:

0. Read docs/WORKFLOW.md at the start of every session.
   It defines the full phase cycle, Codex prompt standards,
   context window management, and repo awareness rules.
   VERSIONING.md handles what version to assign.
   WORKFLOW.md handles how to work.
1. Read docs/VERSIONING.md first - this file - before touching any documentation.
2. Read docs/AI_HANDOFF.md to understand the current phase and what exists.
3. Read docs/PHASE_LOG.md to understand the full history and what was validated.
4. Never assign a version state higher than what is actually true:
   - Do not mark alpha as rc without a validation pass.
   - Do not mark rc as stable without a user commit.
5. Apply every version change to all four versioning locations simultaneously. Partial updates break consistency for the next agent.
6. When in doubt about the current version, trust docs/VERSIONING.md over any other file - it is the single source of truth.
7. Include a patch note block for every MINOR or PATCH version change.
8. Include a validation record block for every rc -> stable promotion.

## Next Phase

Next version: 4.9.0-alpha
Next phase: Community Onboarding + Scope-Aware Retrieval Improvements
Goal: Ingest post orders for remaining unindexed communities and improve retrieval for "show me all" style queries across all communities.
First task: Ingest post orders for remaining unindexed communities via `/post-orders [ALIAS] [text]` in Open WebUI, then validate `/announcements` YES confirmation flow.
