# Agent Sanad v1.8 Winning PRD

## 1. Summary

Agent Sanad v1.8 turns the v1.7 whole-product release into a national-scale housing assistance operating system.

v1.7 proved the product can decide, explain, audit, secure, and demo a single arrears rescheduling journey. v1.8 must add the "wow factor": a policy digital twin, proactive arrears rescue radar, mock national interoperability certification, Arabic-first service copilot, verifiable evidence vault, and self-verifying release brain. The goal is not more screens. The goal is a product that feels ready for a serious UAE pilot while still staying offline, mocked, deterministic, and hackathon-safe.

## 2. Contacts

| Stakeholder | Role | Comment |
|---|---|---|
| Product owner | Hackathon lead | Owns the story, scope, and judging narrative |
| Engineering owner | Full-stack implementer | Owns FastAPI, SQLite, frontend, tests, and release check |
| Policy owner | Housing policy reviewer | Confirms the 20 percent cap, rule explanations, and exception handling |
| Operations owner | Pilot service-center lead | Confirms queues, scripts, training, and escalation flows |
| Security owner | Trust and assurance reviewer | Confirms threat model, ABAC, drills, audit, and evidence integrity |
| Accessibility and Arabic reviewer | Inclusion lead | Confirms Arabic, RTL, plain language, seniors, and people of determination |
| Integration reviewer | UAE platform readiness lead | Confirms mock UAE PASS, GSB, UAE Verify, API marketplace, and future real-connector path |

## 3. Background

### v1.7 Completion Review

Verification was performed on June 10, 2026 in `C:\Users\wasif\OneDrive\Desktop\Agent-Sanad`.

| Check | Result |
|---|---|
| Branch | `main` |
| Remote alignment | `main`, `origin/main`, and `origin/HEAD` point to `c331917` |
| Latest release commit | `52d9806 v1.7.0: Whole product release` |
| Full tests | `349 passed, 1 warning in 12.86s` |
| Release gates | `35 passed, 0 failed` |
| Version | `APP_VERSION == CLIENT_BUILD == 1.7.0` |
| Working tree before this PRD | Clean |

v1.7 is complete by its own release gates. It added:

- Evidence graph v2.
- Ops observability.
- Security drills.
- Five frontend workspaces.
- Presenter mode routes.
- Arabic glossary, accessibility report, and RTL checklist.
- Fairness and impact v3.
- Pilot sandbox materials.
- No raw dict route checks.
- 35 release gates.

### Important v1.7 Gaps Found During Review

These are not release blockers for v1.7, but they are exactly where v1.8 can become a winning release.

| Gap | Evidence | v1.8 response |
|---|---|---|
| Release metadata still drifts | `docs/CURRENT_RELEASE.md` says `319+` tests while actual run is 349; `docs/RELEASE_PROVENANCE.md` still says v1.6; `backend/observability/service_metrics.py` reports 287 tests and 25 gates | Add self-verifying release brain that generates runtime release facts from one source of truth |
| Tests tolerate stale material names | `tests/test_release_provenance.py` checks for v1.5 release notes instead of current provenance | Add provenance contract tests that require current release docs |
| Zero-warning goal is not fully achieved | Full suite still emits one third-party `pytz` deprecation warning | Add explicit warning budget registry and fail on new/unapproved warnings |
| Evidence graph is strong, but not yet a reusable evidence vault | Graph explains a case, but does not create portable verifiable credentials or a transparency log | Add evidence vault, Merkle-style chain, QR verification, and court/auditor packet |
| Observability is internal | Ops endpoints exist, but there is no service command loop with SLO playbooks, operator tasks, and simulated live incidents | Add Mission Control and service reliability autopilot |
| Frontend workspaces exist, but the product can feel like a portal | v1.7 exposes surfaces, but v1.8 needs one killer flow that makes judges feel the future | Add proactive rescue radar and policy digital twin |
| UAE integration is mocked, but not yet certification-shaped | Connectors exist, but not a contract certification kit or onboarding simulator | Add mock GSB/API Marketplace/UAE PASS certification lab |
| Arabic exists, but not service-center native | Translation keys exist, but no guided Arabic voice/chat-style journey for seniors and low-literacy users | Add Arabic-first service copilot with deterministic guardrails |

### Why Now

The UAE digital government ecosystem rewards products that are integrated, accessible, trusted, and measurable.

Official public sources reinforce the direction:

- UAE PASS is the national digital identity layer for secure access, digital signatures, and end-to-end government transactions.
- GSB is the government integration backbone for secure data exchange.
- UAE Verify supports document verification.
- The UAE API Marketplace supports API-led reuse.
- UAE digital government strategy emphasizes accessibility, transparency, accountability, and integrated services.
- UAE digital accessibility policy focuses on people of determination and elderly users.
- The UAE AI Charter emphasizes responsible and inclusive AI adoption.
- The Sheikh Zayed Housing Programme exists to provide housing support to UAE citizens, and the arrears scheduling service is the direct service context for this product.

Reference sources:

- [UAE Digital Government Strategy 2025](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/strategies-plans-and-visions/government-services-and-digital-transformation/uae-national-digital-government-strategy)
- [TDRA Government Service Bus](https://tdra.gov.ae/en/Services/government-service-bus-gsb)
- [TDRA Digital Government Sector](https://tdra.gov.ae/en/About/tdra-sectors)
- [UAE API Marketplace](https://u.ae/en/about-the-uae/digital-uae/digital-transformation/platforms-and-apps/uae-api-marketplace)
- [MOEI Housing Arrears Assistance Scheduling](https://www.moei.gov.ae/en/services/housing-arrears-assistance-scheduling)
- [Sheikh Zayed Housing Programme](https://www.moei.gov.ae/en/about-ministry/sheikh-zayed-housing-program)
- [Housing authorities and programmes](https://u.ae/en/information-and-services/housing/housing-authorities-and-programmes)
- [UAE AI Charter](https://uaelegislation.gov.ae/en/policy/details/the-uae-charter-for-the-development-and-use-of-artificial-intelligence)
- [National Digital Accessibility Policy](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/policies/government-services-and-digital-transformation/national-digital-accessibility-policy)
- [UAE Personal Data Protection Law](https://uaelegislation.gov.ae/en/legislations/1972?keyword=decree+by+law)
- [Electronic Transactions and Trust Services](https://uaelegislation.gov.ae/en/legislations/1539)

## 4. Objective

### Product Objective

Make Agent Sanad feel like the pilot-ready national command layer for arrears rescheduling, not only a decision demo.

The judge should see three things in under five minutes:

1. A family can be rescued before arrears become a crisis.
2. A policy team can safely simulate national impact before changing any rule.
3. An auditor can verify every decision, document, consent, signature, and connector call without trusting the app blindly.

### Strategic Objective

Agent Sanad v1.8 should become the bridge between hackathon MVP and credible government pilot:

- Beneficiary value: faster, clearer, Arabic-first, less stressful arrears support.
- Officer value: less manual chasing, better evidence, fewer risky blind spots.
- Supervisor value: live backlog, SLA, fairness, and incident control.
- Auditor value: portable proof, provenance, and tamper detection.
- Integration value: connector contracts that look ready for UAE PASS, GSB, UAE Verify, banks, and service-center systems.

### Key Results

| Key Result | Target |
|---|---|
| Tests | 420+ passing tests |
| Release gates | 45+ passing automated release gates |
| Version | `APP_VERSION == CLIENT_BUILD == 1.8.0` |
| Warning budget | 0 unexpected warnings; approved third-party warnings documented and tested |
| Release provenance | Runtime, docs, release check, OpenAPI, Postman, and current release docs all agree |
| Digital twin | Simulate at least 5 policy scenarios across all 13 cases and a synthetic cohort |
| Proactive radar | Generate deterministic early-warning interventions for at least 7 risk patterns |
| Evidence vault | Every case can produce a portable verification bundle and QR-style verification payload |
| Interop lab | Mock certification scorecards for UAE PASS, GSB, UAE Verify, API Marketplace, banking/credit, notifications |
| Arabic service copilot | Bilingual guided journey with deterministic, read-only explanations and no policy decisions made by LLM |
| Security | Continuous red-team suite has 20+ drills, including prompt injection, replay, tamper, owner-bypass, and connector fraud |
| Accessibility | WCAG 2.2 AA-style checklist, keyboard walkthrough, RTL report, senior-friendly mode, and print package |

## 5. Market Segments

### Primary Users

| Segment | Job to be done |
|---|---|
| Beneficiary in arrears | Understand options, submit missing evidence, and avoid housing instability |
| Senior citizen beneficiary | Complete a service without confusion, travel, or complex digital steps |
| Service-center officer | Resolve cases quickly while staying inside policy |
| Supervisor | Reduce backlog, see risk, and allocate staff before SLA breaches happen |
| Auditor | Verify the chain of decision, consent, evidence, and human actions |
| Policy team | Test policy changes before they affect citizens |
| Integration team | See exactly how the product will connect to national enablers later |

### Constraints

- Must remain offline and mock-first for the hackathon.
- Must not use real UAE PASS, real GSB, real UAE Verify, real bank APIs, real Emirates IDs, or real beneficiary data.
- LLM can explain and draft plain-language guidance only.
- Deterministic code must make every eligibility, cap, affordability, path, and recommendation decision.
- The 20 percent salary cap is a hard rule.
- `backend/policy/engine.py` should remain untouched unless absolutely necessary.
- All new connectors must be contract-shaped, mocked, failure-aware, audited, and tested.

## 6. Value Propositions

### Winning Value Proposition

Agent Sanad is not an AI that decides housing support. It is a trust machine around a deterministic housing policy engine.

It rescues families earlier, gives officers a complete evidence picture, lets supervisors run a live service, lets policy teams simulate impact before changing rules, and lets auditors verify every step.

### Value Curve

| Dimension | Typical hackathon product | Agent Sanad v1.8 |
|---|---|---|
| Decision quality | AI recommendation | Deterministic policy engine with exact rules |
| Trust | Logs and screenshots | Evidence vault, hash chain, QR verification, provenance |
| Integration | API stubs | Mock national interoperability certification |
| Beneficiary UX | Form and result | Arabic-first rescue journey with guided evidence repair |
| Operations | Dashboard | Mission Control with incidents, SLOs, queue pressure, and playbooks |
| Policy | Static rules | Digital twin and scenario simulator |
| Security | Basic checks | Continuous red-team and chaos drills |
| Accessibility | Translations | Senior mode, RTL, WCAG-style checklist, service-center scripts |
| Demo | Click path | Judge-ready national operating story |

## 7. Solution

### v1.8 Product Name

**Agent Sanad v1.8: National Housing Resilience OS**

This release should feel like a command system for:

- Rescue.
- Policy.
- Trust.
- Operations.
- Integration.

### 7.1 UX And Prototype

#### New Global Navigation

The frontend should keep the single-file architecture, but the product should feel like one integrated system.

Add six v1.8 command areas:

1. **Rescue Radar**
2. **Policy Digital Twin**
3. **Evidence Vault**
4. **Interop Certification Lab**
5. **Arabic Service Copilot**
6. **Mission Control**

The old v1.7 workspaces remain, but v1.8 adds a top-level "National Pilot" mode that tells a stronger story.

#### Killer Demo Flow

1. Start in Rescue Radar.
2. Show a synthetic family trending toward arrears stress.
3. Click "Run rescue plan."
4. The system shows consent, connectors, evidence, 20 percent cap, options, and next actions.
5. Open Policy Digital Twin.
6. Simulate what happens if income thresholds or hardship handling change.
7. Show that deterministic rules still protect the cap.
8. Open Evidence Vault.
9. Verify a QR-style receipt and tamper with one fact.
10. Show verification failure.
11. Open Interop Lab.
12. Show UAE PASS, GSB, UAE Verify, bank, and notification connectors as certification-ready mocks.
13. Open Mission Control.
14. Trigger a connector incident and watch SLO, playbook, audit, and beneficiary messaging update.

### 7.2 Key Features

## Feature 1 - Rescue Radar

### User Story

As a supervisor or officer, I want to spot arrears risk before the citizen needs emergency intervention, so we can offer a safe path earlier.

### Description

Create a deterministic early-warning engine that classifies risk patterns across seeded cases and synthetic cohorts.

It does not make final policy decisions. It recommends outreach, evidence repair, counseling, callback, or supervisor review.

### Backend

Add `backend/rescue_radar.py`.

Add routes:

- `GET /rescue/radar`
- `GET /rescue/radar/{case_id}`
- `POST /rescue/radar/simulate`
- `POST /rescue/outreach/{case_id}`
- `GET /rescue/interventions`

Risk patterns:

- New arrears growth.
- Low headroom near 20 percent cap.
- High obligations.
- Missing income proof.
- Contradictory income.
- Repeated active applications.
- Temporary hardship.
- Family-income pressure.
- Senior citizen support needs.
- Connector data outage.
- Appeal likely.
- Document trust risk.

Outputs:

- `risk_score`
- `risk_band`
- `risk_reasons`
- `recommended_interventions`
- `policy_safe`
- `requires_consent`
- `human_owner`
- `beneficiary_message_en`
- `beneficiary_message_ar`
- `audit_event_id`

### Frontend

Add a Rescue Radar screen with:

- Risk heatmap.
- Case cards.
- Intervention drawer.
- Consent status.
- Arabic beneficiary preview.
- Outreach mock send button.
- "Why this is safe" explanation.

### Tests

- Rescue radar is deterministic.
- Radar does not mutate policy decisions.
- High-risk fixtures map to expected risk patterns.
- Outreach requires consent.
- Arabic message exists for every intervention.
- Audit event is emitted.
- No real PII appears.

## Feature 2 - Policy Digital Twin

### User Story

As a policy team, I want to test policy scenarios on synthetic cases before changing rules, so we can see impact, fairness, workload, and risk safely.

### Description

Build a sandbox simulator that replays all 13 demo cases and synthetic cohorts under scenario settings.

This is the biggest wow feature. Judges should see a future where policy changes are tested like software before they touch citizens.

### Backend

Add `backend/policy_digital_twin.py`.

Add routes:

- `GET /digital-twin/scenarios`
- `POST /digital-twin/run`
- `GET /digital-twin/runs/{run_id}`
- `GET /digital-twin/runs/{run_id}/impact`
- `GET /digital-twin/runs/{run_id}/fairness`
- `GET /digital-twin/runs/{run_id}/workload`
- `GET /digital-twin/runs/{run_id}/explain`
- `GET /digital-twin/runs/{run_id}/compare/{baseline_run_id}`

Scenario knobs:

- `min_headroom_aed`
- `hardship_fast_track`
- `missing_doc_grace_days`
- `appeal_review_sla_hours`
- `connector_outage_rate`
- `senior_support_priority`
- `family_pressure_weight`
- `officer_capacity_per_day`

Hard constraints:

- Never relax the 20 percent salary cap.
- Never change `backend/policy/engine.py` for scenario knobs unless there is no alternative.
- Scenario decisions must be labeled simulated and non-binding.
- Baseline official recommendation must remain visible.

Outputs:

- Approval/refer/request-doc/reject distribution.
- Path distribution.
- Arrears cleared.
- Added months.
- SLA load.
- Officer workload.
- Appeal likelihood.
- Fairness slices.
- Beneficiary impact score.
- Risk delta.
- Rule-fire delta.
- Human-review count.

### Frontend

Add a Policy Digital Twin workspace with:

- Scenario controls.
- Baseline vs scenario table.
- Case-by-case diff.
- Fairness chart.
- Workload chart.
- Cap-protection banner.
- Export button for policy memo.

### Tests

- Scenario output is deterministic for same seed.
- 20 percent cap cannot be relaxed.
- Baseline official decisions do not mutate.
- Scenario run is audit logged.
- Compare route returns exact deltas.
- Synthetic cohort scenario has stable counts.

## Feature 3 - Evidence Vault And Trust Receipt

### User Story

As an auditor or beneficiary, I want a portable receipt that proves what evidence was used and whether it was tampered with.

### Description

Upgrade evidence graph v2 into a verifiable evidence vault.

The vault should create a case proof bundle with:

- Evidence graph.
- Consent receipts.
- Connector attestations.
- Document trust results.
- Policy rule firings.
- Decision package hash.
- Signature/e-Seal proof.
- Lifecycle timeline.
- Human action log.
- QR-style verification payload.

### Backend

Add `backend/evidence_vault.py`.

Add routes:

- `POST /cases/{case_id}/evidence-vault/build`
- `GET /cases/{case_id}/evidence-vault`
- `GET /cases/{case_id}/trust-receipt`
- `POST /trust-receipts/verify`
- `POST /trust-receipts/tamper-demo`
- `GET /trust-receipts/{receipt_id}/public`

Use simple deterministic hashes. A Merkle-style tree is enough for v1.8. No blockchain.

### Frontend

Add Evidence Vault workspace:

- Trust receipt viewer.
- QR-style payload block.
- Tamper demo.
- Public verifier panel.
- Auditor notes.
- Exportable JSON.

### Tests

- Build vault for all 13 cases.
- Verify untampered receipt passes.
- Tampered receipt fails.
- Receipt includes consent, connector, rule, package, lifecycle, and action references.
- Public receipt redacts sensitive data.

## Feature 4 - National Interoperability Certification Lab

### User Story

As an integration reviewer, I want to see whether each mock connector is ready for real onboarding, so I can trust the future integration path.

### Description

Create a certification lab that scores every mock connector against contract, auth, consent, audit, retry, redaction, rate-limit, and failure requirements.

Mock targets:

- UAE PASS.
- GSB.
- UAE Verify.
- Financial capacity.
- Bank/loan system.
- Notifications.
- Case management.
- Tawasul 171 style support channel.
- API Marketplace publishing.

### Backend

Add `backend/interop_certification.py`.

Add routes:

- `GET /interop/certification`
- `GET /interop/certification/{connector}`
- `POST /interop/certification/run`
- `GET /interop/onboarding-pack`
- `GET /interop/api-marketplace-readiness`
- `GET /interop/gsb-onboarding-checklist`
- `GET /interop/uaepass-readiness`
- `GET /interop/uae-verify-readiness`

Score categories:

- Contract schema.
- Auth shape.
- Consent enforcement.
- Purpose binding.
- Data minimization.
- Audit event.
- Trace ID.
- Retry and timeout.
- Circuit breaker.
- Error envelope.
- Redaction.
- Synthetic fixture coverage.
- Failure simulation.

### Frontend

Add Interop Certification Lab:

- Connector scorecards.
- Contract diff.
- GSB onboarding checklist.
- API marketplace readiness.
- UAE PASS readiness.
- UAE Verify readiness.
- Failure replay.

### Tests

- Every connector has a scorecard.
- No connector can score passing without consent and audit checks.
- OpenAPI and Postman include interop routes.
- Mock certification is deterministic.

## Feature 5 - Arabic Service Copilot

### User Story

As a beneficiary, especially a senior citizen or low-literacy user, I want the service to guide me in plain Arabic and English, so I know what to do next.

### Description

Build a deterministic, Arabic-first service copilot.

The copilot may use an optional LLM only to rephrase approved content. It never decides, never changes numbers, never bypasses rules, and never invents requirements.

### Backend

Add `backend/service_copilot.py`.

Add routes:

- `POST /copilot/session/start`
- `POST /copilot/session/{session_id}/message`
- `GET /copilot/session/{session_id}`
- `GET /copilot/scripts`
- `GET /copilot/safety-case`
- `POST /copilot/redteam/run`

Supported intents:

- Check my case status.
- Explain my result.
- What document is missing?
- Why was I referred?
- What is the 20 percent cap?
- Submit appeal guidance.
- Book service-center callback.
- Switch Arabic/English.
- Senior-friendly mode.

Guardrails:

- Intent classifier is deterministic.
- Responses are template-first.
- Optional LLM output must be constrained to approved facts.
- Prompt injection returns a safety response and audit event.
- Every response has source facts.

### Frontend

Add Arabic Service Copilot workspace:

- Chat-like panel.
- Arabic default toggle.
- Senior mode.
- Plain-language answer cards.
- Source chips.
- "Officer handoff" button.
- Safety trace panel.

### Tests

- All supported intents return deterministic content.
- Arabic and English exist for every response.
- Prompt injection cannot change decision.
- LLM-disabled mode works.
- Source facts are present.

## Feature 6 - Mission Control And Service Reliability Autopilot

### User Story

As a supervisor or admin, I want the system to tell me what is broken, who is affected, and what to do next.

### Description

Upgrade observability into action.

Mission Control should translate signals into playbooks:

- Connector outage.
- SLA breach risk.
- Appeal backlog.
- Security drill failure.
- Consent failure spike.
- Evidence repair backlog.
- Release drift.
- Warning budget breach.

### Backend

Add `backend/mission_control.py`.

Add routes:

- `GET /mission-control`
- `GET /mission-control/playbooks`
- `POST /mission-control/playbooks/{playbook_id}/run`
- `GET /mission-control/tasks`
- `POST /mission-control/tasks/{task_id}/complete`
- `GET /mission-control/risk-brief`
- `GET /mission-control/live-demo-script`

### Frontend

Mission Control should show:

- Live health.
- Top incidents.
- Impacted cases.
- Playbook recommendations.
- Owner.
- ETA.
- Audit event.
- One-click demo incident.
- Recovery proof.

### Tests

- Incidents create playbook tasks.
- Completing tasks updates state.
- Release drift creates high-priority task.
- Connector outage maps to impacted cases.
- Playbook run emits audit event.

## Feature 7 - Self-Verifying Release Brain

### User Story

As a builder or judge, I want the app to prove what version it is, how many tests/gates passed, and whether docs match runtime.

### Description

Fix the v1.7 metadata drift permanently.

Create one release metadata source and use it everywhere:

- Runtime.
- Release check.
- Current release doc.
- Release provenance.
- Release notes.
- OpenAPI.
- Postman.
- Frontend.
- Ops endpoint.

### Backend

Add `backend/release_brain.py`.

Add routes:

- `GET /release/brain`
- `GET /release/provenance`
- `GET /release/drift`
- `POST /release/drift/check`
- `GET /release/warning-budget`

Add `docs/RELEASE_FACTS.json`.

Fields:

- version.
- commit.
- branch.
- test_count.
- test_command.
- gate_count.
- release_check_command.
- warning_budget.
- approved_warnings.
- generated_docs.
- generated_at.

### Scripts

Update `scripts/release-check.ps1`:

- 45+ gates.
- Verify release facts.
- Verify current docs.
- Verify runtime release endpoint.
- Verify OpenAPI/Postman version.
- Verify no stale v1.6/v1.7 counts in active docs.
- Verify approved warning registry.
- Verify frontend build version.

### Tests

- No active doc can say stale test/gate counts.
- `GET /ops/release-check/latest` reports v1.8 facts.
- `docs/RELEASE_PROVENANCE.md` is current.
- `docs/CURRENT_RELEASE.md` is current.
- `docs/RELEASE_NOTES_V1_8.md` exists.

## Feature 8 - Continuous Red Team And Chaos Lab

### User Story

As a security reviewer, I want the system to attack itself safely, so we can show it resists common failures.

### Description

Expand v1.7 security drills into a continuous red-team lab.

Drills:

- Consent bypass.
- Wrong owner access.
- UAE PASS replay.
- Expired session.
- Connector tamper.
- Document tamper.
- Package tamper.
- Audit-chain mutation.
- Prompt injection.
- Rate-limit abuse.
- Oversized payload.
- Auditor write attempt.
- Digital twin cap relaxation attempt.
- Interop connector missing consent.
- Copilot hallucination attempt.
- Release facts drift.
- QR receipt tamper.
- Public receipt leakage.
- Arabic prompt injection.
- Circuit breaker abuse.

Routes:

- `POST /redteam/run`
- `GET /redteam/latest`
- `GET /redteam/history`
- `GET /redteam/coverage`

Tests:

- 20+ drills pass.
- Failed drill creates Mission Control incident.
- Red-team history is persisted or deterministically available.
- Drill output is safe to display.

## Feature 9 - Materials Pack v1.8

### New Docs

Add:

- `docs/RELEASE_NOTES_V1_8.md`
- `docs/RELEASE_FACTS.json`
- `docs/V1_8_IMPLEMENTATION_SUMMARY.md`
- `docs/NATIONAL_HOUSING_RESILIENCE_OS.md`
- `docs/POLICY_DIGITAL_TWIN_GUIDE.md`
- `docs/RESCUE_RADAR_PLAYBOOK.md`
- `docs/EVIDENCE_VAULT_TRUST_RECEIPT.md`
- `docs/INTEROP_CERTIFICATION_PACK.md`
- `docs/UAE_PLATFORM_ALIGNMENT_V1_8.md`
- `docs/ARABIC_SERVICE_COPILOT_SAFETY_CASE.md`
- `docs/REDTEAM_CHAOS_LAB.md`
- `docs/MISSION_CONTROL_RUNBOOK.md`
- `docs/JUDGE_PACKET_V1_8.md`
- `docs/RUN_OF_SHOW_V1_8.md`
- `docs/PILOT_MOU_TEMPLATE.md`
- `docs/TRAINING_AND_ADOPTION_PLAN.md`
- `docs/DATA_RETENTION_AND_PURGE_PLAN.md`
- `docs/PROCUREMENT_SECURITY_QUESTIONNAIRE.md`
- `docs/ACCESSIBILITY_WCAG_2_2_AA_REPORT.md`

### New Material Routes

Add:

- `GET /materials/v1.8/judge-packet`
- `GET /materials/v1.8/run-of-show`
- `GET /materials/v1.8/interop-certification-pack`
- `GET /materials/v1.8/policy-digital-twin-guide`
- `GET /materials/v1.8/evidence-vault-guide`
- `GET /materials/v1.8/copilot-safety-case`

## 7.3 Technology

### Backend Architecture

New modules:

- `backend/rescue_radar.py`
- `backend/policy_digital_twin.py`
- `backend/evidence_vault.py`
- `backend/interop_certification.py`
- `backend/service_copilot.py`
- `backend/mission_control.py`
- `backend/release_brain.py`
- `backend/redteam_lab.py`

Prefer small pure-Python modules with deterministic functions and typed Pydantic request/response models.

### SQLite

Add tables only if needed:

- `rescue_interventions`
- `digital_twin_runs`
- `evidence_vault_receipts`
- `interop_certification_runs`
- `copilot_sessions`
- `mission_control_tasks`
- `redteam_runs`
- `release_facts`

All tables must degrade gracefully if SQLite is unavailable.

### Frontend

Keep the single-file app. Use no dependencies.

Add:

- Top-level National Pilot mode.
- Rescue Radar.
- Policy Digital Twin.
- Evidence Vault.
- Interop Certification Lab.
- Arabic Service Copilot.
- Mission Control.

Do not make a landing page. The app should open into usable product.

### API Contract

All public write routes must use typed request models.

Regenerate:

- `docs/api/openapi.json`
- `docs/POSTMAN_COLLECTION.json`

### Security

- ABAC on every sensitive route.
- Public trust receipt route must be redacted.
- Copilot is read-only.
- Digital twin is non-binding.
- Release facts cannot be user-mutated.
- Red-team routes require admin role except safe latest/coverage views.

## 7.4 Assumptions

| Assumption | How to validate |
|---|---|
| Judges will reward national-scale operating story more than more CRUD screens | Run demo with a five-minute script and check if story is understood |
| Policy Digital Twin is the strongest wow moment | Ask reviewers which screen they remember after demo |
| Rescue Radar can stay mock-only while feeling useful | Use deterministic synthetic cases and show clear non-binding labels |
| Arabic Service Copilot can be safe without real LLM | Use template-first replies and optional LLM disabled by default |
| Interop certification will impress without real connectors | Make scorecards concrete, contract-shaped, and failure-aware |
| Evidence Vault can be credible with deterministic hashes | Show tamper failure and public redacted verification |

## 8. Release

### Scope For v1.8

Must ship:

- Version bump to `1.8.0`.
- Rescue Radar.
- Policy Digital Twin.
- Evidence Vault and Trust Receipt.
- Interop Certification Lab.
- Arabic Service Copilot.
- Mission Control.
- Self-Verifying Release Brain.
- Continuous Red Team and Chaos Lab.
- v1.8 materials pack.
- OpenAPI and Postman regeneration.
- 420+ tests.
- 45+ release gates.
- 0 unexpected warnings.

### Out Of Scope

- Real UAE PASS OAuth.
- Real GSB connection.
- Real UAE Verify connection.
- Real bank or credit bureau integration.
- Real SMS/WhatsApp sending.
- Real beneficiary data.
- Production deployment.
- Changing the deterministic policy engine unless there is no alternative.

### Acceptance Criteria

| Area | Acceptance |
|---|---|
| Branch | Latest `main` fetched and local main aligned with `origin/main` before work |
| Version | Backend and frontend both `1.8.0` |
| Tests | `python -B -m pytest tests\ -q -p no:cacheprovider` passes with 420+ tests |
| Gates | `scripts\release-check.ps1` passes with 45+ gates |
| Warnings | 0 unexpected warnings |
| Rescue | Radar and interventions work for all 13 cases and synthetic cohort |
| Digital twin | Scenario runs, impact, fairness, workload, and compare routes work |
| Evidence vault | Trust receipt verifies and tamper demo fails safely |
| Interop | Every connector has certification scorecard and readiness checklist |
| Copilot | Arabic/English deterministic guided journey works with injection defense |
| Mission Control | Incidents produce tasks/playbooks and release drift is detected |
| Red team | 20+ drills pass and failures create incidents |
| Docs | Current release, provenance, release notes, materials, OpenAPI, Postman are current |
| Safety | No real PII, no real workbook, no real credentials |

### Release Gate Additions

Add gates for:

- v1.8 version consistency.
- Release facts source of truth.
- Current release doc is current.
- Release provenance is current.
- No stale test/gate counts.
- Warning budget.
- Rescue radar tests.
- Digital twin tests.
- Evidence vault tests.
- Interop certification tests.
- Copilot tests.
- Mission Control tests.
- Red-team lab tests.
- Material routes.
- OpenAPI/Postman regeneration.
- Public receipt redaction.
- Digital twin cannot relax 20 percent cap.
- Copilot cannot change decisions.
- All write routes typed.
- All new frontend workspace labels have Arabic keys.

## Execution Hyperprompt

Use this prompt to fully execute the v1.8 PRD:

```text
You are Codex working in the Agent Sanad repo.

Goal: fully execute docs/V1_8_WINNING_PRD.md end to end. This must be a massive, winning, product-grade v1.8 release with a real wow factor while staying offline, deterministic, mocked, and hackathon-safe.

Non-negotiables:
- Do not use subagents.
- Stay on latest main. Fetch first.
- Read AGENTS.md before touching files.
- Preserve doctrine: "LLM reads and explains. Deterministic code decides. Human owns the exception."
- Do not touch backend/policy/engine.py unless absolutely unavoidable.
- Never relax the 20 percent salary cap.
- Do not use real UAE PASS, real GSB, real UAE Verify, real bank APIs, real Emirates IDs, real beneficiary data, or real credentials.
- All integrations must remain mocked but contract-shaped, audited, typed, tested, and failure-aware.
- APP_VERSION in backend/app.py must equal CLIENT_BUILD in frontend/index.html.
- Preserve all existing behavior and tests.
- Use apply_patch for manual edits.

First:
1. git fetch --prune origin
2. ensure local main is latest origin/main
3. inspect git status and latest commits
4. read AGENTS.md
5. read docs/V1_8_WINNING_PRD.md
6. inspect backend/app.py, backend/api_models.py, backend/store.py, backend/case_lifecycle.py, backend/evidence_graph_v2.py, backend/observability/service_metrics.py, backend/security_drills.py, backend/routes_v1_5.py, frontend/index.html, frontend/i18n.json, tests/, scripts/release-check.ps1, docs/CURRENT_RELEASE.md, docs/RELEASE_PROVENANCE.md, docs/RELEASE_NOTES_V1_7.md

Implement v1.8:

Release foundation:
- Bump backend/frontend version to 1.8.0.
- Create docs/RELEASE_FACTS.json as the release source of truth.
- Add backend/release_brain.py.
- Add routes:
  - GET /release/brain
  - GET /release/provenance
  - GET /release/drift
  - POST /release/drift/check
  - GET /release/warning-budget
- Make /ops/release-check/latest report current v1.8 facts, not stale hardcoded counts.
- Update docs/CURRENT_RELEASE.md, docs/RELEASE_PROVENANCE.md, docs/RELEASE_NOTES_V1_8.md.
- Add tests that fail if active docs contain stale v1.6/v1.7 test counts or stale release provenance.
- Add warning budget registry and fail on unexpected warnings. Approved third-party warnings must be explicit.

Rescue Radar:
- Add backend/rescue_radar.py.
- Add typed models.
- Add routes:
  - GET /rescue/radar
  - GET /rescue/radar/{case_id}
  - POST /rescue/radar/simulate
  - POST /rescue/outreach/{case_id}
  - GET /rescue/interventions
- Implement deterministic early-warning patterns for arrears growth, low headroom, high obligations, missing income proof, income contradiction, active duplicate request, hardship, family pressure, senior support, connector outage, appeal likelihood, and document trust risk.
- Ensure radar never mutates policy decisions.
- Require consent for outreach.
- Emit audit/lifecycle events.
- Add Arabic and English beneficiary messages.

Policy Digital Twin:
- Add backend/policy_digital_twin.py.
- Add routes:
  - GET /digital-twin/scenarios
  - POST /digital-twin/run
  - GET /digital-twin/runs/{run_id}
  - GET /digital-twin/runs/{run_id}/impact
  - GET /digital-twin/runs/{run_id}/fairness
  - GET /digital-twin/runs/{run_id}/workload
  - GET /digital-twin/runs/{run_id}/explain
  - GET /digital-twin/runs/{run_id}/compare/{baseline_run_id}
- Support scenario knobs from the PRD.
- Label all scenario decisions simulated and non-binding.
- Enforce that the 20 percent salary cap cannot be relaxed.
- Preserve official baseline recommendations.
- Add deterministic synthetic cohort support.

Evidence Vault:
- Add backend/evidence_vault.py.
- Add routes:
  - POST /cases/{case_id}/evidence-vault/build
  - GET /cases/{case_id}/evidence-vault
  - GET /cases/{case_id}/trust-receipt
  - POST /trust-receipts/verify
  - POST /trust-receipts/tamper-demo
  - GET /trust-receipts/{receipt_id}/public
- Build deterministic hash/Merkle-style trust receipts from evidence graph v2, consent, connectors, rules, lifecycle, actions, appeal, package, signature, e-Seal.
- Public receipt must redact sensitive data.
- Tamper demo must fail verification safely.

Interop Certification Lab:
- Add backend/interop_certification.py.
- Add routes:
  - GET /interop/certification
  - GET /interop/certification/{connector}
  - POST /interop/certification/run
  - GET /interop/onboarding-pack
  - GET /interop/api-marketplace-readiness
  - GET /interop/gsb-onboarding-checklist
  - GET /interop/uaepass-readiness
  - GET /interop/uae-verify-readiness
- Score UAE PASS, GSB, UAE Verify, financial-capacity, bank/loan, notifications, case-management, Tawasul-style support, and API marketplace readiness.
- Score contract schema, auth shape, consent, purpose binding, minimization, audit, trace ID, retry/timeout, circuit breaker, error envelope, redaction, synthetic fixtures, and failure simulation.

Arabic Service Copilot:
- Add backend/service_copilot.py.
- Add routes:
  - POST /copilot/session/start
  - POST /copilot/session/{session_id}/message
  - GET /copilot/session/{session_id}
  - GET /copilot/scripts
  - GET /copilot/safety-case
  - POST /copilot/redteam/run
- Implement deterministic intent handling for case status, result explanation, missing documents, referral explanation, 20 percent cap, appeal guidance, callback booking, language switch, and senior mode.
- Optional LLM can only rephrase approved facts and must be off-safe by default.
- Prompt injection must not change a decision and must emit a safety event.
- Every response must cite source facts.

Mission Control:
- Add backend/mission_control.py.
- Add routes:
  - GET /mission-control
  - GET /mission-control/playbooks
  - POST /mission-control/playbooks/{playbook_id}/run
  - GET /mission-control/tasks
  - POST /mission-control/tasks/{task_id}/complete
  - GET /mission-control/risk-brief
  - GET /mission-control/live-demo-script
- Convert connector outage, SLA breach risk, appeal backlog, security drill failure, consent spike, evidence repair backlog, release drift, and warning budget breach into owner/action/playbook tasks.

Continuous Red Team and Chaos Lab:
- Add backend/redteam_lab.py.
- Add routes:
  - POST /redteam/run
  - GET /redteam/latest
  - GET /redteam/history
  - GET /redteam/coverage
- Implement 20+ drills listed in the PRD.
- Failed drill creates Mission Control incident.

Frontend:
- Keep single-file frontend/index.html and no new dependencies.
- Add top-level National Pilot mode.
- Add six command areas:
  - Rescue Radar
  - Policy Digital Twin
  - Evidence Vault
  - Interop Certification Lab
  - Arabic Service Copilot
  - Mission Control
- Keep v1.7 workspaces.
- Add judge-ready five-minute demo flow.
- Add one-click demo incident, one-click policy scenario, one-click trust receipt tamper demo, one-click interop certification run.
- Add Arabic keys in frontend/i18n.json for every new visible label.
- Preserve RTL and accessibility.

Materials:
- Add docs:
  - docs/RELEASE_NOTES_V1_8.md
  - docs/V1_8_IMPLEMENTATION_SUMMARY.md
  - docs/NATIONAL_HOUSING_RESILIENCE_OS.md
  - docs/POLICY_DIGITAL_TWIN_GUIDE.md
  - docs/RESCUE_RADAR_PLAYBOOK.md
  - docs/EVIDENCE_VAULT_TRUST_RECEIPT.md
  - docs/INTEROP_CERTIFICATION_PACK.md
  - docs/UAE_PLATFORM_ALIGNMENT_V1_8.md
  - docs/ARABIC_SERVICE_COPILOT_SAFETY_CASE.md
  - docs/REDTEAM_CHAOS_LAB.md
  - docs/MISSION_CONTROL_RUNBOOK.md
  - docs/JUDGE_PACKET_V1_8.md
  - docs/RUN_OF_SHOW_V1_8.md
  - docs/PILOT_MOU_TEMPLATE.md
  - docs/TRAINING_AND_ADOPTION_PLAN.md
  - docs/DATA_RETENTION_AND_PURGE_PLAN.md
  - docs/PROCUREMENT_SECURITY_QUESTIONNAIRE.md
  - docs/ACCESSIBILITY_WCAG_2_2_AA_REPORT.md
- Add material routes:
  - GET /materials/v1.8/judge-packet
  - GET /materials/v1.8/run-of-show
  - GET /materials/v1.8/interop-certification-pack
  - GET /materials/v1.8/policy-digital-twin-guide
  - GET /materials/v1.8/evidence-vault-guide
  - GET /materials/v1.8/copilot-safety-case

Contracts and docs:
- No public write route should use raw dict bodies unless explicitly justified and tested.
- Regenerate docs/api/openapi.json.
- Regenerate docs/POSTMAN_COLLECTION.json.
- Update README.md, AGENTS.md, docs/PRODUCTION_READINESS.md, docs/API_GUIDE.md if needed.
- Make all active docs current for v1.8.

Testing:
- Target 420+ tests and 0 unexpected warnings.
- Add focused tests for:
  - version consistency v1.8
  - release brain and release drift
  - warning budget
  - rescue radar
  - policy digital twin
  - evidence vault and trust receipts
  - interop certification
  - Arabic service copilot
  - Mission Control
  - red-team chaos lab
  - material routes
  - frontend v1.8 static surfaces
  - i18n coverage
  - no raw dict routes
  - OpenAPI/Postman current
  - no real PII/workbook/credentials

Update scripts/release-check.ps1:
- Require 45+ gates.
- Require 420+ tests.
- Require v1.8.0 version consistency.
- Require current release facts.
- Require release provenance current.
- Require all v1.8 modules/routes/materials.
- Require OpenAPI/Postman current.
- Require 0 unexpected warnings.

Run before finishing:
$env:PYTHONPATH="."; python -B -m pytest tests\ -q -p no:cacheprovider
powershell -ExecutionPolicy Bypass -File scripts\release-check.ps1
git status --short --branch

Finish with:
- implemented feature summary
- exact test result
- exact release-check result
- files changed
- known limitations
- suggested commit message
```

## Final Winning Narrative

v1.8 should be presented as:

> Agent Sanad is the National Housing Resilience OS: it finds arrears risk early, simulates policy safely, explains every rule, verifies every evidence chain, guides citizens in Arabic, and proves operational readiness before a single real integration is switched on.

That is the hackathon-level jump: from "AI agent for one service" to "trusted government service operating system."
