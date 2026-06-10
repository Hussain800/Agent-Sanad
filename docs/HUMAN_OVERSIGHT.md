# Agent Sanad v1.5 Human Oversight

## Doctrine

LLM reads and explains. Deterministic code decides. Human owns the exception.

## Oversight Points

### 1. Exception Routing
Cases are auto-routed to human review when:
- Risk signals detected (INC-01, OBL-01, HARD-01, TEN-01)
- Confidence is medium or low
- Documents are missing or unverifiable
- Period compliance fails
- Active request already exists

### 2. Officer Workbench
- Complete evidence trace: state timeline, adapter source map, rule trace, calculation trace, period trace, security trace
- Append-only audit feed
- Actions: approve, adjust (reason required), escalate (reason required)
- Override reason codes for all non-approve actions
- OFF-01 audit event recorded for every officer action

### 3. Supervisor Command Center
- Backlog monitoring by status and age
- SLA risk board with breach tracking
- Fairness slice review
- Connector incident monitoring
- Officer workload distribution
- Override review with reason codes
- Consent denial rate tracking
- Document trust failure rate tracking
- Policy drift monitoring

### 4. Auditor Controls
- SHA256 audit chain verification
- Consent usage reports
- Package verification
- Access log export
- Responsible AI evidence pack

### 5. Override Governance
- Adjust actions require reason codes
- Escalate actions require reason codes
- All overrides recorded in append-only audit
- Supervisor can review override history
- Original deterministic recommendation always preserved

### 6. Confidence Bands
| Band | Criteria | Auto Action |
|------|----------|-------------|
| High | All gates passed, no risk signals, in-cap | Approve recommendation |
| Medium | FAM-01 or similar sensitivity flags | Officer review recommended |
| Low | Failed gates or major risk signals | Human review required |
