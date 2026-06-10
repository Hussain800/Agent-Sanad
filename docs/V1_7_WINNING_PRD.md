# Agent Sanad v1.7 Winning PRD

Purpose: take the v1.6 pilot-command release and make Agent Sanad feel complete from every angle: product experience, evidence depth, generated materials, observability, security drills, Arabic/accessibility excellence, and pilot operations. v1.6 proved the backend control plane. v1.7 must prove the whole product.

Core doctrine remains unchanged:

> LLM reads and explains. Deterministic code decides. Human owns the exception.

## 1. Summary

Agent Sanad v1.7 is the "whole product" release. It turns the strong backend assurance layer into a complete, judge-ready, committee-ready, and pilot-team-ready product.

The release focuses on visible trust: full workspaces for beneficiary, officer, supervisor, auditor, and admin; a source-specific evidence graph; generated release materials; zero-warning tests; service observability; security drills; Arabic-first accessibility; and a pilot sandbox packet.

## 2. Current Review

Latest reviewed branch: `main`.

Latest reviewed commit: `56efcd2`.

Local branch state: `main` is aligned with `origin/main`.

Verification:

- Full test suite passes: `287 passed, 1 warning`.
- `scripts/release-check.ps1` passes: `25 passed, 0 failed`.
- Runtime version is `1.6.0`.
- v1.6 features are present: contract-first models, case lifecycle, evidence graph, audit export, ABAC v2, UAE PASS/signature v4, connector reliability lab, fairness analytics, reasoning evals, and release provenance.

## 3. v1.6 Completed

v1.6 successfully added:

- `backend/api_models.py`.
- `backend/case_lifecycle.py`.
- `backend/evidence_graph.py`.
- lifecycle routes.
- evidence graph routes.
- audit export routes.
- access decision route.
- connector reliability lab routes.
- fairness analytics routes.
- OpenAPI/Postman updates.
- release provenance.
- reasoning and LLM safety docs.
- 287 passing tests.
- 25 release gates.

## 4. Must-Fix Gaps

### G1. Full Suite Still Emits a Warning

The only remaining warning is a third-party `pytz` deprecation warning. It is not product code, but v1.6 acceptance asked for zero warnings. v1.7 should make the release check enforce zero unexpected warnings by filtering or documenting approved third-party warnings.

### G2. Active Docs Still Drift

README still contains a "168 tests across 12 files" section and old production-boundary wording. `docs/PRODUCTION_READINESS.md` still claims "59 automated tests" and old pilot gaps. `tests/test_release_provenance.py` still checks for `RELEASE_NOTES_V1_5.md`.

v1.7 must make active docs current and add stronger drift detection.

### G3. Release Notes Naming Is Behind

The repo has `RELEASE_NOTES_V1_5.md`, but no `RELEASE_NOTES_V1_6.md` or v1.7 release-note pattern. v1.7 needs a consistent release-note naming policy and generated release notes.

### G4. Frontend Does Not Yet Expose v1.6 Fully

The backend has lifecycle, evidence graph, audit export, fairness, reliability lab, and materials routes. The frontend still mostly exposes earlier views with light v1.6 static checks.

v1.7 must make those controls visible and usable.

### G5. Evidence Graph Is Too Generic

Current graph includes generic policy nodes and a small set of connector/action/package nodes. It does not yet trace case-specific facts, extracted values, fired rules, plan fields, document trust results, consent usage, appeal evidence, or officer action evidence in enough detail.

### G6. Lifecycle Is Not Wired Into Every Workflow

The lifecycle engine exists, but not every action, appeal, package, connector failure, and officer action is governed by the lifecycle engine.

### G7. API Contracts Are Better, But Not Fully Enforced

Some v1.6 routes still use raw `dict` bodies. v1.7 must close the remaining contract gaps and make generated OpenAPI the source for API docs and Postman.

### G8. Observability Is Still Developer-Oriented

Structured logs and release checks exist, but there is no service operations dashboard, SLO report, trace timeline, or incident review artifact that a pilot operator can use.

### G9. Security Drills Are Missing

Security controls exist. v1.7 must add attack simulations: consent bypass, IDOR, replay, connector tampering, package tamper, prompt injection in evidence, rate-limit abuse, and audit-chain mutation.

### G10. Real Pilot Packet Is Still Incomplete

There are strong docs, but the sandbox handoff still needs a data-processing record, DPIA-style checklist, runbook, service-centre scripts, deployment topology, migration path, monitoring plan, and go/no-go checklist.

## 5. Background

v1.7 aligns Agent Sanad with UAE digital-government priorities:

- [UAE PASS](https://docs.uaepass.ae/) and [TDRA UAE PASS](https://dgov.tdra.gov.ae/en/services/uae-pass) support secure national digital identity and digital signatures.
- [TDRA Government Service Bus](https://tdra.gov.ae/en/Services/government-service-bus-gsb) supports integrated government data exchange.
- [UAE API First Policy](https://uaelegislation.gov.ae/en/policy/details/api-first-policy) supports reusable API-first public services.
- [UAE Digital Government Strategy 2025](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/strategies-plans-and-visions/government-services-and-digital-transformation/uae-national-digital-government-strategy) supports cross-government digital transformation.
- [UAE Charter for AI](https://uaelegislation.gov.ae/en/policy/details/the-uae-charter-for-the-development-and-use-of-artificial-intelligence) supports responsible AI governance.
- [National Digital Accessibility Policy](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/policies/government-services-and-digital-transformation/national-digital-accessibility-policy) supports accessible services for people of determination and elderly users.
- [UAE Verify](https://tdra.gov.ae/en/media/press-release/2022/tdra-launches-the-uae-verify-platform) supports document authenticity verification.
- [TDRA Digital Enablers Report 2023](https://tdra.gov.ae/en/media/press-release/2023/tdra-releases-the-digital-enablers-report-2023) shows the operational scale of UAE PASS, UAE Verify, API Marketplace, GSB, and Tawasul 171.
- [UAE Information Assurance Regulation](https://tdra.gov.ae/-/media/About/regulations-and-ruling/EN/UAE-Information-Assurance-Regulation-v1-1-pdf.ashx) supports risk-based information assurance thinking.

## 6. Objective

Make Agent Sanad v1.7 impossible to dismiss as "just a backend demo."

It must show a complete public-service product:

- a beneficiary can understand and complete the journey
- an officer can operate a queue
- a supervisor can manage service quality
- an auditor can export evidence
- an admin can simulate connector incidents
- a technical team can trust contracts and release evidence
- a judge can see the product in one guided run

## 7. Key Results

| KR | Target |
|---|---|
| Version | Backend `APP_VERSION` and frontend `CLIENT_BUILD` are `1.7.0` |
| Tests | 340+ passing tests |
| Warnings | 0 unexpected warnings |
| Release | `scripts/release-check.ps1` has 35+ gates and passes |
| Frontend | Five workspaces: beneficiary, officer, supervisor, auditor, admin |
| Evidence | Case-specific evidence graph covers facts, rules, plans, documents, actions, appeals, packages, signatures |
| Lifecycle | 100% of state-changing case routes use lifecycle transitions |
| Contracts | No public body route uses raw `dict` unless explicitly justified and tested |
| Materials | API docs, Postman, release notes, runbooks, pitch materials generated or drift-tested |
| Security | Security drill suite covers 10+ abuse cases |
| Accessibility | Arabic and accessibility QA has route, doc, tests, and visible UI affordances |
| Observability | Service health, SLO, incident, and trace dashboards exist in API and UI |

## 8. Market Segments

### Beneficiary

Needs a simple service cockpit: identity, consent, case status, missing evidence, appeals, package verification, Arabic glossary, and accessible controls.

### Officer

Needs an assigned queue with lifecycle, evidence graph, repair tasks, plan simulator, appeals, callbacks, and safe action controls.

### Supervisor

Needs command views for backlog, SLA risk, fairness, connector incidents, appeals, overrides, workload, and service quality.

### Auditor

Needs a no-code export surface for audit chain, access decisions, consent usage, evidence graph, package integrity, and responsible AI materials.

### Admin/Integration Team

Needs connector reliability lab, OpenAPI, Postman, generated docs, material generation, release checks, and mock data reset.

### Judge/Sponsor

Needs a crisp, visual proof that the system is a governed service workflow, not a chatbot.

## 9. Value Propositions

### Beneficiary Value

- fewer unclear statuses
- Arabic-first guidance
- accessible task and appeal flow
- verifiable final package
- transparent consent and privacy controls

### Officer Value

- fewer disconnected tools
- better evidence visibility
- stronger lifecycle governance
- faster exception triage
- safer overrides and appeals

### Government Value

- API-first handoff
- stronger audit posture
- clearer pilot readiness
- better accessibility and Arabic quality
- responsible AI evidence without LLM decisioning

## 10. Solution

### 10.1 v1.7 Release Hygiene

Fix:

- stale README test-count section
- stale `PRODUCTION_READINESS.md`
- stale `RELEASE_NOTES_V1_5.md` references
- release-check comments that mention older versions
- docs drift tests that allow older values
- release provenance commit references

Add:

- `docs/RELEASE_NOTES_V1_6.md`
- `docs/RELEASE_NOTES_V1_7.md`
- `docs/CURRENT_RELEASE.md`
- `tests/test_zero_warnings.py`

### 10.2 Five Workspace Frontend

Upgrade the single-page app into five functional workspaces.

Beneficiary:

- lifecycle timeline
- consent center
- evidence tasks
- appeal center
- decision package verification
- notification preferences
- Arabic glossary

Officer:

- assigned queue
- evidence graph viewer
- repair task review
- appeal review
- callback scheduler
- plan simulator
- lifecycle transition controls

Supervisor:

- backlog
- SLA risk
- fairness
- connector incidents
- officer workload
- override review
- appeal reversals

Auditor:

- audit export
- access decisions
- consent usage
- evidence graph
- package verification
- responsible AI packet links

Admin:

- connector reliability lab
- failure-profile controls
- circuit-breaker reset
- release-check status
- material generation
- mock data reset

### 10.3 Source-Specific Evidence Graph v2

Add `backend/evidence_graph_v2.py`.

Nodes must include:

- fixture source
- connector call
- consent
- document trust check
- extraction result
- income value
- arrears amount
- current EMI
- 20% cap
- fired rule
- plan field
- confidence/risk
- repair action
- appeal evidence
- officer action
- lifecycle transition
- decision package
- signature
- e-Seal

Routes:

- `GET /cases/{case_id}/evidence-graph/v2`
- `GET /cases/{case_id}/evidence-graph/v2/mermaid`
- `GET /cases/{case_id}/evidence-summary`

### 10.4 Lifecycle Enforcement Everywhere

Create a lifecycle middleware/service guard for state-changing routes.

Routes must call lifecycle service:

- application submit
- decide
- officer action
- action upload/reject/resubmit/waive/complete
- appeal submit/review/decision
- package create/sign/seal/revoke
- connector incident escalation
- case close

Add tests for every state-changing route.

### 10.5 Contract Completion

No remaining raw `dict` route bodies except documented material routes.

Add:

- `tests/test_no_raw_dict_routes.py`
- schema examples for every public route
- OpenAPI schema coverage checker
- generated docs from OpenAPI
- generated Postman from OpenAPI

### 10.6 Observability and SLO Center

Add `backend/observability/service_metrics.py`.

Routes:

- `GET /ops/health`
- `GET /ops/slo`
- `GET /ops/traces/{case_id}`
- `GET /ops/incidents`
- `POST /ops/incidents/{id}/resolve`
- `GET /ops/release-check/latest`

Metrics:

- case decision latency
- connector latency
- connector failure rate
- SLA breach rate
- appeal age
- audit export success
- package verification success
- error envelope count
- rate-limit events

UI:

- supervisor/admin ops panel

### 10.7 Security Drill Suite

Add `backend/security_drills.py`.

Routes:

- `POST /security-drills/run`
- `GET /security-drills/latest`

Drills:

- consent bypass
- wrong owner access
- replayed UAE PASS callback
- expired UAE PASS session
- connector tamper
- document tamper
- package hash tamper
- audit-chain mutation
- prompt injection in document text
- rate-limit abuse
- oversized payload
- auditor write attempt

Tests:

- `tests/test_security_drills.py`

### 10.8 Pilot Sandbox Pack

Add generated pilot artifacts:

- `docs/PILOT_SANDBOX_PACKET.md`
- `docs/DATA_PROCESSING_RECORD.md`
- `docs/DPIA_LITE.md`
- `docs/MONITORING_PLAN.md`
- `docs/DEPLOYMENT_TOPOLOGY.md`
- `docs/MIGRATION_PATH.md`
- `docs/SERVICE_CENTRE_SCRIPTS.md`
- `docs/GO_NO_GO_CHECKLIST.md`
- `docs/SANAD_ONE_PAGER.md`

Add route:

- `GET /materials/pilot-sandbox-packet`

### 10.9 Arabic and Accessibility v2

Add:

- visible Arabic glossary workspace
- plain-language policy terms
- RTL screenshot checklist
- keyboard-only walkthrough
- focus order map
- screen-reader label inventory
- form error summary pattern
- printable bilingual decision package

Routes:

- `GET /materials/arabic-glossary`
- `GET /materials/accessibility-report`
- `GET /materials/rtl-checklist`

Tests:

- `tests/test_accessibility_v17.py`
- `tests/test_arabic_glossary.py`

### 10.10 Fairness and Impact v3

Add richer fairness and impact reporting:

- cohort generator with deterministic seed
- path distribution by synthetic segment
- override distribution
- appeal reversal distribution
- repair-loop completion distribution
- confidence/risk distribution
- housing stability impact ledger export

Routes:

- `GET /impact/housing-stability-ledger`
- `GET /fairness/report/v2`
- `GET /fairness/cohort/{id}`

### 10.11 Demo Command Mode

Add a guided run-of-show mode.

Routes:

- `GET /demo/run-of-show`
- `POST /demo/run-of-show/{step_id}`
- `GET /demo/judge-packet`

UI:

- presenter mode
- step timer
- judge objection cards
- one-click failure demo
- one-click audit export
- one-click evidence graph

Docs:

- `docs/RUN_OF_SHOW_V1_7.md`
- `docs/JUDGE_PACKET_V1_7.md`

## 11. API Surface

New or upgraded routes:

- `GET /cases/{case_id}/evidence-graph/v2`
- `GET /cases/{case_id}/evidence-graph/v2/mermaid`
- `GET /cases/{case_id}/evidence-summary`
- `GET /ops/health`
- `GET /ops/slo`
- `GET /ops/traces/{case_id}`
- `GET /ops/incidents`
- `POST /ops/incidents/{id}/resolve`
- `GET /ops/release-check/latest`
- `POST /security-drills/run`
- `GET /security-drills/latest`
- `GET /materials/pilot-sandbox-packet`
- `GET /materials/rtl-checklist`
- `GET /impact/housing-stability-ledger`
- `GET /fairness/report/v2`
- `GET /fairness/cohort/{id}`
- `GET /demo/run-of-show`
- `POST /demo/run-of-show/{step_id}`
- `GET /demo/judge-packet`

## 12. Data Model Additions

Add or extend:

- `ops_metrics`
- `ops_incidents`
- `release_check_runs`
- `security_drill_runs`
- `evidence_graph_nodes`
- `evidence_graph_edges`
- `material_generations`
- `demo_run_steps`
- `impact_ledger`
- `accessibility_checks`
- `arabic_glossary_terms`

## 13. UX Requirements

### Visual Standard

The UI must feel like a serious UAE government service operations cockpit:

- dense but calm
- clear hierarchy
- no decorative clutter
- Arabic-first capable
- keyboard usable
- audit-friendly
- no marketing hero replacing the actual product

### Required Screens

- Beneficiary Cockpit
- Officer Workbench
- Supervisor Command Center
- Auditor Evidence Room
- Admin Reliability Lab
- Presenter Mode

## 14. Testing Plan

Target: 340+ tests, 0 unexpected warnings.

Add:

- `tests/test_zero_warnings.py`
- `tests/test_no_raw_dict_routes.py`
- `tests/test_evidence_graph_v2.py`
- `tests/test_lifecycle_enforcement.py`
- `tests/test_ops_observability.py`
- `tests/test_security_drills.py`
- `tests/test_pilot_sandbox_packet.py`
- `tests/test_accessibility_v17.py`
- `tests/test_arabic_glossary.py`
- `tests/test_impact_ledger.py`
- `tests/test_demo_command_mode.py`
- `tests/test_release_notes_current.py`

Must test:

- full suite has 0 unexpected warnings
- README active sections show v1.7 and 340+ tests
- release notes use current naming
- every state-changing route emits lifecycle event
- evidence graph v2 includes case-specific facts
- audit export includes evidence graph v2
- no raw dict bodies for public write routes
- security drills all pass
- ops SLO route returns expected metrics
- pilot sandbox packet route exists
- Arabic glossary contains key policy terms
- accessibility report includes keyboard, focus, RTL, contrast, screen-reader checks
- presenter mode has run-of-show steps
- release-check has 35+ gates

## 15. Release Plan

### Phase 1: Hygiene

- bump to `1.7.0`
- fix docs drift
- add release notes v1.6/v1.7
- enforce zero unexpected warnings
- update release provenance

Exit: clean baseline.

### Phase 2: Frontend Whole Product

- build five workspaces
- add presenter mode
- add Arabic glossary and accessibility panels

Exit: v1.6 backend controls visible in product.

### Phase 3: Evidence and Lifecycle

- evidence graph v2
- lifecycle enforcement across state-changing routes
- audit export v2

Exit: every decision and action is traceable.

### Phase 4: Ops and Security

- observability/SLO center
- security drill suite
- connector incident operations

Exit: pilot operators have control surfaces.

### Phase 5: Pilot Packet

- sandbox packet
- data-processing record
- monitoring plan
- deployment topology
- go/no-go checklist
- judge packet

Exit: complete v1.7 release candidate.

## 16. Acceptance Criteria

v1.7 is complete when:

- local `main` is aligned with `origin/main`
- full suite passes with 340+ tests
- 0 unexpected warnings
- release-check has 35+ gates and passes
- version is `1.7.0` in backend and frontend
- active docs have no stale test counts or release names
- release notes v1.7 exist
- five frontend workspaces exist and are tested
- evidence graph v2 is case-specific
- lifecycle enforcement covers all state-changing routes
- ops/SLO center exists
- security drills exist and pass
- pilot sandbox packet exists
- Arabic/accessibility v2 exists
- OpenAPI/Postman/API docs are regenerated
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

v1.6 proved Agent Sanad can be audited.

v1.7 proves Agent Sanad can be operated, presented, handed off, and trusted as a complete service.

The final pitch:

Agent Sanad is an Arabic-first, API-first, audit-first public-service operating system for housing arrears rescheduling. It gives beneficiaries clarity, officers control, supervisors oversight, auditors evidence, and government teams a credible path to a sandbox pilot, while keeping the LLM out of every money decision.

