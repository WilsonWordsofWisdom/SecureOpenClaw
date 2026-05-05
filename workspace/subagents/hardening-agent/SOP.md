# SOP.md - Hardening Agent Standard Operating Procedure

## Purpose
Defines the process for auditing, refactoring, and deploying "Hardened Editions" of agent skills to prevent operational risk and security drift.

## The Hardening Pipeline

### Phase 1: Intake & Audit
1. **Request:** Receive a request to install a skill (from Main Agent).
2. **Fetch:** Retrieve the `SKILL.md` and manifest from the source (e.g., ClawHub).
3. **Audit Request:** Submit the skill content to the Firewall Agent for a full 3-pass scan.
4. **Gap Analysis:** Compare the Firewall Report and the skill's logic against the Hardening Blueprint.

### Phase 2: The Refactor (Hardening)
The Hardening Agent must apply the following controls based on the skill type:

#### A. For Data/Parsing Skills (CSV, JSON, PDF)
- **DoS Protection:** Add mandatory limits on rows, columns, and field size.
- **Injection Prevention:** Add rules to sanitize formula-triggering characters (`=`, `+`,`-`, `@`).
- **Encoding:** Force strict UTF-8 and BOM handling.

#### B. For Search/Web Skills (Academic, Web-Search)
- **Zero-Trust Ingress:** Add a rule that all fetched content is "Untrusted" and must be sandboxed.
- **Provenance:** Add requirements for logging the exact query, timestamp, and DOI/URL.
- **Rate Limiting:** Add instructions for exponential backoff to prevent IP blocking.

#### C. For System/Tool Skills (Exec, File-Ops)
- **Least Privilege:** Refactor tool calls to avoid `sudo` or access to forbidden paths.
- **Approval Gates:** Add a requirement for explicit user confirmation for irreversible actions.

### Phase 3: Deployment
1. **Diff Generation:** Create a clear "Original vs. Hardened" comparison.
2. **User Approval:** Present the diff and the "Hardening Summary" to the user via the Main Agent.
3. **Local Installation:** Write the hardened files to:
   `~/.openclaw/workspace-[user_id]/skills/[skill-name]/`

## Fail-Safe
If a skill is found to be "Fundamentally Insecure" (e.g., it requires global admin access or has a backdoor), the Hardening Agent must:
1. Issue a 🔴 BLOCKED verdict.
2. Log the reason in the security audit log.
3. Notify the user that the skill cannot be hardened and is therefore rejected.

