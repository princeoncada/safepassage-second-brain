# Phase 4B Primary Workflow Ingestion

Phase 4B adds a predictable way to ingest the SafePassage base kiosk training workflow as the primary workflow authority layer.

The primary workflow is default guidance only. It should answer base-process questions when no higher-authority source applies.

## Authority Hierarchy

```text
post_order
announcement
primary_workflow
```

Post orders have the highest authority. Announcements override the base workflow. Primary workflow is fallback/default guidance.

## Source Document

Expected source:

```text
NEW SAFEPASSAGE KIOSK TRAINING SCRIPT.pdf
```

OCR is not required. If PDF text extraction is unreliable, manually paste extracted text into:

```text
automation/ingestion/sample_primary_workflow_input.md
```

Use:

```text
automation/ingestion/primary_workflow_input_template.md
```

as the blank input structure.

## Ingest

Generate primary workflow Markdown:

```powershell
python automation/ingestion/ingest_primary_workflow.py
```

Generated files go to:

```text
vault/09_SOPs/
```

The script does not overwrite existing files unless `--force` is passed:

```powershell
python automation/ingestion/ingest_primary_workflow.py --force
```

Each generated document includes:

- `type: "workflow"`
- `authority_level: "primary_workflow"`
- `community: "global"`
- `scope: ["kiosk"]`
- source document, source section, source page, and authority note

## Reindex

After ingestion:

```powershell
python rag/scripts/reset_chroma.py --yes
python rag/scripts/index_vault.py
```

## Validate

Default workflow:

```powershell
python rag/scripts/query_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What is the default process when a guest has no physical ID?" --top-k 5
```

Expected: retrieve `primary-no-physical-id` and answer with primary/default workflow language.

Community override:

```powershell
python rag/scripts/query_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Expected: Sierra Ridge post order or QA rule outranks primary workflow.

Default call attempts:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident by default?" --top-k 5
```

Expected: answer says default is twice and to check post orders for accuracy.

Unknown community fallback:

```powershell
python rag/scripts/answer_vault.py "How many times do I call the resident for Atlantis Bay?" --top-k 5
```

Expected: answer says no Atlantis Bay-specific source exists and may cite primary workflow only as default guidance.

## What Not To Do

- Do not treat primary workflow as equal to a post order.
- Do not use primary workflow to override announcements.
- Do not hallucinate community-specific policy from global workflow.
- Do not add agents, autonomous memory editing, Git automation, dashboards, or Phase 4C behavior.

## Known Limitations

- PDF parsing is not required and may be unreliable.
- Manual extraction quality affects retrieval quality.
- Primary workflow is global fallback guidance, not community-specific authority.
- Generated files should be reviewed before committing.
