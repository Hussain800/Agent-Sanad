# Agent Sanad v1.5 API Guide

**Version**: 1.5.0  
**Base URL**: `http://127.0.0.1:8000`  
**Auth**: `x-sanad-role` header (beneficiary, officer, supervisor, auditor, admin)  
**Error Envelope**: `{"error_code": "...", "message": "...", "path": "...", "app_version": "1.5.0"}`

## Core Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/healthz` | Liveness + mock_mode + app_version |
| GET | `/cases` | List seeded case IDs |
| GET | `/cases/{id}` | Case snapshot |
| POST | `/demo/run/{id}` | Full case decision |
| POST | `/applications/mock/decide` | Custom application decision |
| GET | `/officer-actions` | List officer actions |
| GET | `/benchmark` | Historical benchmark metrics |
| GET | `/architecture` | IBM 7-skills mapping |

## v1.5 Consent Guard v2

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/consents` | Create consent |
| GET | `/consents/{id}` | Get consent |
| POST | `/consents/{id}/revoke` | Revoke consent |
| POST | `/consents/{id}/validate` | Validate consent (purpose, scope, expiry, ownership) |
| GET | `/consents/{id}/usage` | Consent usage history |
| GET | `/cases/{id}/consent-events` | Consent events for case |

## v1.5 UAE PASS Session v3

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/sessions/uaepass/mock/start` | Start session |
| GET | `/sessions/{id}` | Get session state |
| POST | `/sessions/{id}/expire-mock` | Force expire session |
| POST | `/sessions/{id}/revoke-mock` | Revoke session |

## v1.5 Actions v4

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/cases/{id}/actions/{aid}/upload-mock` | Upload action evidence |
| POST | `/cases/{id}/actions/{aid}/reject` | Reject action |
| POST | `/cases/{id}/actions/{aid}/resubmit` | Resubmit action |
| POST | `/cases/{id}/actions/{aid}/complete` | Complete action |
| POST | `/cases/{id}/actions/{aid}/waive` | Waive action |
| GET | `/cases/{id}/actions` | List actions |
| GET | `/cases/{id}/actions/timeline` | Action event timeline |

## v1.5 Appeals Workbench

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/cases/{id}/appeals` | Create appeal |
| GET | `/cases/{id}/appeals` | List case appeals |
| GET | `/appeals` | List all appeals |
| GET | `/appeals/{id}` | Get appeal detail |
| POST | `/appeals/{id}/submit-evidence` | Submit evidence |
| POST | `/appeals/{id}/review` | Start officer review |
| POST | `/appeals/{id}/decision` | Make decision |
| POST | `/appeals/{id}/supervisor-approve` | Supervisor approval |

## v1.5 Decision Packages v2

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/cases/{id}/decision-package` | Create package |
| GET | `/cases/{id}/decision-package` | Get package |
| POST | `/decision-packages/{id}/verify` | Verify package integrity |
| GET | `/decision-packages/{id}/receipt` | Get receipt + verification |
| POST | `/decision-packages/{id}/revoke-mock` | Revoke package |

## v1.5 Supervisor Command Center

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/supervisor/metrics` | Summary metrics |
| GET | `/supervisor/overrides` | Override history |
| GET | `/supervisor/backlog` | Case backlog |
| GET | `/supervisor/sla-risk` | SLA risk board |
| GET | `/supervisor/fairness` | Fairness slices |
| GET | `/supervisor/connectors/incidents` | Connector incidents |
| GET | `/supervisor/officer-workload` | Officer workload |
| GET | `/supervisor/override-review` | Override review |
| GET | `/supervisor/consent-denial-rate` | Consent denial rate |
| GET | `/supervisor/document-trust-failure-rate` | Document trust failure rate |
| GET | `/supervisor/connector-health` | Connector health |
| GET | `/supervisor/policy-drift` | Policy drift |

## v1.5 Case Management Connector

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/connectors/case-management/mock/assign-officer` | Assign officer |
| POST | `/connectors/case-management/mock/schedule-callback` | Schedule callback |
| POST | `/connectors/case-management/mock/record-note` | Record note |
| POST | `/connectors/case-management/mock/update-sla` | Update SLA |
| POST | `/connectors/case-management/mock/create-escalation` | Create escalation |
| POST | `/connectors/case-management/mock/close-case` | Close case |

## Materials

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/openapi.json` | OpenAPI specification |
| GET | `/materials/api-guide` | API guide |
| GET | `/materials/integration-map` | Integration map |
| GET | `/materials/security-one-pager` | Security overview |
