# Open WebUI Ingest Commands

Use these commands only when you are ready to paste reviewed text into Open WebUI for deterministic ingestion. The system always shows a preview first. Nothing is written to `vault/` until you reply `YES`.

## Supported Commands

### Post Orders

Format:

```text
/post-orders [community alias] [pasted post order text]
```

Example:

```text
/post-orders CBK 5/17/2026 Post Order (K): Only contact the resident twice to confirm visitor access.
```

The preview lists each parsed rule with its rule number, type, and text. Reply `YES` to ingest or `NO` to cancel.

### Announcements

Format:

```text
/announcements [community alias] [pasted announcement text]
```

Example:

```text
/announcements CBK CBK Pickleball Tournament May 13, 16, 26, June 2, 17, July 7, 14, 15. Visitors should say the name of the event.
```

The preview lists each parsed announcement with its number, inferred category, and text. Reply `YES` to ingest or `NO` to cancel.

## Confirmation

After the preview, answer with exactly:

```text
YES
```

to write to `vault/` through the existing deterministic ingestion script and rebuild ChromaDB.

Answer with:

```text
NO
```

to cancel. Cancellation clears the pending request and writes nothing.

Pending previews expire after 5 minutes. If the session expires, resubmit the slash command.

## What Happens After YES

For `/post-orders`, the backend writes a temporary batch file and calls:

```text
automation/ingestion/refresh_post_orders.py
```

For `/announcements`, the backend writes a temporary batch file and calls:

```text
automation/ingestion/refresh_announcements.py
```

If ingestion succeeds, the backend calls:

```text
rag/scripts/index_vault.py
```

The temp batch file is deleted after successful ingestion and rebuild. The system then answers with what was written and whether ChromaDB was rebuilt.

## What Happens After NO

The pending request is cleared. Nothing is written to `vault/`, and ChromaDB is not rebuilt. You can safely retry with a corrected command.

## Common Mistakes

- Missing alias: use `/post-orders CBK ...`, not `/post-orders ...`.
- Unrecognized alias: use one of the supported aliases listed below.
- Pasting without a command: normal chat questions still go through RAG answering and do not ingest text.
- Replying with anything except `YES`: use `NO` to cancel cleanly.
- Waiting too long: pending previews expire after 5 minutes.

## Supported Community Aliases

| Alias | Community |
| --- | --- |
| BBL | Blue Bell Main |
| BBLM | Blue Bell Morris RD |
| BBLN | Blue Bell North Wales |
| BLC | Bellechase |
| CBK | Clearbrook Main |
| CBKE | Clearbrook East |
| CBKN | Clearbrook North |
| CFX | (Kings Point) Clairmont Fairfax |
| CLW | Clarewood |
| DCTC | Deep Canyon Tennis Club |
| DULT | Dulaney Towers |
| ENV | Environ |
| FLL | Floral Lakes |
| GLEN | The Glen (Tamiment) |
| GWT | Gateway Towers |
| HP | Heritage Palms |
| HPD | Heritage Palms Dunbar |
| HPM | Heritage Palms Miles |
| HPN | Heritage Palms North |
| HPS | Heritage Palms South |
| HPW | Heritage Palms Wal |
| LACU | Lacuna (Atlantic National) |
| MON | Monterey |
| OPB | Old Pelican Bay |
| PAL | Paloma |
| PBPB | Palm Beach Back (Pioneer) |
| PBM | Palm Beach Main |
| PBPG | Palm Beach Greenwood (Manor) |
| PLM | Palm Isles |
| PLMIC | Palm Isles Condo 3 |
| PLMIM | Palm Isles Main |
| RH | Rolling Hills |
| RHL | Royal Highlands |
| SDP | Sandpiper |
| SR | Sierra Ridge |
| SSR | Somerset |
| SSRC | Silver Sands |
| TUB | Tuscany Bay |
| VC | Victoria |
| KPW | (Kings Point) Weldon |

## Worked Example: CBK Post Order

1. Send:

```text
/post-orders CBK 5/17/2026 Post Order (K): Only contact the resident twice to confirm visitor access.
```

2. Review the preview:

```text
Post order preview for Clearbrook Main (CBK) - 1 rule(s) parsed:

1. [K] Only contact the resident twice to confirm visitor access.

Confirm ingestion? Reply YES to write to vault or NO to cancel.
```

3. Reply:

```text
YES
```

4. The system writes through the post-order refresh script, rebuilds ChromaDB, and confirms completion.

## Worked Example: CBK Announcement

1. Send:

```text
/announcements CBK CBK Pickleball Tournament May 13, 16, 26, June 2, 17, July 7, 14, 15. Visitors should say the name of the event.
```

2. Review the preview:

```text
Announcement preview for Clearbrook Main (CBK) - 1 announcement(s) parsed:

1. [event] CBK Pickleball Tournament May 13, 16, 26, June 2, 17, July 7, 14, 15. Visitors should say the name of the event.

Confirm ingestion? Reply YES to write to vault or NO to cancel.
```

3. Reply:

```text
YES
```

4. The system writes through the announcement refresh script, rebuilds ChromaDB, and confirms completion.
