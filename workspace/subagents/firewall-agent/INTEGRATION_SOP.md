
## Inline FIREWALL SCAN REPORT TEMPLATE (inline)

You can copy-paste this block when composing a FIREWALL SCAN REPORT in communications or logs, without needing a separate file. The template is in JSON Lines style for easy appending.

```json
{
  "scan_id": "FA-20260418-0001",
  "timestamp_utc": "2026-04-18T17:25:00Z",
  "source": "Firewall Agent",
  "content_type": "skill_installation",
  "content_source": "skill-weather",
  "content_summary": "Pre-install audit check for weather skill; no external calls.",
  "findings": [
    {"id": "F1", "description": "no issues", "severity": "low", "location": "root"}
  ],
  "verdict": "CLEAN",
  "outcome": "approved",
  "approval_id": "APPR-0001"
}
```
