# Agent Sanad v1.5 Winning PRD

Purpose: take the completed v1.4 production-shaped mock platform and turn it into a pilot-assurance release. v1.4 proved mocked connectors, consent, RBAC, audit chain, simulator, and digital closeout. v1.5 must now make those controls deeper, more believable, more usable, and more complete as a UAE public-service product.

Core doctrine remains unchanged:

> LLM reads and explains. Deterministic code decides. Human owns the exception.

## 1. Summary

Agent Sanad v1.5 is the assurance release. It closes the gaps between "we have a mocked production surface" and "a ministry team could evaluate this as a controlled pilot candidate."

The release focuses on trust: strong purpose enforcement, case ownership, replay protection, document intelligence, fairness review, accessibility, service-level operations, richer supervisor tools, complete demo materials, and clean docs that match the actual product.

## 2. Current Review

Latest reviewed branch: `main`.

Latest reviewed commit: `e471dc5`.

Local branch state: `main` is aligned with `origin/main`.

Verification:

- Full test suite passes: `168 passed, 1 warning`.
- `scripts/release-check.ps1` passes: `8 passed, 0 failed`.
- Runtime version is `1.4.0`.
- v1.4 backend modules exist: connectors, consent, RBAC, audit chain, simulator, decision package, security.
- v1.4 frontend additions exist: consent screen, connector health panel, supervisor metrics.

## 3. v1.4 Completed

v1.4 successfully added:

- Connector registry and health/simulate/reset endpoints.
- Six mocked connectors: UAE PASS, GSB, SZHP core, UAE Verify, financial capacity, notifications.
- Consent create/get/revoke/events.
- RBAC by `x-sanad-role`.
- SHA256 audit chain.
- Durable repair-action endpoints.
- Fair Plan Simulator endpoints.
- Decision packages, mock signatures, e-Seal-shaped closeout.
- Supervisor metrics, overrides, connector health, policy drift.
- Security middleware for correlation ID, rate limiting, security headers, and request-size limits.
- SQLite tables for v1.4 state.
- `APP_VERSION` and `CLIENT_BUILD` bumped to `1.4.0`.
- Release-check script.
- 168 passing tests.

## 4. Must-Fix Gaps

These are not failures of v1.4. They are the natural v1.5 hardening list.

### G1. Docs and Release Metadata Drift

The README still advertises 125 tests and 9 test files in multiple places. The release script still labels its test gate `139+`. AGENTS.md describes 168 tests, but some old sections still mention 125.

v1.5 must make all public-facing docs and release scripts consistent with actual v1.5 state.

### G2. Consent Is Present but Not Deep Enough

The GSB connector requires consent, but consent validation does not yet enforce:

- purpose-code match
- connector scope match
- expiry
- beneficiary ownership
- revoked state across all connector routes
- audit event for denied access

v1.5 must make consent purpose-bound, scoped, expiring, auditable, and ownership-aware.

### G3. UAE PASS Session Is Too Thin

The mock session exists, but callback replay protection is not credible enough. Session nonce is generated, but there is no full stateful lifecycle with consumed nonce, expiry, callback attempts, subject binding, and consent binding.

v1.5 must make the UAE PASS mock behave like a real auth control surface.

### G4. RBAC Is Not True ABAC

Role checks exist, but beneficiary ownership is not consistently enforced. A beneficiary should not be able to fetch or mutate another beneficiary's case, consent, task, notification, or decision package.

v1.5 must add user ownership and object-level access checks.

### G5. Signature Verification Is Too Optimistic

Mock signature verification currently returns valid for arbitrary signature/hash pairs. v1.5 must bind signatures to package IDs and package hashes, and fail when the package changes.

### G6. Connector Count and Contracts Are Incomplete

v1.4 has six connectors. v1.4 PRD asked for at least seven. v1.5 should add the missing service-centre/case-management connector and turn all connector payloads into Pydantic models instead of raw `dict` bodies.

### G7. Repair Actions Are Durable but Not Productized

Repair action endpoints exist, but the workflow lacks full state transition rules, upload-mock implementation, action owner enforcement, SLA, notification triggers, and Arabic task lifecycle copy.

### G8. Appeals Exist as a Stub Surface

Appeals need a real review queue, required evidence, supervisor approval for sensitive reversals, and clear beneficiary-facing status.

### G9. Supervisor Dashboard Is Too Thin

Current metrics are useful, but not yet a command center. v1.5 should add SLA risk, backlog, connector incidents, fairness indicators, override heatmap, and policy drift review.

### G10. Accessibility and Arabic-First QA Are Missing

Arabic keys exist, but v1.5 needs a real accessibility and RTL verification pass: keyboard navigation, focus states, contrast, screen-reader labels, Arabic layout checks, and no text overflow.

### G11. API-First Materials Are Incomplete

OpenAPI exists implicitly through FastAPI, but v1.5 needs generated artifacts:

- OpenAPI JSON
- Postman collection
- API one-pager
- connector contract samples
- SDK snippets
- event catalog
- data dictionary

### G12. Pilot Operations Are Not Fully Modeled

v1.5 must add incident states, SLA clocks, case assignment, service-centre callbacks, notifications, escalation, support audit, and release evidence.

## 5. Background

The UAE digital-government direction rewards systems that are API-first, accessible, secure, auditable, and trusted by citizens. v1.5 should align the product with that direction.

Official source alignment:

- [UAE PASS documentation](https://docs.uaepass.ae/) supports identity, authentication, and signature-service framing.
- [TDRA Government Service Bus](https://tdra.gov.ae/en/Services/government-service-bus-gsb) supports integrated data exchange between government entities.
- [UAE API First Policy](https://uaelegislation.gov.ae/en/policy/details/api-first-policy) supports contract-first public services.
- [UAE Digital Government Strategy 2025](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/strategies-plans-and-visions/government-services-and-digital-transformation/uae-national-digital-government-strategy) supports cross-sector digital-government commitment.
- [UAE Charter for AI](https://uaelegislation.gov.ae/en/policy/details/the-uae-charter-for-the-development-and-use-of-artificial-intelligence) supports lawful, responsible AI use.
- [UAE data protection guidance](https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws) supports confidentiality and privacy controls.
- [National Digital Accessibility Policy](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/policies/government-services-and-digital-transformation/national-digital-accessibility-policy) supports accessible digital services.
- [UAE Verify](https://tdra.gov.ae/en/media/press-release/2022/tdra-launches-the-uae-verify-platform) supports document authenticity verification.

## 6. Objective

Make Agent Sanad v1.5 feel like the audited pilot packet a government team would want before approving a sandbox trial.

Key outcomes:

- Every data access is consented, scoped, owned, and auditable.
- Every case has a lifecycle, SLA, owner, and escalation path.
- Every connector has typed contracts, failures, and recovery states.
- Every decision package can be verified or rejected correctly.
- Every visible flow is Arabic-ready and accessible.
- Every material needed for judging, security review, and technical handoff is included.

## 7. Key Results

| KR | Target |
|---|---|
| Tests | 220+ passing tests |
| Version | Backend `APP_VERSION` and frontend `CLIENT_BUILD` are `1.5.0` |
| Consent | 100% of sensitive connector calls enforce purpose, scope, expiry, owner, revoked state |
| ABAC | Beneficiary object ownership enforced across cases, consents, actions, packages, appeals |
| UAE PASS | Callback replay, expired nonce, wrong nonce, and reused code all fail |
| Signature | Modified package, wrong package hash, wrong signature ID, and expired signature all fail |
| Connectors | At least 7 connectors with Pydantic request/response models and contract tests |
| Actions | Repair action upload, complete, reject, waive, and resubmit flows tested |
| Appeals | Appeals have create/list/review/decision/supervisor approval flow |
| Accessibility | Automated and manual checklist stored in docs |
| API materials | OpenAPI JSON, Postman collection, API guide, data dictionary, event catalog generated |
| Release | v1.5 release-check passes all gates |

## 8. Market Segments

### Beneficiary

Needs confidence, privacy, Arabic-first clarity, accessible service, status updates, and a way to repair or appeal.

### Officer

Needs queue ownership, complete evidence, task status, safe overrides, callbacks, and SLA risk indicators.

### Supervisor

Needs workload, fairness, override, policy drift, connector reliability, and case-aging intelligence.

### Auditor

Needs hash-chain integrity, consent evidence, access logs, decision package verification, and exportable review material.

### Integration Team

Needs typed contracts, OpenAPI, connector examples, failure modes, release checks, and deployment assumptions.

## 9. Value Propositions

### Beneficiary Value

- Fewer unclear statuses.
- No repeated document chasing.
- More privacy control.
- Clear appeal path.
- Accessible Arabic-first experience.
- Digitally verifiable outcome.

### Officer Value

- Fewer blind spots.
- Faster exception triage.
- Clear service-level risk.
- Stronger override governance.
- Better connector failure recovery.

### Government Value

- Stronger pilot readiness.
- Better legal and audit posture.
- Better API-first story.
- Better trust and accessibility story.
- Better evidence that the AI is bounded and safe.

## 10. Solution

### 10.1 Consent and Purpose Engine v2

Add a real consent guard.

Backend:

- `backend/consent_guard.py`
- `backend/purpose.py`

Routes:

- `POST /consents/{id}/validate`
- `GET /consents/{id}/usage`
- `GET /privacy/export/{beneficiary_ref}`

Rules:

- purpose must match
- connector scope must match
- expiry must not pass
- revoked consent fails
- user must own the consent unless officer/supervisor/auditor/admin role allows access
- denied attempts create audit-chain events
- connector calls record `consent_decision`

Tests:

- wrong purpose denied
- missing scope denied
- expired consent denied
- revoked consent denied
- wrong owner denied
- admin access allowed
- denied attempts audited

### 10.2 UAE PASS Session v3

Make the mock auth session stateful.

Data fields:

- session id
- nonce
- auth code hash
- state
- attempts
- expires at
- consumed at
- subject ref
- consent id
- assurance level

Failure cases:

- missing session
- wrong nonce
- expired session
- replayed callback
- reused code
- callback after consumed

Frontend:

- show session state
- show expiry countdown
- show clear recovery when callback fails

### 10.3 ABAC and Case Ownership

Add object-level authorization.

Rules:

- beneficiary sees only own cases and own consents
- beneficiary mutates only own actions
- officer sees assigned queue
- supervisor sees all queue plus metrics
- auditor sees immutable records only
- admin can configure mocks but cannot silently alter decisions

Routes to protect:

- cases
- consents
- actions
- applications
- decision packages
- appeals
- notifications
- privacy export

### 10.4 Signature and Decision Package v2

Bind signature to package and hash.

Add:

- package version
- package status
- package hash
- signed hash
- signature expiry
- verified at
- verifier reference
- e-Seal reference

Routes:

- `POST /decision-packages/{package_id}/verify`
- `GET /decision-packages/{package_id}/receipt`
- `POST /decision-packages/{package_id}/revoke-mock`

Failure cases:

- hash mismatch
- signature unknown
- signature expired
- package revoked
- wrong signatory

### 10.5 Connector Contracts v2

Add typed schemas for every connector.

Modules:

- `backend/connector_schemas.py`
- `backend/connectors_case_management.py`

Add seventh connector:

- `case-management`

Services:

- assign officer
- schedule callback
- record service-centre note
- update SLA
- create escalation
- close case

All connectors must include:

- request model
- response model
- health model
- failure-mode model
- contract tests
- audit/call logging
- consent policy

### 10.6 Repair Action Workflow v4

Make repair tasks a real workflow.

States:

- open
- uploaded
- submitted
- accepted
- rejected
- resubmission_requested
- waived
- expired
- closed

Routes:

- `POST /cases/{case_id}/actions/{action_id}/upload-mock`
- `POST /cases/{case_id}/actions/{action_id}/reject`
- `POST /cases/{case_id}/actions/{action_id}/resubmit`
- `GET /cases/{case_id}/actions/timeline`

Rules:

- only owner can upload
- officer can accept/reject/waive
- supervisor can waive high-risk items
- action completion can trigger re-decision
- status changes emit notifications and audit-chain events

### 10.7 Appeals Workbench

Implement a complete appeal lifecycle.

Routes:

- `POST /cases/{case_id}/appeals`
- `GET /cases/{case_id}/appeals`
- `GET /appeals`
- `GET /appeals/{appeal_id}`
- `POST /appeals/{appeal_id}/submit-evidence`
- `POST /appeals/{appeal_id}/review`
- `POST /appeals/{appeal_id}/decision`
- `POST /appeals/{appeal_id}/supervisor-approve`

States:

- draft
- submitted
- evidence_needed
- officer_review
- supervisor_review
- upheld
- reversed
- closed

### 10.8 Supervisor Command Center v2

Add a real operating view.

Metrics:

- backlog by status
- oldest case age
- SLA at risk
- repair-loop completion rate
- appeal volume
- reversal rate
- override rate by officer
- connector failure rate
- consent denial rate
- document trust failure rate
- policy drift score
- fairness slices

Routes:

- `GET /supervisor/backlog`
- `GET /supervisor/sla-risk`
- `GET /supervisor/fairness`
- `GET /supervisor/connectors/incidents`
- `GET /supervisor/officer-workload`

### 10.9 Fairness and Responsible AI Evidence Pack

Because the product uses AI explanation around deterministic decisions, v1.5 must include a responsible AI evidence pack.

Artifacts:

- `docs/RESPONSIBLE_AI.md`
- `docs/FAIRNESS_REVIEW.md`
- `docs/MODEL_CARD.md`
- `docs/HUMAN_OVERSIGHT.md`

Include:

- decision boundary
- no LLM decisioning
- policy engine ownership
- fairness slices from synthetic data
- confidence bands
- human override governance
- known limitations
- out-of-scope uses

### 10.10 Accessibility and Arabic QA

Add accessibility checklist and fixes.

Frontend must support:

- keyboard navigation
- visible focus states
- accessible labels
- skip-to-content link
- sufficient contrast
- no text overflow
- RTL layout sanity
- Arabic task and appeal copy
- print-friendly decision package

Artifacts:

- `docs/ACCESSIBILITY_QA.md`
- screenshot checklist
- Arabic glossary

### 10.11 API and Handoff Materials

Generate:

- `docs/api/openapi.json`
- `docs/API_GUIDE.md`
- `docs/CONNECTOR_CONTRACTS.md`
- `docs/DATA_DICTIONARY.md`
- `docs/EVENT_CATALOG.md`
- `docs/POSTMAN_COLLECTION.json`
- `docs/SECURITY_ONE_PAGER.md`
- `docs/UAE_INTEGRATION_MAP.md`
- `docs/PILOT_RUNBOOK.md`
- `docs/INCIDENT_PLAYBOOK.md`
- `docs/RELEASE_NOTES_V1_5.md`

Update:

- README
- AGENTS.md
- ARCHITECTURE.md
- PRODUCTION_READINESS.md
- JUDGE_QA.md
- DEMO_SCRIPTS.md
- SCREENSHOTS.md

### 10.12 Release Check v1.5

Update `scripts/release-check.ps1`.

Checks:

- version equals 1.5.0
- tests pass
- test count at least 220
- no workbook tracked
- no PII patterns
- OpenAPI generated
- Postman generated
- connector contract tests pass
- consent guard tests pass
- ABAC tests pass
- audit chain tests pass
- signature tamper tests pass
- Arabic keys coverage passes
- docs version references are current
- release notes exist

## 11. API Surface

### Consent and Privacy

- `POST /consents/{id}/validate`
- `GET /consents/{id}/usage`
- `GET /privacy/export/{beneficiary_ref}`

### Sessions

- `GET /sessions/{id}`
- `POST /sessions/{id}/expire-mock`
- `POST /sessions/{id}/revoke-mock`

### Actions

- `POST /cases/{case_id}/actions/{action_id}/upload-mock`
- `POST /cases/{case_id}/actions/{action_id}/reject`
- `POST /cases/{case_id}/actions/{action_id}/resubmit`
- `GET /cases/{case_id}/actions/timeline`

### Appeals

- `POST /cases/{case_id}/appeals`
- `GET /cases/{case_id}/appeals`
- `GET /appeals`
- `GET /appeals/{appeal_id}`
- `POST /appeals/{appeal_id}/submit-evidence`
- `POST /appeals/{appeal_id}/review`
- `POST /appeals/{appeal_id}/decision`
- `POST /appeals/{appeal_id}/supervisor-approve`

### Decision Packages

- `POST /decision-packages/{package_id}/verify`
- `GET /decision-packages/{package_id}/receipt`
- `POST /decision-packages/{package_id}/revoke-mock`

### Supervisor

- `GET /supervisor/backlog`
- `GET /supervisor/sla-risk`
- `GET /supervisor/fairness`
- `GET /supervisor/connectors/incidents`
- `GET /supervisor/officer-workload`

### Materials

- `GET /openapi.json`
- `GET /materials/api-guide`
- `GET /materials/integration-map`
- `GET /materials/security-one-pager`

## 12. Data Model Additions

Add or extend tables:

- `consent_usage`
- `access_decisions`
- `session_events`
- `case_assignments`
- `case_sla`
- `action_events`
- `appeals`
- `appeal_events`
- `notification_events`
- `connector_contract_runs`
- `fairness_slices`
- `material_exports`

## 13. UX Requirements

### Beneficiary

- service cockpit with status timeline
- consent review and revoke
- repair task lifecycle
- appeal submission
- decision package verification
- notification preferences
- Arabic-first copy
- accessibility-friendly controls

### Officer

- assigned queue
- action review
- appeal review
- callback scheduling
- connector incident indicators
- plan simulator with official/recommended separation
- override reason enforcement

### Supervisor

- backlog board
- SLA risk board
- fairness review
- connector incident console
- officer workload
- override review
- policy drift review

### Auditor

- audit-chain verification
- consent usage report
- package verification
- access log export
- responsible AI evidence pack

### Admin

- connector simulator
- failure modes
- material generation
- release-check status

## 14. Testing Plan

Target: 220+ tests.

Add:

- `tests/test_consent_guard.py`
- `tests/test_sessions.py`
- `tests/test_abac.py`
- `tests/test_signature_integrity.py`
- `tests/test_action_workflow.py`
- `tests/test_appeals.py`
- `tests/test_supervisor_command.py`
- `tests/test_materials.py`
- `tests/test_accessibility_i18n.py`
- `tests/test_connector_contracts.py`

Must test:

- consent purpose mismatch denied
- consent scope mismatch denied
- expired consent denied
- revoked consent denied
- wrong owner denied
- denied access audited
- callback replay denied
- wrong nonce denied
- expired UAE PASS session denied
- reused auth code denied
- signature hash mismatch denied
- package revoke blocks verification
- beneficiary cannot access another case
- action owner rules
- action upload/reject/resubmit/waive lifecycle
- appeal create/review/decision/supervisor approval
- supervisor metrics reflect seeded events
- connector contracts validate request/response models
- OpenAPI and Postman artifacts generated
- Arabic keys cover all new visible labels
- README and release scripts mention current test count

## 15. Release Plan

### Phase 1: Hygiene and Version

- bump to `1.5.0`
- update README, AGENTS.md, release script labels
- add docs consistency test
- generate first v1.5 release notes

Exit: no stale v1.4 or 125-test public claims except historical docs.

### Phase 2: Trust Controls

- consent guard v2
- UAE PASS session v3
- ABAC ownership
- signature integrity

Exit: trust-control tests pass.

### Phase 3: Workflow Depth

- action workflow v4
- appeals workbench
- case assignment and SLA
- notifications linked to state changes

Exit: beneficiary/officer flows are complete.

### Phase 4: Command Center

- supervisor backlog
- SLA risk
- fairness slices
- connector incidents
- officer workload

Exit: supervisor can run the service from the dashboard.

### Phase 5: Materials and QA

- API guide
- connector contracts
- data dictionary
- event catalog
- security one-pager
- responsible AI pack
- accessibility QA
- pilot runbook
- incident playbook
- screenshots

Exit: full judging and pilot packet complete.

## 16. Acceptance Criteria

v1.5 is complete when:

- local `main` is aligned with `origin/main`
- full suite passes with 220+ tests
- release-check v1.5 passes
- version is `1.5.0` in backend and frontend
- docs are current
- consent guard enforces purpose, scope, expiry, revocation, and ownership
- UAE PASS replay and expiry tests pass
- ABAC ownership tests pass
- signature tamper tests pass
- seventh connector exists
- all connector contracts have typed models
- actions and appeals are real workflows
- supervisor command center has backlog, SLA, fairness, connector incidents, workload
- accessibility QA doc exists
- responsible AI pack exists
- API and pilot materials exist
- no real PII or workbook is tracked

## 17. Non-Goals

- real UAE PASS credentials
- real GSB access
- real credit bureau access
- real production secrets
- policy-engine changes unless explicitly approved
- runtime policy editing
- LLM decisioning on eligibility, money, compliance, or officer action

## 18. Winning Narrative

v1.4 says: we can plug into a UAE-style digital-government ecosystem.

v1.5 says: we can be trusted inside it.

The final pitch:

Agent Sanad is a governed public-service operating system for arrears rescheduling. It proves identity, consent, evidence, policy, human oversight, accessibility, audit integrity, and operational readiness without ever letting the LLM decide the money.

