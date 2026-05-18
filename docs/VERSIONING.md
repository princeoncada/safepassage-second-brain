# SafePassage Second Brain - Versioning Reference

## Purpose

This file is the authoritative versioning reference for all AI agents and human contributors working on this project. Read this file before making any changes to phase documentation.

## Version Format

Versions follow X.Y.Z semantic versioning:

**Z — Patch** (increment Z)
A targeted fix to existing behavior. No new capability added.
Use when: fixing a bug in one function, correcting config data, fixing a regex,
updating a single-file logic error, retiring a doc convention.
Examples: scope filter regex fix, alias token cap fix, source dedup fix,
doc convention update (like this one).

**Y — Minor** (increment Y, reset Z to 0)
A new feature or capability added to the system. Meaningful behavior change
that operators or agents would notice.
Use when: new API field, new retrieval behavior, new slash command, new
workflow phase that adds a capability, new ingestion feature.
Examples: conversation history (4.10.0), scope-aware retrieval (4.9.0),
ambiguity clarification (part of 4.9.x).

**X — Major** (increment X, reset Y and Z to 0)
Architectural shift or production milestone.
Use when: new ingestion pipeline, new data model, v2 of the system,
production deployment, breaking API change.
Examples: (none yet - system is pre-1.0)

**Decision table — which number to increment:**
| Change type                              | Bump |
|------------------------------------------|------|
| Bug fix, single function or file         | Z    |
| Config data fix (aliases, rules)         | Z    |
| Doc convention or workflow fix           | Z    |
| New API field or schema addition         | Y    |
| New retrieval behavior or capability     | Y    |
| New slash command or ingestion feature   | Y    |
| New phase that adds operator capability  | Y    |
| Architectural redesign or v2             | X    |
| Production deployment milestone          | X    |

**Historical note:**
Versions 4.9.0 through 4.12.0 used inflated Y numbers for what should have
been Z patches. This history is preserved as-is. The correct convention
applies from 4.12.1 onward.

## State Definitions

alpha
  Implemented but not yet manually tested.
  Do not rely on operationally.
  Codex has finished implementation. User has not yet run validation.

beta
  Partially validated. Known issues remain.
  Use with caution during testing only.
  At least one validation pass completed but failures or gaps exist.

rc (retired)
  Previously used as a release candidate state between beta and stable.
  No longer used in the active phase cycle as of Phase 4.11.0.
  Existing rc entries in the version history table are preserved for reference.

stable
  Committed to master. Production ready.
  Full validation passed. User has committed. Safe to rely on.

## Promotion Rules

alpha -> beta
  Trigger: first partial validation pass completed
  Action: update STATE from alpha to beta in all four versioning locations
  Note: document which tests passed and which failed

alpha -> stable (or beta -> stable)
  Trigger: all known bugs fixed AND all validation commands pass AND user commits to master
  Action: update STATE from alpha (or beta) to stable in all four versioning locations
  Note: document the validation record and which checks passed

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
| Version | 4.14.0-stable |
| Phase | Phase 4.14.0 |
| State | stable |
| Date | 2026-05-18 |
| Commit | master |
| Summary | incremental indexing with --files flag - VALIDATED |

## Complete Version History

| Version | Phase | State | Date | Summary |
| --- | --- | --- | --- | --- |
| 4.14.0-stable | Phase 4.14.0 | stable | 2026-05-18 | incremental indexing with --files flag - VALIDATED |
| 4.13.4-stable | Patch | stable | 2026-05-18 | fix double sources display in CLI output - VALIDATED |
| 4.13.3-stable | Patch | stable | 2026-05-18 | emergency code vault fix + ingestion/indexing/dedup fixes - VALIDATED |
| 4.13.2-stable | Patch | stable | 2026-05-17 | fix pending detection + reverse rule order - VALIDATED |
| 4.13.1-stable | Patch | stable | 2026-05-17 | surface pending rules in scoped listing - VALIDATED |
| 4.13.0-stable | Phase 4.13.0 | stable | 2026-05-17 | archive redundant legacy SR K files - VALIDATED |
| 4.12.1 | Patch | stable | 2026-05-17 | lock X.Y.Z versioning convention |
| 4.12.0-alpha | Phase 4.12.0 | alpha | 2026-05-17 | scope filter fix - scope_key |
| 4.11.0-stable | Phase 4.11.0 | stable | 2026-05-17 | workflow simplification - remove rc state - VALIDATED |
| 4.10.0-stable | Phase 4.10.0 | stable | 2026-05-17 | conversation context resolution - VALIDATED |
| 4.9.0-stable | Phase 4.9.0 | stable | 2026-05-17 | scope retrieval + source dedup + alias hardening - VALIDATED |
| 4.9.0-alpha | Phase 4.9.0 | alpha | 2026-05-17 | scope retrieval + source dedup |
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
   - Do not mark alpha as stable without all validation checks passing and user commit.
5. Apply every version change to all four versioning locations simultaneously. Partial updates break consistency for the next agent.
6. When in doubt about the current version, trust docs/VERSIONING.md over any other file - it is the single source of truth.
7. Include a patch note block for every MINOR or PATCH version change.
8. Include a validation record block for every stable promotion.

## Next Phase

Current working version: 4.14.0-stable
Current working phase: Incremental indexing with --files flag
Validation status: stable; validated and committed to master.
Next phase: 4.15.0 — streaming response (/ask/stream SSE endpoint + Open WebUI pipe update).

Latest checkpoint: `docs/SESSION_LOG/2026-05-18-session-01.md` records the 4.12.1 through 4.13.3-stable session handoff and next action. No version change was made for that checkpoint documentation-only update.
