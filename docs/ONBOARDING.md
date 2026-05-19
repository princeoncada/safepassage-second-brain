# SafePassage Second Brain Onboarding

This guide is for a new operator or engineer setting up the system from scratch.

## 1. Prerequisites

- Python 3.10+
- `pytesseract` Python package and the local Tesseract OCR binary for OCR
- DeepSeek API key
- Open WebUI, optional for the chat UI
- Git

## 2. Environment Setup

Clone the repository:

```powershell
git clone https://github.com/princeoncada/safepassage-second-brain.git
cd safepassage-second-brain
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create local environment config:

```powershell
copy .env.example .env
```

Edit `.env` and fill in `DEEPSEEK_API_KEY`.

`rag/chroma/` does not need to be committed. It is derived from `vault/` and is gitignored.

## 3. First-Time Indexing

Build the local ChromaDB index from vault Markdown:

```powershell
python rag/scripts/index_vault.py
```

Confirm ChromaDB files are created under:

```text
rag/chroma/
```

## 4. Running the API

Start the local FastAPI server:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

On startup, confirm the model log shows `Loading weights` once. It should load at server startup, not once per query.

Test `/ask`:

```powershell
curl http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"post orders for sierra ridge kiosk\",\"top_k\":5}"
```

## 5. Running a Query from CLI

Run a normal grounded answer:

```powershell
python rag/scripts/answer_vault.py "post orders for sierra ridge kiosk"
```

Inspect retrieval without AI:

```powershell
python rag/scripts/answer_vault.py --no-ai --show-context "glen kiosk"
```

## 6. Ingesting New Post Orders via Slash Command

In Open WebUI, type:

```text
/post-orders
```

Follow the two-step wizard:

1. Enter the community alias, such as `SR`, `CBK`, or `GLEN`.
2. Paste the post-order text.

Review the preview. Type `YES` to ingest or `NO` to cancel. If a conflict preview appears, choose `KEEP NEW` or `KEEP OLD` first.

## 7. Ingesting New Announcements

In Open WebUI, type:

```text
/announcements [alias] [text]
```

Example:

```text
/announcements CBK CBK Pickleball Tournament May 13. Visitors should say the event name.
```

Review the preview. Type `YES` to ingest or `NO` to cancel.

## 8. Rebuilding ChromaDB After Manual Vault Edits

Run a full rebuild:

```powershell
python rag/scripts/index_vault.py
```

Or incrementally index specific files:

```powershell
python rag/scripts/index_vault.py --files vault/03_Post_Orders/example.md
```

Use incremental indexing when you know exactly which vault Markdown files changed.

## 9. Reviewing the Audit Log

Show the latest audit entries:

```powershell
python automation/audit_review.py --tail 20
```

Filter by community and confidence:

```powershell
python automation/audit_review.py --community SR --confidence 0.5
```

The audit log is append-only JSON Lines under `logs/query_audit.jsonl` and is not committed.

## 10. Open WebUI Pipe Setup

Install the pipe from:

```text
openwebui/pipe.py
```

Point it to:

```text
http://localhost:8000/ask/stream
```

Use `openwebui/USAGE_GUIDE.md` for operator shift guidance, prompt patterns, citations, refusals, dashboard briefing usage, and boundaries.

## 11. Rollback

Inspect recent commits:

```powershell
git log --oneline
```

Restore a specific vault file from a known commit:

```powershell
git checkout <commit> -- vault/path/to/file.md
```

Rebuild ChromaDB after rollback:

```powershell
python rag/scripts/index_vault.py
```

Rollback changes source truth in `vault/`; the ChromaDB index must be rebuilt afterward.
