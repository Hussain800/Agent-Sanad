# Agent Sanad v1.6 Winning PRD

Purpose: take the v1.5 pilot-assurance release and turn it into a certification-ready, operations-ready, judge-proof public-service product. v1.5 added the trust controls. v1.6 must now make the whole system coherent: contract-first APIs, one case lifecycle, real workflow governance, stronger evidence lineage, deeper Arabic/accessibility quality, audit exports, release provenance, and pilot packaging.

Core doctrine remains unchanged:

> LLM reads and explains. Deterministic code decides. Human owns the exception.

## 1. Summary

Agent Sanad v1.6 is the "pilot command" release. It should feel like a complete sandbox package that a UAE government digital team, service owner, auditor, security reviewer, and hackathon judge can all inspect without finding obvious gaps.

The release is not about adding a flashy surface. It is about making the current surfaces trustworthy, typed, testable, explainable, accessible, exportable, and operational.

## 2. Current Review

Latest reviewed branch: `main`.

Latest reviewed commit: `53da1f2`.

Local branch state: `main` is aligned with `origin/main`.

Working tree note: after the v1.5 release merge, the only local untracked file at review time is this v1.6 PRD.

Verification:

- Full test suite passes: `231 passed, 2 warnings`.
- `scripts/release-check.ps1` passes: `17 passed, 0 failed`.
- Runtime version is `1.5.0`.
- v1.5 modules exist: `backend/consent_guard.py`, `backend/uaepass_session.py`, `backend/abac.py`, `backend/routes_v1_5.py`.
- v1.5 materials exist: responsible AI, fairness review, model card, human oversight, accessibility QA, API guide, connector contracts, data dictionary, event catalog, pilot runbook, incident playbook, OpenAPI JSON, Postman collection, release notes.

## 3. v1.5 Completed

v1.5 successfully added:

- Consent guard v2.
- UAE PASS session v3.
- ABAC ownership layer.
- Signature integrity tests.
- Seventh connector: case-management.
- Action workflow v4 endpoints.
- Appeals workbench.
- Supervisor command center endpoints.
- OpenAPI and Postman artifacts.
- Responsible AI and pilot-readiness materials.
- README and release materials updated to v1.5.
- Release check expanded to 17 gates.
- 231 passing tests.

## 4. Must-Fix Gaps

### G1. v1.5 Release Hygiene

The repo is on latest `main` and v1.5 is merged. v1.6 should start by preserving that clean baseline, then updating versioned docs, release metadata, and generated artifacts in one coherent release branch.

### G2. Test Warning

`tests/test_appeals.py::test_appeal_create` returns an integer instead of returning `None`, causing `PytestReturnNotNoneWarning`.

v1.6 must remove all warnings from the full suite.

### G3. Decision Package Version Drift

`backend/decision_package.py` still embeds `"app_version": "1.4.0"` inside generated package summaries, even though runtime version is `1.5.0`.

v1.6 must remove hardcoded release values from package generation.

### G4. Contract-First Claim Is Not Fully True

v1.5 adds Pydantic classes inside `routes_v1_5.py`, but many routes still accept raw `dict` bodies and do not use request/response models. The docs say connectors are typed. The implementation is only partly typed.

v1.6 must make contracts real.

### G5. ABAC Defaults Are Too Permissive

Some ownership checks gracefully allow access when ownership cannot be established. That is demo-friendly but not pilot-assurance strong.

v1.6 must move from permissive fallback to explicit allow/deny by route and role.

### G6. One Case Lifecycle Is Missing

The app now has actions, appeals, assignments, SLA, packages, and supervisor views, but there is no single case-lifecycle state machine that governs allowed transitions.

v1.6 must add one canonical lifecycle.

### G7. Workflow Logic Is Spread Across Routes

Action and appeal state updates are direct SQL inside route handlers. This is hard to audit and hard to test as the product grows.

v1.6 must move workflow rules into service modules.

### G8. Evidence Lineage Is Still Shallow

Connector calls, audit-chain events, action events, document checks, and decision packages exist, but there is no single evidence graph that shows exactly which facts fed a recommendation or package.

v1.6 must add an evidence graph and export.

### G9. Materials Exist, But Are Mostly Static

Docs and artifacts exist. v1.6 must make them generated or checked where possible, so the product cannot drift silently.

### G10. Frontend v1.5 Is Thin

The backend grew substantially. The frontend has selected v1.5 panels, but not a fully integrated beneficiary/officer/supervisor/admin/auditor experience for all new v1.5 controls.

v1.6 must expose the trust and operations story in the UI.

## 5. Background

v1.6 should align the product with official UAE digital government expectations:

- [UAE PASS](https://docs.uaepass.ae/) supports the national identity and signature story.
- [TDRA UAE PASS service page](https://dgov.tdra.gov.ae/en/services/uae-pass) frames UAE PASS as secure national digital identity.
- [TDRA Government Service Bus](https://tdra.gov.ae/en/Services/government-service-bus-gsb) supports integrated government data exchange.
- [UAE API First Policy](https://uaelegislation.gov.ae/en/policy/details/api-first-policy) supports API-first public services.
- [UAE Digital Government Strategy 2025](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/strategies-plans-and-visions/government-services-and-digital-transformation/uae-national-digital-government-strategy) supports cross-sector digital-government commitment.
- [UAE Charter for AI](https://uaelegislation.gov.ae/en/policy/details/the-uae-charter-for-the-development-and-use-of-artificial-intelligence) supports responsible AI governance.
- [National Digital Accessibility Policy](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/policies/government-services-and-digital-transformation/national-digital-accessibility-policy) supports accessible public digital services.
- [UAE Verify](https://tdra.gov.ae/en/media/press-release/2022/tdra-launches-the-uae-verify-platform) supports document authenticity checks.
- [TDRA Digital Enablers Report](https://tdra.gov.ae/en/media/press-release/2023/tdra-releases-the-digital-enablers-report-2023) shows the scale of UAE PASS, UAE Verify, API Marketplace, GSB, and Tawasul 171-style service operations.

## 6. Objective

Make Agent Sanad v1.6 a complete pilot command package.

It should answer:

- Can we trust the implementation, not just the story?
- Can we prove every API contract?
- Can we trace every fact, task, appeal, package, and signature?
- Can a beneficiary use it accessibly in Arabic?
- Can an officer operate it all day?
- Can a supervisor govern service quality?
- Can an auditor export evidence without asking engineering?
- Can a technical team run a release without tribal knowledge?

## 7. Key Results

| KR | Target |
|---|---|
| Version | Backend `APP_VERSION` and frontend `CLIENT_BUILD` are `1.6.0` |
| Tests | 280+ passing tests, 0 warnings |
| Release | `scripts/release-check.ps1` has 25+ gates and passes |
| Contracts | All v1.4-v1.6 public routes use Pydantic request/response models where applicable |
| OpenAPI | OpenAPI, Postman, API guide, and connector samples are generated from the same source |
| Lifecycle | One case state machine governs actions, appeals, assignments, SLA, packages, and closeout |
| Evidence | Every recommendation has an evidence graph export |
| ABAC | Unknown ownership denies by default for sensitive objects |
| UI | Beneficiary, officer, supervisor, auditor, and admin workspaces expose v1.5/v1.6 controls |
| Accessibility | Accessibility checks and RTL checks pass with documented screenshots |
| Security | Threat model, abuse cases, and security tests cover all trust controls |
| Materials | Pilot packet is complete and release-checked |

## 8. Market Segments

### Beneficiary

Needs a simple, accessible, Arabic-first service that explains status, evidence, appeals, consent, and final outcome.

### Officer

Needs an efficient workbench with assigned cases, repair tasks, appeals, callbacks, plan simulation, evidence graph, and safe action controls.

### Supervisor

Needs command views: backlog, SLA risk, fairness, connector incidents, officer workload, overrides, appeals, and policy drift.

### Auditor

Needs exportable evidence: consent usage, access decisions, audit-chain verification, package integrity, appeal history, and model governance.

### Integration Team

Needs typed contracts, OpenAPI, Postman, data dictionary, event catalog, migration story, release gates, and mock connector behavior that is stable.

### Judge

Needs a crisp product story: not a chatbot, not a spreadsheet, but a governed service workflow ready for a sandbox pilot.

## 9. Value Propositions

### Beneficiary Value

- Trust the service status.
- See what is needed and why.
- Repair evidence without confusion.
- Appeal with a clear path.
- Verify the final package.
- Use the product in Arabic with accessible controls.

### Officer Value

- One queue, one lifecycle, one source of truth.
- Fewer ad hoc decisions.
- Fewer repeated checks.
- Better evidence visibility.
- Safer overrides and appeals.

### Government Value

- API-first and audit-first.
- Stronger AI governance posture.
- Better accessibility posture.
- Better release evidence.
- Better path from hackathon to controlled pilot.

## 10. Solution

### 10.1 v1.5 Stabilization

First actions:

- Fix pytest warning in `tests/test_appeals.py`.
- Replace hardcoded `"1.4.0"` in decision package summary with runtime app version or a passed-in version.
- Update AGENTS.md stale endpoint/test sections to match v1.5/v1.6 reality.
- Start from the v1.5 release merge commit and create a v1.6 implementation branch if a branch is needed.
- Add a docs drift test that fails on stale release strings in active docs.

### 10.2 Contract-First API Layer

Add `backend/api_models.py`.

Move all route payloads from raw `dict` to typed models:

- consent validation
- UAE PASS session start/callback
- action upload/reject/resubmit/waive
- appeals create/evidence/review/decision/supervisor approval
- decision package verification
- connector simulator
- case-management connector
- notification connector
- supervisor filters
- materials routes

Every public route should have:

- request model, if it has a body
- response model
- example payload
- error shape
- OpenAPI tag
- contract test

### 10.3 Route Organization

Split `backend/app.py` and `backend/routes_v1_5.py` into route modules:

- `backend/routes/core.py`
- `backend/routes/connectors.py`
- `backend/routes/consents.py`
- `backend/routes/sessions.py`
- `backend/routes/actions.py`
- `backend/routes/appeals.py`
- `backend/routes/supervisor.py`
- `backend/routes/materials.py`
- `backend/routes/packages.py`

Keep `backend/app.py` as the composition root.

### 10.4 Case Lifecycle Engine

Add `backend/case_lifecycle.py`.

States:

- submitted
- identity_verified
- consent_granted
- data_retrieved
- evidence_needed
- evidence_submitted
- policy_ready
- recommendation_ready
- officer_review
- beneficiary_repair
- appeal_draft
- appeal_submitted
- appeal_review
- supervisor_review
- approved
- adjusted
- rejected
- referred
- signed
- sealed
- closed

Rules:

- invalid transitions fail
- every transition emits audit-chain event
- every transition updates SLA
- every transition can trigger notification
- transitions are idempotent when safe

Routes:

- `GET /cases/{case_id}/lifecycle`
- `POST /cases/{case_id}/lifecycle/transition`
- `GET /cases/{case_id}/timeline`

### 10.5 Workflow Services

Move business rules out of route handlers.

Add:

- `backend/services/action_service.py`
- `backend/services/appeal_service.py`
- `backend/services/package_service.py`
- `backend/services/supervisor_service.py`
- `backend/services/materials_service.py`

Rules:

- routes parse and authorize
- services enforce workflow
- store persists
- audit chain records
- tests target services and endpoints

### 10.6 Evidence Graph

Add `backend/evidence_graph.py`.

Evidence nodes:

- consent
- connector call
- fixture source
- salary certificate extraction
- document trust check
- policy rule
- proposed plan field
- repair action
- appeal evidence
- officer action
- decision package
- signature
- e-Seal

Routes:

- `GET /cases/{case_id}/evidence-graph`
- `GET /cases/{case_id}/evidence-graph/export`
- `GET /decision-packages/{package_id}/evidence-graph`

Formats:

- JSON graph
- Mermaid diagram text
- compact auditor summary

### 10.7 Audit Export and Verification Packet

Add auditor export.

Routes:

- `GET /audit/export/{case_id}`
- `GET /audit/export/{case_id}/zip-manifest`
- `POST /audit/export/{case_id}/verify`

Export includes:

- audit chain
- access decisions
- consent usage
- connector calls
- evidence graph
- recommendation
- officer actions
- appeals
- package verification
- policy version
- app version

No raw PII or raw document text.

### 10.8 ABAC v2

Change sensitive-object behavior:

- unknown ownership denies by default
- shared sample cases have explicit public-demo ownership policy
- officer assignment controls officer access
- auditor access is read-only
- admin configuration does not imply decision override

Add:

- `access_decisions` table records allow/deny
- `GET /access-decisions/{case_id}`
- tests for unknown object denial
- tests for auditor write denial
- tests for officer unassigned denial

### 10.9 UAE PASS and Signature v4

Improve session and signature model:

- store subject ref
- bind subject ref to consent
- bind consent to session
- store auth code hash separately from nonce
- add callback attempt count
- deny revoked sessions in callback
- deny consumed sessions before nonce validation
- signature request binds to package id and package hash
- signature verification checks signature status, package hash, signatory, expiry, revoked state

### 10.10 Connector Reliability Lab

Upgrade connector simulator:

- latency injection
- timeout
- stale data
- partial data
- schema mismatch
- consent denied
- provider down
- retry success after failure
- circuit breaker mock
- incident creation

Routes:

- `POST /connectors/{name}/failure-profile`
- `GET /connectors/{name}/incidents`
- `POST /connectors/{name}/retry`
- `POST /connectors/{name}/circuit-breaker/reset`

UI:

- admin reliability lab
- supervisor incident board
- officer case-level connector status

### 10.11 Arabic and Accessibility Excellence

Add serious UX QA:

- skip links
- focus traps for modals
- keyboard shortcuts for officer queue
- aria labels for icon buttons
- form error summaries
- print styles for decision package
- RTL screenshots checklist
- Arabic glossary surfaced in UI
- text overflow test for key screens
- no hidden English strings in Arabic mode

Routes/materials:

- `GET /materials/accessibility-report`
- `GET /materials/arabic-glossary`

### 10.12 Fairness and Policy Analytics v2

Current fairness slices are basic. Add:

- synthetic cohort generator
- segment comparison
- false positive/false negative analysis for request-docs/refer/reject
- override disparity view
- appeal reversal by segment
- confidence distribution
- policy drift snapshots

Routes:

- `POST /fairness/synthetic-cohort/generate`
- `GET /fairness/slices`
- `GET /fairness/appeals`
- `GET /fairness/overrides`
- `GET /fairness/report`

Important: fairness analysis does not alter policy decisions.

### 10.13 Reasoning Quality and LLM Safety Evaluation

Even though the LLM never decides, explanation quality matters.

Add:

- golden reasoning snapshots
- Arabic explanation snapshots
- prompt-injection explanation tests
- hallucination guard tests
- citation/evidence-reference checks
- "no new facts in reasoning" test

Docs:

- `docs/REASONING_EVALS.md`
- `docs/LLM_SAFETY_CASE.md`

### 10.14 Pilot Operations Pack v2

Upgrade pilot materials:

- sandbox onboarding checklist
- connector onboarding checklist
- data-processing assumptions
- DPIA-style privacy checklist
- support playbook
- service-centre script
- training guide for officers
- supervisor daily operating routine
- auditor review procedure
- rollback plan
- release provenance page

Docs:

- `docs/SANDBOX_ONBOARDING.md`
- `docs/OFFICER_TRAINING_GUIDE.md`
- `docs/SUPERVISOR_OPERATING_ROUTINE.md`
- `docs/AUDITOR_REVIEW_PROCEDURE.md`
- `docs/PRIVACY_IMPACT_CHECKLIST.md`
- `docs/ROLLBACK_PLAN.md`
- `docs/RELEASE_PROVENANCE.md`

### 10.15 Demo and Judging Pack v2

Add polished materials:

- 60-second product pitch
- 90-second judge path
- 3-minute technical proof
- 5-minute pilot-readiness story
- 7-minute security/audit story
- failure-mode script
- Arabic beneficiary walkthrough
- supervisor command walkthrough
- API-first walkthrough

Docs:

- `docs/PITCH_PACK_V1_6.md`
- `docs/DEMO_RUN_OF_SHOW_V1_6.md`
- `docs/JUDGE_OBJECTION_HANDLING.md`

## 11. API Surface

New or upgraded routes:

- `GET /cases/{case_id}/lifecycle`
- `POST /cases/{case_id}/lifecycle/transition`
- `GET /cases/{case_id}/timeline`
- `GET /cases/{case_id}/evidence-graph`
- `GET /cases/{case_id}/evidence-graph/export`
- `GET /decision-packages/{package_id}/evidence-graph`
- `GET /audit/export/{case_id}`
- `GET /audit/export/{case_id}/zip-manifest`
- `POST /audit/export/{case_id}/verify`
- `GET /access-decisions/{case_id}`
- `POST /connectors/{name}/failure-profile`
- `GET /connectors/{name}/incidents`
- `POST /connectors/{name}/retry`
- `POST /connectors/{name}/circuit-breaker/reset`
- `POST /fairness/synthetic-cohort/generate`
- `GET /fairness/slices`
- `GET /fairness/appeals`
- `GET /fairness/overrides`
- `GET /fairness/report`
- `GET /materials/accessibility-report`
- `GET /materials/arabic-glossary`
- `GET /materials/release-provenance`

## 12. Data Model Additions

Add or extend tables:

- `case_lifecycle`
- `case_timeline`
- `evidence_nodes`
- `evidence_edges`
- `audit_exports`
- `access_decisions`
- `connector_incidents`
- `connector_failure_profiles`
- `synthetic_cohorts`
- `reasoning_eval_runs`
- `material_snapshots`
- `release_provenance`

## 13. UX Requirements

### Beneficiary Workspace

- lifecycle timeline
- consent center
- evidence tasks
- appeal center
- decision package verification
- notification preferences
- Arabic glossary
- accessibility-friendly forms

### Officer Workspace

- assigned cases
- evidence graph
- repair action review
- appeal review
- callback scheduling
- plan simulator
- connector status per case
- safe transition buttons

### Supervisor Workspace

- command center
- SLA risk
- fairness analytics
- connector incidents
- officer workload
- appeal reversals
- override review
- policy drift snapshots

### Auditor Workspace

- audit export
- evidence graph
- consent usage
- access decisions
- package verification
- responsible AI packet

### Admin Workspace

- connector reliability lab
- release check status
- material generation
- OpenAPI/Postman export
- mock data reset

## 14. Testing Plan

Target: 280+ tests, 0 warnings.

Add:

- `tests/test_api_contract_models.py`
- `tests/test_case_lifecycle.py`
- `tests/test_evidence_graph.py`
- `tests/test_audit_export.py`
- `tests/test_abac_v2.py`
- `tests/test_uaepass_signature_v4.py`
- `tests/test_connector_reliability_lab.py`
- `tests/test_frontend_v16_static.py`
- `tests/test_fairness_analytics.py`
- `tests/test_reasoning_evals.py`
- `tests/test_release_provenance.py`
- `tests/test_docs_drift.py`

Must test:

- no pytest warnings
- no active docs mention wrong current version
- decision package summary uses current app version
- raw dict endpoints replaced by typed models where applicable
- OpenAPI contains schemas for v1.6 routes
- invalid lifecycle transitions fail
- lifecycle transitions audit and notify
- evidence graph contains rule, connector, consent, package, and signature nodes
- audit export verifies
- unknown ownership denies by default
- auditor write attempts fail
- officer unassigned case access fails
- connector circuit breaker works
- failure profile creates incident
- retry clears incident when configured
- Arabic mode has no missing visible keys for v1.6
- accessibility report route returns required checklist
- fairness report never mutates policy decisions
- reasoning contains no unsupported facts
- release provenance includes commit, version, tests, docs, and generated artifacts

## 15. Release Plan

### Phase 1: Stabilize v1.5

- fix test warning
- fix package version drift
- preserve v1.5 release baseline
- update AGENTS stale sections
- add docs drift test

Exit: v1.5 baseline clean, green, and preserved.

### Phase 2: Contracts and Architecture

- add `api_models.py`
- move dict endpoints to typed models
- split routes into modules
- update OpenAPI/Postman generation

Exit: contract tests pass.

### Phase 3: Lifecycle and Evidence

- add lifecycle engine
- add workflow service modules
- add evidence graph
- add audit export

Exit: case trace is exportable end to end.

### Phase 4: Operations and Governance

- ABAC v2
- connector reliability lab
- fairness analytics v2
- reasoning evals
- release provenance

Exit: pilot command controls are real.

### Phase 5: Frontend and Materials

- upgrade beneficiary/officer/supervisor/auditor/admin workspaces
- add accessibility and Arabic QA
- update all docs and pitch materials
- add release-check v1.6

Exit: v1.6 release candidate.

## 16. Acceptance Criteria

v1.6 is complete when:

- local `main` is aligned with `origin/main`
- working tree is clean or all v1.6 files are intentionally staged
- full tests pass with 280+ tests and 0 warnings
- release-check v1.6 passes 25+ gates
- version is `1.6.0` in backend and frontend
- decision packages use current app version
- all v1.6 route bodies are typed
- OpenAPI/Postman/API guide are generated and current
- one lifecycle state machine governs case workflow
- evidence graph export exists
- audit export verifies
- ABAC denies unknown sensitive ownership by default
- connector reliability lab exists
- fairness analytics v2 exists
- reasoning evals exist
- accessibility and Arabic QA materials exist
- judge/demo/pilot/security materials are current
- no real PII or workbook is tracked

## 17. Non-Goals

- real UAE PASS credentials
- real GSB access
- real credit bureau access
- real production secrets
- runtime policy editing
- LLM decisioning on eligibility, money, compliance, or officer action
- changing `backend/policy/engine.py` unless separately approved

## 18. Winning Narrative

v1.4 proved Agent Sanad could plug into a UAE-style digital ecosystem.

v1.5 proved it could be trusted at the control level.

v1.6 proves it can be operated, audited, integrated, released, and explained as a real pilot candidate.

The final pitch:

Agent Sanad is not a demo chatbot. It is an API-first, Arabic-first, audit-first public-service workflow for housing arrears rescheduling, with deterministic policy decisions, human-owned exceptions, verifiable evidence, and pilot-grade operations.
