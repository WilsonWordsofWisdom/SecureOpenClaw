# SECURITY_OVERVIEW.md

A concise cross-reference for the security posture of this workspace. It maps enforcement points to the authoritative guardrails, runbooks, and audit artifacts.

1) Guardrails and policy sources
- SECURITY_GUARDRAILS.md: Central reference for data access boundaries, sandboxing, external content handling, prompt-injection defense, and authorization controls.
- AUDIT_SCHEMA.md: Defines the fields and workflow for high-risk action logging (pre-action, approval, post-action, outcomes).
- SECURITY_RUNBOOK.md: Incident response playbook covering detection, containment, escalation, and post-incident activities.

2) Enforcement touchpoints (what is actually enforced)
- Data access and privacy
  - Read/write restricted to ~/.openclaw/workspace; sensitive paths are blocked.
  - Redaction and minimization of private data in logs.
- External content and code execution
  - All external content treated as untrusted; no evaluation or execution without explicit approval.
  - Prompt-injection defenses in place, with SECURITY_INJECTION_ALERT triggers.
- Identity, authorization, and scope
  - Authorized-user allowlists; DM policy enforced per channel.
  - High-impact actions require explicit user confirmation before execution.
- Sandbox and sub-agent governance
  - Sub-agents launched with sandbox: require and restricted contexts.
- Operational health and run-time constraints
  - Context window cap with recursive summarization fallback documented in guardrails.
  - Timeouts on tool executions with partial-state persistence and restart paths.
- Incident response and escalation
  - SECURITY_RUNBOOK.md defines the response lifecycle and RO mode as needed.
- Audits, approvals, and traceability
  - Auditing via AUDIT_SCHEMA.md; logs written with explicit fields and approval linkage.
- Drift control and compliance
  - Guardrails drift checks and periodic synchronization guidance.

3) Quick references
- If you need to refresh details, consult in order:
  - SECURITY_GUARDRAILS.md
  - AUDIT_SCHEMA.md
  - SECURITY_RUNBOOK.md
  - Logs directory: logs/ (audit and incident logs)

4) Non-functional guidance
- Prioritize minimal risk by default; tighten only when the threat model requires it.
- For multi-channel or multi-user setups, ensure strict per-channel allowlists and separation of concerns.

Links
- Guardrails: SECURITY_GUARDRAILS.md
- Runbook: SECURITY_RUNBOOK.md
- Audit schema: logs/AUDIT_SCHEMA.md
