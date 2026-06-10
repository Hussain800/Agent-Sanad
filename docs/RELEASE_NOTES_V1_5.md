# Agent Sanad v1.5 Release Notes

## Overview

v1.5 is the assurance release. It closes the gaps between a mocked production surface and a controlled pilot-candidate platform.

## What's New

### Trust Controls
- **Consent Guard v2**: Purpose, scope, expiry, revocation, and beneficiary ownership enforcement for all sensitive connector calls. Denied access attempts are audited.
- **UAE PASS Session v3**: Stored nonce, expiry, consumed callback, replay rejection, wrong nonce rejection, reused code rejection.
- **ABAC Ownership**: Object-level authorization for cases, consents, actions, applications, packages, appeals, notifications, and privacy export.
- **Signature Integrity v2**: Package hash binding, tamper detection, signature expiry, revocation — tampered packages fail verification.

### Connectors
- **7th Connector**: Case-management (assign officer, schedule callback, record note, update SLA, create escalation, close case).
- **Typed Pydantic Schemas**: All connector routes use Pydantic request/response models.

### Workflows
- **Action Workflow v4**: upload-mock, reject, resubmit, waive, complete with owner enforcement, timeline, notifications, and audit events.
- **Appeals Workbench**: Create, list, submit evidence, review, decision, supervisor approval.
- **Case Assignment & SLA**: Officer assignment, SLA tracking, service-centre callback scheduling.

### Supervisor Command Center
- Backlog view, SLA risk board, fairness slices, connector incidents, officer workload, override review, consent denial rate, document trust failure rate.

### Frontend
- Accessibility improvements: skip-to-content link, visible focus states, keyboard navigation, high-contrast mode.
- 45 new Arabic i18n keys for all v1.5 visible text.

### API & Materials
- OpenAPI JSON (`docs/api/openapi.json`)
- Postman collection (`docs/POSTMAN_COLLECTION.json`)
- API guide, integration map, security one-pager at `/materials/*`

### Testing
- 224 passing tests across 20 test files
- New test files: consent_guard, sessions, abac, signature_integrity, action_workflow, appeals, supervisor_command, connector_contracts

### Version
- Backend `APP_VERSION`: 1.5.0
- Frontend `CLIENT_BUILD`: 1.5.0
- `scripts/release-check.ps1` updated with 17 automated gates

## Known Limitations
- All connectors remain mock (contract-shaped, fixture-backed)
- No real UAE PASS, GSB, or Emirates ID integration
- LangGraph is optional and import-guarded
- Policy engine unchanged from v1.4
