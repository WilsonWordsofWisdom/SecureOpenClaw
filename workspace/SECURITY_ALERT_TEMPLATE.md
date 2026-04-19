# SECURITY_ALERT_TEMPLATE.md

Template for channel-scoped security alerts. Copy-paste and fill fields as incidents occur. This keeps incident reporting consistent across surfaces.

Alert header (matter-of-fact):

- ⚠️ SECURITY ALERT: [IncidentType] detected on [Host/Component]

Core details:

- Time (UTC/GMT+08:00): [2026-04-18T17:04:00Z]
- Affected components: [Gateway|Node|Agent|Module]
- Description: [Brief summary of the anomaly or breach]
- Immediate actions taken: [Containment steps, e.g., RO mode, halt sub-agents]
- Next steps requested: [Remediation plan and approvals]
- Logs/References: [Paths to security_audit.log, incident id]

Channel-specific formatting:

- Telegram/Whatsapp: one concise message; no embeds
- Slack: short alert with a link to logs or a dedicated thread

Example:

- ⚠️ SECURITY ALERT: Potential privilege-escalation on gateway.local
- Time (UTC/GMT+08:00): 2026-04-18T17:04:00Z
- Affected components: gateway
- Description: Suspicious pre-action audit entry observed; awaiting approval
- Immediate actions taken: RO mode engaged
- Next steps: Validate approvals; rotate credentials if needed
- Logs/References: ~/.openclaw/logs/security_audit.log; incident_id=SEC-2026-0418-02
