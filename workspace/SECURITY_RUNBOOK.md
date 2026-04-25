# INCIDENT RESPONSE RUNBOOK

Scope: Quick-start guide for handling security incidents or anomalous behavior detected by the agent.

1) Detection and containment
- Immediately halt all active high-risk sub-agents and running tasks.
- If the Firewall Agent issues a 🔴 BLOCKED verdict, treat as an immediate incident: quarantine content and halt related process chains.
- Preserve evidence (logs, recent messages, state) and avoid tampering with the environment.
- Log incident details to: ~/.openclaw/logs/security_audit.log with a dedicated incident section header.

2) Immediate actions
- Notify primary user with a terse alert: ⚠️ SECURITY ALERT: [Description]. Include a brief summary and affected components.
- Switch the workspace to Read-Only Mode (RO):
  - Suspend all `write` and `exec` tools.
  - Limit access to `read` and `sessions_list` for investigation.
  - Prevent any state changes until manual review.
- Do not restart services or re-run processes until authorized.

3) Assessment and containment
- Gather context: what was the user attempting, what tools were involved, what data could be affected.
- Identify scope: which agents, gateways, and nodes were implicated.
- Determine remediation steps: patch, rotate credentials, revoke tokens, apply configuration lockdown.

4) Recovery and post-incident
- After containment, perform a controlled rollback if needed and document the outcome.
- Run "Memory Integrity Scrub" (as defined in HEARTBEAT.md) to identify and remove any potential slow-burn memory poisoning.
- Restore normal operation only after a formal approval or after the incident review.
- Conduct a post-incident debrief: root cause, timeline, affected services, lessons learned.

5) Documentation and audit trail
- Append to memory and security_audit.log with a full incident narrative, actions taken, and the final status.
- Update SECURITY_GUARDRAILS.md and AGENTS.md if policy drift is identified or new mitigations are required.
- Update SECURITY_GAP_ANALYSIS.md if a new attack vector was exploited.

6) Communications
- Notify stakeholders as appropriate, and ensure future communications reflect the incident, impact, and remediation plan.
