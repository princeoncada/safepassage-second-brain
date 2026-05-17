# SafePassage Second Brain - Operational Workflow Reference

## Purpose

This file defines the standard workflow for all AI agents and human contributors working on this project. It must be read at the start of every session before any planning, coding, or documentation work begins.

## Session Opening Ritual

Every new session - whether a new chathead, a new AI agent, or a continuing session - must begin with these steps in order:

Step 1: Sync the repo
  Pull the latest master branch before reading anything.
  Never assume local files are current.
  Command: git pull origin master

Step 2: Read these files in order
  1. docs/VERSIONING.md      - current version and state machine
  2. docs/AI_HANDOFF.md      - current phase, what exists, next step
  3. docs/PHASE_LOG.md       - full history and validation records
  4. docs/DECISIONS.md       - architectural constraints and ADRs
  5. docs/WORKFLOW.md        - this file, operational process
  6. README.md               - version badge and phase list

Step 3: Report state before acting
  After reading, the AI agent must state:
  - Current version (from VERSIONING.md)
  - Current phase and its state (alpha/beta/rc/stable)
  - What is in progress or pending
  - Recommended next action
  The user confirms or redirects before any work begins.

Step 4: Sync again before writing any Codex prompt
  Always pull master immediately before writing a Codex prompt.
  Never write a Codex prompt from a stale local state.

## Standard Phase Cycle

Every phase follows this cycle. Steps must not be skipped.

PLAN
  AI and user discuss the phase scope.
  AI asks clarifying questions before writing anything.
  Output: agreement on what will be built.

PROMPT
  AI writes the Codex master prompt.
  Format: one clean code block only.
  Required sections in every prompt:
    - PROJECT and TASK header with version
    - BEFORE CHANGING ANYTHING - read file list
    - CURRENT PROJECT STATE - commit hash, validated phases, current bugs
    - IMPLEMENTATION - numbered requirements with file-level detail
    - SAFETY CONSTRAINTS - never/always lists
    - FILES TO CHANGE - explicit modify/create/do not touch lists
    - AFTER IMPLEMENTATION - stop and summarize instruction

BUILD
  User runs Codex with the prompt.
  AI does not assist during this step.

VERIFY
  AI writes PowerShell validation commands.
  These are always given SEPARATELY from the Codex prompt.
  Never include validation commands inside the Codex prompt.
  Never tell Codex to validate its own implementation.

TEST
  User runs validation commands and pastes results here.

ANALYZE
  AI reviews every validation check individually.
  Reports pass/fail per check with root cause for any failure.
  Identifies any non-blocking observations separately from blockers.

FIX (if needed)
  AI writes a targeted fix prompt.
  Fix prompts must include:
    - Root cause explanation
    - Exact files to change
    - Exact logic to add or modify
    - Do not touch list
  Repeat from BUILD until all checks pass.

DOCUMENT
  After all checks pass, AI writes a post-validation Codex prompt.
  This prompt always:
    - Promotes the version from rc to stable
    - Records the validation results in PHASE_LOG.md
    - Updates all four versioning locations
    - Updates AI_HANDOFF.md recommended next step
  This step is mandatory after every successful validation.
  It is never optional or deferred.
  Note: The post-validation documentation prompt is given as a plain
  Codex prompt block only. The 3-section wrapper is not used here.
  Only implementation work uses the 3-section format.

COMMIT
  User manually commits all changes to master.
  AI never commits, pushes, or creates branches.
  After commit: version state becomes stable in the next session.

## Codex Prompt Standards

Every Codex prompt must follow these rules:

Read-first list (mandatory, always included):
  - docs/VERSIONING.md
  - docs/AI_HANDOFF.md
  - docs/PHASE_LOG.md
  - docs/DECISIONS.md
  - docs/WORKFLOW.md
  - Plus any files directly relevant to the implementation

Git rules (mandatory, always included):
  - Do NOT commit
  - Do NOT push
  - Do NOT create branches
  - Do NOT run validation commands
  - Do NOT validate your own implementation

Stop instruction (mandatory, always last):
  Stop after implementation and summarize:
  1. Files changed and files created
  2. Logic added or modified per file
  3. Expected behavior after the changes
  4. Any assumptions made during implementation

Documentation requirement (mandatory for every phase prompt):
  Documentation updates are implementation requirements, not afterthoughts.
  Every phase prompt must include updates to:
  - README.md (phase list with version number)
  - docs/PHASE_LOG.md (phase entry with version tag and checklist)
  - docs/AI_HANDOFF.md (current phase, what exists, recommended next step)
  - docs/VERSIONING.md (version history table)

## When To Use The 3-Section Format

The 3-section format (SECTION 1: Codex Master Prompt / SECTION 2: What
You Need From Me / SECTION 3: PowerShell Validation Commands) is only
used for implementation work.

USE 3-section format for:
- Starting a new phase
- Fixing a bug or regression
- Any task where Codex will write or modify code

DO NOT USE 3-section format for:
- Post-validation documentation prompts
  (version promotion, recording validation results, patch notes)
- Session checkpoint prompts before closing a chathead
- Any documentation-only Codex task

For post-validation documentation and session checkpoints:
- Give the Codex prompt directly as a single plain txt code block
- No Section 2 or Section 3 needed
- These prompts touch only docs/ files, never code

## Post-Validation Documentation Prompt

After every successful validation, AI writes a separate Codex prompt that records the results and promotes the version. This prompt always:

1. Lists every validation check with PASSED or FAILED
2. Records known remaining items (non-blocking)
3. Promotes version in all four locations (rc -> stable)
4. Adds a Validation Record section to PHASE_LOG.md
5. Updates AI_HANDOFF.md recommended next step
6. Updates docs/VERSIONING.md current version table

This prompt runs after the user commits, or immediately before if the user wants to commit everything in one shot.

## Context Window Management

When a chathead conversation becomes long, use this process to preserve state before opening a new chathead.

Signs that context window management is needed:
  - Conversation has been running for many hours
  - Multiple phases have been completed in one session
  - AI starts losing track of earlier decisions
  - User wants to close and continue later

Session Checkpoint process:
  Step 1: AI writes a SESSION CHECKPOINT Codex prompt
    This prompt:
    - Updates docs/AI_HANDOFF.md with exact current state
    - Updates docs/VERSIONING.md with any in-progress version
    - Records any uncommitted in-progress work with its version state
    - Creates docs/SESSION_LOG/YYYY-MM-DD-HH.md with session summary
      containing: what was done, what is in progress, what is next,
      any open decisions, and any known issues
    - References docs/NEW_CHATHEAD_OPENER.md for the new chathead opener

  Step 2: User runs the checkpoint prompt through Codex and commits

  Step 3: New chathead opens
    User pastes only: the repo URL
    AI pulls master, reads the six required files, and reports state
    No other context from the old chathead is needed

Session log format (docs/SESSION_LOG/YYYY-MM-DD-HH.md):
  # Session Log - YYYY-MM-DD HH:MM
  ## What Was Done
  ## What Is In Progress
  ## Current Version State
  ## Open Decisions
  ## Known Issues
  ## Next Recommended Action
  ## New Chathead Opener
  See docs/NEW_CHATHEAD_OPENER.md for the current opener text.

The session log must reference docs/NEW_CHATHEAD_OPENER.md for the
opener text. It must NOT embed the opener inline. The canonical opener
is always stored in docs/NEW_CHATHEAD_OPENER.md and updated there only.

## Repo Awareness Rules

AI must follow these rules to stay repo-aware:

1. Pull master at the start of every session before reading any file.
2. Pull master immediately before writing any Codex prompt.
3. Never write a Codex prompt based on files read more than one step ago.
4. After user commits, acknowledge the new commit state before continuing.
5. If a pull reveals unexpected changes, report them before proceeding.
6. Never assume a local file reflects the current master state.

## Live Operational Testing

When the user tests the system during an actual work shift:

1. Treat live operational feedback as the highest priority signal.
2. Any gap discovered during live use becomes a bug or missing feature.
3. Document operational gaps as known issues in AI_HANDOFF.md immediately.
4. Do not defer live operational issues to a later phase without explicit agreement.
5. Prioritize fixes that affect the user's ability to do their job right now.

## Versioning Integration

This workflow integrates with the versioning system in docs/VERSIONING.md.

Version state during the phase cycle:
  PLAN and PROMPT stages:     previous stable version still current
  BUILD stage:                new alpha version assigned
  TEST stage:                 alpha or beta depending on first results
  after all checks pass:      rc version assigned
  after DOCUMENT prompt runs: rc version recorded
  after user commits:         stable version in next session

Every Codex prompt header must include the current version:
  PROJECT: SafePassage Second Brain
  TASK: [description]
  VERSION: [current version being worked on]

## Safety Rules That Never Change

Regardless of phase or instruction:
  - Do NOT write to vault/ without explicit YES confirmation
  - Do NOT bypass human review before ingestion
  - Do NOT weaken safe refusal
  - Do NOT hallucinate communities
  - Do NOT let announcements override post orders
  - Do NOT add autonomous agents
  - Do NOT commit, push, or create branches
  - Do NOT run validation commands inside Codex prompts
  - ALWAYS preserve: post_order > announcement > primary_workflow
  - ALWAYS preserve: vault/ as source of truth
  - ALWAYS preserve: rag/chroma/ as disposable derived data
