# Announcement Refresh Report

- Batch Date: 2026-05-15
- Source Name: Daily Reminders
- Update Type: partial
- Input File: automation/ingestion/sample_announcement_batch.md
- Mode: write
- Communities Detected: Clearbrook Main, Gateway Towers, Palm Beach Main, Sierra Ridge, Somerset, global
- Categories Detected: approved_vendor, community_announcement, compliance_warning, event, gate_issue, nvr_issue, temporary_protocol, traffic_handling

## Added Announcements

- none

## Unchanged / Duplicate Announcements

- `global-compliance-warning-2fb7611ac9` duplicate hash
- `global-gate-issue-59fbe470ad` duplicate hash
- `global-temporary-protocol-dbd8af212b` duplicate hash
- `global-compliance-warning-15aaa9747f` duplicate hash
- `global-traffic-handling-2add581ccd` duplicate hash
- `global-nvr-issue-674a254eae` duplicate hash
- `somerset-community-announcement-2d90fa1d91` duplicate hash
- `clearbrook-main-event-1d75b9c596` duplicate hash
- `clearbrook-main-approved-vendor-21d526ef62` duplicate hash
- `sierra-ridge-gate-issue-884a274be6` duplicate hash
- `somerset-gate-issue-71f7f9d5fb` duplicate hash
- `palm-beach-main-nvr-issue-5480237367` duplicate hash
- `palm-beach-main-nvr-issue-16eed795d6` duplicate hash
- `gateway-towers-gate-issue-849d845c87` duplicate hash

## Review Needed

- none

## Pending / Expired Advisory Items

- none

## Reminder

- Rebuild ChromaDB after accepting announcement refresh output.
- Announcements are lower authority than post orders and higher authority than primary workflow.
- OCR is deferred; this script expects cleaned pasted text.
