# Audit Log Schema — v1.0

## Purpose

Structured audit trail for high-risk and sensitive agent actions (skill installations, sudo/npm/pip commands, system config changes). Provides accountability, traceability, and rollback context.

## Log File

- Path: `workspace/logs/skill_installation_audit.log`
- Format: JSON Lines (one JSON object per line)
- Rotation: Optional daily rotation (`skill_installation_audit-YYYYMMDD.log`) + archive.
- Permissions: 600 (owner read/write only)

## Schema (per entry)

| Field           | Type   | Required | Description |
|-----------------|--------|----------|-------------|
| timestamp       | string | yes      | ISO 8601 UTC (e.g., 2026-04-18T16:51:00Z) |
| action          | string | yes      | e.g., `skill_install`, `npm_install`, `pip_install`, `sudo_exec`, `config_change` |
| target          | string | yes      | Skill/package/config target |
| version         | string | no       | Version / tag / commit |
| hash            | string | no       | SHA-256 of artifact (if applicable) |
| audit_summary   | string | yes      | Brief security review summary (no secrets) |
| approval_id     | string | yes      | Reference to user approval (e.g., message id) |
| outcome         | string | yes      | `pending` \| `approved` \| `denied` \| `success` \| `failure` \| `rolled_back` |
| reasoning_snapshot | string | yes | Concise summary of the agent's chain-of-thought/logic justifying the request |
| notes           | string | no       | Error/rollback context (no secrets) |

## Redaction Rules

- Never log secrets, API keys, credentials, tokens, or raw private data.
- If content would be sensitive, replace with `[REDACTED]`.

## Example Entry

```json
{"timestamp":"2026-04-18T16:51:00Z","action":"skill_install","target":"weather","version":"1.2.0","hash":"sha256:...","audit_summary":"Reviewed source: no secret access; no arbitrary code execution; minimal network scope. Low risk.","approval_id":"msg_124","outcome":"approved","notes":"User approved via Telegram."}
```

## Workflow

1. Pre-action log entry with `outcome: "pending"`
2. Ask user for explicit approval
3. On approval → execute + append `success`/`failure`
4. If rollback needed → append `rolled_back` with brief notes
