# Agent Sanad v1.5 Connector Contracts

## Connectors (7 mock, contract-true)

| Connector | Owner | Services |
|-----------|-------|----------|
| uaepass | UAEPASS | auth, userinfo, signature, eseal |
| gsb | TDRA-GSB | identity.profile, housing.loan, housing.arrears, financial.liabilities |
| szhp-core | SZHP | applicant.profile, loan.account, arrears.ledger, payment.history |
| uae-verify | TDRA-UAEVerify | verify.document, verify.batch |
| financial-capacity | ECB-Mock | salary.verify, obligations.summary, credit.risk-band |
| notifications | NIA-Mock | sms, email, push, callback |
| case-management | SZHP-Case | assign_officer, schedule_callback, record_note, update_sla, create_escalation, close_case |

## Contract Shape

All connectors follow the same contract:

### Health Check
```json
GET /connectors/{name}/health
{"name": "...", "status": "up|degraded", "failure_mode": null, "mock": true, "timestamp": "..."}
```

### Simulate Failure
```json
POST /connectors/{name}/simulate {"failure_mode": "timeout"}
```

### Reset
```json
POST /connectors/{name}/reset {}
```

### Consent Policy
All connectors require consent before returning sensitive data. Consent is validated against purpose, scope, expiry, revocation, and beneficiary ownership.

## Failure Modes

| Mode | Behavior |
|------|----------|
| timeout | Returns timeout status after 500ms |
| provider_down | Returns provider_down status |
| stale_data | Returns stale data flag |
| consent_missing | Returns consent_denied |

## Pydantic Models

All connector request/response payloads use Pydantic v2 models with `extra="forbid"`.

Key models:
- `ConnectorHealthResponse` - health check response
- `CaseAssignRequest` / `CaseAssignResponse` - case assignment
- `ConsentValidateRequest` / `ConsentValidateResponse` - consent validation
- `AppealCreateRequest` / `AppealCreateResponse` - appeal creation
- `AppealDecisionRequest` - appeal decision
