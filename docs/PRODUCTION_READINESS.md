# Agent Sanad — Production Readiness Assessment

An honest engineering evaluation: what is production-shaped **today**, what is
mocked **by design** for the hackathon, and exactly what a ministry pilot
requires. Written the way we would hand it to an MOEI technical committee —
no overclaiming.

---

## 1. What is genuinely production-grade today

| Area | Status | Evidence |
|---|---|---|
| **Decision core** | Production-grade | Deterministic `decide()`; Rules 1–3 + assessment matrix; externalized thresholds in `config.yaml`; zero LLM on the money path; benchmarked at 94.6% path-match on 522 held-out real 2025 decisions |
| **Data contracts** | Production-grade | Pydantic v2 everywhere, `extra="forbid"`; the engine consumes only validated objects; `MockApplication` validates citizen input before anything touches a Case |
| **State machine** | Production-grade | Canonical 8-state journey emitted as append-only audit events with actor + reason + mock flag; UI renders from the real events, not a hard-coded picture |
| **Auditability** | Production-grade pattern | Append-only `AuditLog`; every adapter call, rule firing, state transition, and officer action (OFF-01) recorded; request-id correlation across structured JSON logs |
| **Security boundaries** | Production-grade pattern | Document text untrusted (RSK-01); LLM read-only by construction; XSS-escaped rendering; PII-free synthetic fixtures; real workbook gitignored and verified untracked by tests |
| **Error contract** | Production-grade | All errors return `{error_code, message, path, app_version}` (PRD §5.5); no framework tracebacks leak to clients |
| **Build integrity** | Production-grade | Frontend pins `CLIENT_BUILD`; `/healthz` returns `app_version`; mismatch (stale server process) surfaces an actionable banner instead of raw 404s; a regression test forbids the two pins from drifting |
| **Test discipline** | Production-grade | 59 automated tests: policy regression per case, API contracts, state-machine contract, governance/PII, custom-application flows, injection-cannot-override |
| **Reliability** | Production-grade pattern | Offline-first; cached fallbacks on extraction and reasoning; UI retry affordances; one-command launchers that refuse to start over a stale process |

## 2. What is mocked by design (and how it swaps in pilot)

Per PRD v1.1 §5.3, integrations are **contract-true adapters**: production-shaped
interfaces whose bodies return fixtures. The workflow core never changes when
the body is replaced.

| Mock | Pilot replacement | Contract that stays fixed |
|---|---|---|
| UAE PASS verification screen | Real UAE PASS OAuth/OIDC redirect flow | `ApplicantProfile` |
| Loan adapter | MOEI loan-system API | `LoanData` |
| Arrears adapter | Arrears ledger API | `ArrearsData` |
| Salary verification | Financial-services verification API | verified income + variance |
| Document validation | Malware/type scanning + storage service | `DocumentManifest` |
| Salary-certificate parse | Production OCR + extraction service | `IncomeEvidence` (Pydantic-gated) |

## 3. Genuine gaps for a ministry pilot (the honest list)

These are **not** demo defects — they are the scoped pilot work, in priority order:

1. **Persistence** — cases, applications, audit events, and officer actions are
   stateless per-request today. Pilot needs a datastore (PostgreSQL) with an
   append-only audit table and retention policy.
2. **Real identity & authorization** — UAE PASS OAuth for citizens; SSO + role
   model (officer / supervisor / auditor) for the workbench; session management.
3. **Real Programme integrations** — replace the five adapter bodies; add the
   retry/timeout/circuit-breaker layer around real network calls.
4. **Document pipeline** — real upload, virus scanning, storage with encryption
   at rest, production OCR with the existing Pydantic gate.
5. **Deployment** — TLS, containerization, environment configs, monitoring and
   alerting on the structured logs, backup/DR.
6. **Compliance & assurance** — penetration test, data-protection review (PII
   residency), accessibility (WCAG), full Arabic localization.
7. **Officer workflow depth** — durable queues, assignment, SLA timers,
   supervisor escalation paths.

None of these touch the decision engine, the rule catalog, the schemas, or the
audit model — that is the point of the architecture.

## 4. Demo posture

The demo runs fully offline from synthetic fixtures with one optional live
touch (synthetic GOLDEN certificate parse, cached fallback). A presenter keeps
the 13 sample cases available in both the beneficiary flow ("Sample case"
picker) and the officer queue, while judges can submit **custom applications**
through the same deterministic engine to prove it is not hard-coded.

---

*Summary line for the committee: the governance core is built and validated;
pilot work is integration and operations, not invention.*
