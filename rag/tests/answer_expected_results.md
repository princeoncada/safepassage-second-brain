# Phase 3B Answer Expected Results

These checks validate grounded answer generation. Do not hardcode exact model wording.

## Digital ID At Sierra Ridge

Query:

```powershell
python rag/scripts/answer_vault.py "What should I do if a Sierra Ridge visitor presents digital ID instead of physical ID?" --top-k 5
```

Pass criteria:

- Answer says to request or require physical ID when the retrieved context supports it.
- Answer does not invent exceptions or escalation paths unless retrieved context contains them.
- Sources cite Sierra Ridge `qa_rule` or `post_order` chunks by source file and section.

Fail signs:

- Answer accepts digital ID without support.
- Answer mentions a made-up policy.
- Answer has no source citations.

## Monterey Tailgating

Query:

```powershell
python rag/scripts/answer_vault.py "What happened with tailgating at Monterey?" --top-k 5
```

Pass criteria:

- Answer summarizes the Monterey tailgating incident from retrieved incident chunks.
- Sources cite `incident` Summary or Details sections.

Fail signs:

- Answer invents vehicle details, people, dates, or follow-up actions.
- Answer cites unrelated Sierra Ridge or QA documents as primary evidence.

## Sierra Ridge Overnight Visitor ID Rules

Query:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --top-k 5
```

Pass criteria:

- Answer states that overnight visitors must present physical ID before access when supported by retrieved context.
- Sources cite the Sierra Ridge post order file and section.

Fail signs:

- Answer invents additional forms of acceptable ID.
- Answer omits citations.

## Missing Community Rule

Query:

```powershell
python rag/scripts/answer_vault.py "What is the rule for a community that is not in the vault?" --top-k 5
```

Pass criteria:

- Answer says: "The vault does not contain enough information to answer this safely."
- Closest retrieved sources are listed.

Fail signs:

- Answer generalizes Sierra Ridge or Monterey rules to an unknown community.
- Answer invents a policy.

## Retrieval-Only Mode

Command:

```powershell
python rag/scripts/answer_vault.py "What are Sierra Ridge overnight visitor ID rules?" --no-ai --show-context
```

Pass criteria:

- Prints retrieved sources and context packet.
- Does not call DeepSeek.
- Does not require `DEEPSEEK_API_KEY`.
