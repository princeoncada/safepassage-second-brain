# Open WebUI Shift Reference Guide

This guide is for VA operators using Open WebUI during a shift. The system answers from indexed SafePassage source files only. It is a reference tool, not a replacement for post orders, supervisors, live systems, or human judgment.

## How To Start A Query

Ask one direct operational question at a time. Include the community name or alias when the question is community-specific.

Useful examples:

- `What are the current post orders for Clearbrook Main CBK visitor ID?`
- `Does Sierra Ridge SR require physical ID for visitors?`
- `Are there active announcements for Palm Beach Main PBM?`
- `What Gateway Towers GWT announcements are active today?`
- `Are there gate, NVR, or kiosk issues for Monterey MON?`
- `What workflow should I follow for a call attempt if no community post order applies?`
- `Show me any compliance warnings for Somerset SSR.`
- `What should I know before working Heritage Palms HP tonight?`
- `Are there current reminders for Blue Bell Main BBL?`

Use the full community name if the alias is not familiar. Use the alias if you need a shorter prompt.

## How To Interpret An Answer

Every grounded answer should include citations. A citation points to the source file, section, and authority level used for the answer.

Authority levels matter:

- `post_order` is the highest authority.
- `announcement` can add current reminders or temporary instructions, but it does not override a post order.
- `primary_workflow` is default workflow guidance when no stronger community-specific source applies.

A safe refusal means the system does not have enough indexed information for that community or topic. Do not treat a refusal as proof that no rule exists. It only means the system cannot answer from indexed sources.

A low-confidence or warning response means the system found weak, pending, expired, future-dated, review, or stale information. Treat those answers as advisory and verify through normal channels before acting.

## Shift Start Workflow

At the beginning of a shift, run a short set of queries for situational awareness:

1. Check active announcements:
   `What active announcements should I know about for CBK?`

2. Check gate, NVR, or kiosk issues:
   `Are there any gate, NVR, or kiosk issues for Sierra Ridge SR?`

3. Check post orders for the assigned community:
   `What are the current post orders for Palm Beach Main PBM access control?`

4. Check compliance warnings:
   `Show compliance warnings for Gateway Towers GWT.`

5. If assigned to a less familiar post, ask for a compact briefing:
   `Give me a shift briefing for Monterey MON.`

## Dashboard Shift Briefing

The dashboard is a read-only shift briefing view built from indexed source files.

Use:

- `/dashboard/briefing` for a Markdown briefing grouped by operational section.
- `/dashboard/summary` for the same dashboard data in structured form.
- `/dashboard/briefing?community=CBK` to filter the briefing to Clearbrook Main and global items.
- `/dashboard/summary?community=SR` to filter structured dashboard data to Sierra Ridge and global items.

Briefing sections:

- Active Temporary Protocols: temporary instructions currently in effect.
- Gate / NVR / Kiosk Issues: access-control equipment, camera, kiosk, traffic, or emergency handling notes.
- Active Events: current event-related operational notes.
- Important Operational Reminders: active announcements that do not fit the other sections.
- Expiring Soon: items with near-term end or expiry dates.
- Community-Specific Alerts: active items tied to a specific community.
- QA / Compliance Warnings: compliance, QA, required-action, or termination-risk notes.

Dashboard summaries do not override the cited source files. If the dashboard and a post order appear to conflict, follow the post order and escalate for clarification.

## When The System Refuses To Answer

If the system refuses, it means it cannot find enough indexed source material to answer safely.

Next steps:

- Check the physical post order binder or approved community instructions.
- Ask a supervisor or lead for direction.
- Escalate through normal SafePassage channels.
- Do not invent an answer from memory if the matter affects access, safety, compliance, or resident handling.

## What Not To Rely On The System For

Do not rely on Open WebUI to:

- Make real-time judgment calls.
- Override post orders.
- Replace human review before ingestion.
- Confirm live gate, NVR, camera, or kiosk status.
- Act autonomously or take action for you.
- Prove that no rule exists when it refuses to answer.

## Worked Examples

1. Prompt: `What is the current visitor ID rule for Clearbrook Main CBK?`
   Expected answer type: post order answer with source citations if indexed.

2. Prompt: `Does Sierra Ridge SR accept digital ID for visitors?`
   Expected answer type: post order answer if available; otherwise a safe refusal or warning.

3. Prompt: `Are there active announcements for Palm Beach Main PBM?`
   Expected answer type: active announcement summary with citations, or safe refusal if none are indexed.

4. Prompt: `What Gateway Towers GWT reminders are active today?`
   Expected answer type: announcement or reminder answer with temporal status.

5. Prompt: `Are there NVR issues for Monterey MON?`
   Expected answer type: gate/NVR/kiosk issue summary if indexed, with source citations.

6. Prompt: `Show me compliance warnings for Somerset SSR.`
   Expected answer type: QA or compliance warning summary, or safe refusal if no indexed warnings exist.

7. Prompt: `What is the default call-attempt workflow?`
   Expected answer type: primary workflow guidance, labeled as default guidance.

8. Prompt: `What are the post orders for Heritage Palms HP?`
   Expected answer type: community-specific post order summary if indexed.

9. Prompt: `Are there current announcements for Blue Bell Main BBL gate access?`
   Expected answer type: announcement answer if active announcements exist, or refusal if there is no indexed source.

10. Prompt: `What is the vehicle policy for Atlantis Bay?`
    Expected answer type: safe refusal because Atlantis Bay is not an indexed known community.

11. Prompt: `Can I ignore a post order if an announcement says something different?`
    Expected answer type: refusal or authority reminder that post orders remain higher authority than announcements.

12. Prompt: `Is the CBK gate working right now?`
    Expected answer type: refusal or warning because the system cannot confirm live equipment status.
