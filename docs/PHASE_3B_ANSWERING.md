# Phase 3B Answer Generation From Retrieved Vault Context

## What Phase 3B Does

Phase 3B adds a minimal answer-generation CLI on top of Phase 3A retrieval.

Flow:

```text
question
-> local embedding
-> ChromaDB retrieval
-> compact context packet
-> DeepSeek final answer
-> cited response
```

Answers must use only retrieved vault chunks.

## What Phase 3B Does Not Do

- No Open WebUI.
- No n8n integration.
- No agents.
- No automatic memory editing.
- No Git automation.
- No dashboards or UI.
- No Phase 4 automation.

## Set The API Key

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_key_here"
```

Do not commit API keys.

## Run With AI

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

## Run Retrieval Only

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

`--no-ai` prints retrieved context and citations without calling DeepSeek or requiring an API key.

## Citations

Answers should cite source file and section:

```text
Sources:
[1] vault/04_QA_Rules/example.md — Agent Action
[2] vault/03_Post_Orders/example.md — Details
```

The script also prints the retrieved source summary and citations after the generated answer.

## Insufficient Context

When retrieved context does not directly answer the question, the answer must say:

```text
The vault does not contain enough information to answer this safely.
```

Then it should list the closest retrieved sources.

## Validation

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --top-k 5
python rag/scripts/answer_vault.py "What is the rule for a community that is not in the vault?" --top-k 5
```

Expected behavior is documented in `rag/tests/answer_expected_results.md`.

## Known Limitations

- The answer quality depends on retrieved chunks.
- The model can only answer from indexed Markdown.
- Missing or weak vault content should produce an insufficient-context answer.
- This is a CLI proof of work, not a production assistant.
