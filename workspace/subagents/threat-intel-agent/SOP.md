# SOP.md - Threat Intel Agent Standard Operating Procedure

## Purpose
Defines the operational cycle for the Threat Intel Agent (TIA) to maintain the security posture of the OpenClaw workspace.

## Operational Cycle

### 1. Weekly Intel Sweep
- **Trigger:** Scheduled heartbeat or Main Agent request.
- **Mandatory Sources:** The TIA must limit its research to these four authoritative sources to optimize token usage and maintain data quality:
    - **OWASP Agentic:** https://owasp.org/www-project-agentic-ai-top-10/ (Quarterly)
    - **MITRE ATLAS:** https://atlas.mitre.org/ (Weekly)
    - **Giskard AI Security Feed:** https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026 (Daily)
    - **Snyk Vulnerability DB:** https://security.snyk.io/ (Daily)
- **Action:** 
    - Execute targeted scans of the mandatory sources or web searches for latest agentic AI vulnerabilities.
    - **Delta Analysis:** Focus specifically on updates since the last scan date recorded in `SECURITY_GAP_ANALYSIS.md`.
    - Prioritize the extraction of new risks, vulnerabilities, or control recommendations over general reading.
- **Output:** A list of "Candidate Threats."

### 2. Internal Review
- **Action:** Compare candidate threats against `SECURITY_GAP_ANALYSIS.md` and `SECURITY_GUARDRAILS.md`.
- **Verdict:** 
  - *Mitigated*: No action needed.
  - *Partial*: Update existing guardrail for better coverage.
  - *Gap*: New control required.

### 3. Proposal Submission
- **Action:** Submit a "Threat Intel Report" to the Main Agent.
- **Content:** Threat description, evidence, and proposed mitigation.

### 4. Approval & Implementation (The Main Agent's Role)
- **Process**:
  1. TIA $\rightarrow$ Main Agent (Report)
  2. Main Agent $\rightarrow$ User (Approval Request)
  3. User $\rightarrow$ Main Agent (Approval/Denial)
  4. Main Agent $\rightarrow$ File System (Implements the a-symmetric control)

## Integration with Security Artifacts
- **SECURITY_GAP_ANALYSIS.md**: The TIA provides the raw data to update this file.
- **SECURITY_GUARDRAILS.md**: The TIA suggests the specific wording for new rules.
- **red_team_results.csv**: TIA analyzes red-team failures to suggest new controls.

## Fail-Safe
If the TIA detects a "Critical" threat that could lead to immediate compromise, it must bypass the weekly cycle and issue an **IMMEDIATE SECURITY ALERT** to the Main Agent.