# Agent Sanad — Final Hardening Report

Branch `v1.1-final-hardening-tooling` · base `v1.1-completion-pass-2` (`aab5d8a`).
Seven sequential review passes were run over the whole product before the
tooling addendum was executed. This is the defect ledger and what was done.

---

## Review passes and findings

### 1 · Product/UI reviewer
- Landing → UAE PASS → stepper → processing → result → officer portal flow
  confirmed coherent; mock/offline posture clearly labeled on every surface.
- C-level (left as-is, recorded): native `prompt()` dialogs for officer reason
  codes; stepper circles not click-navigable; duplicated architecture link in
  footer. None affect demo quality; all noted for pilot polish.

### 2 · Frontend robustness reviewer — A-level defects FIXED
| # | Defect | Fix |
|---|---|---|
| A2 | Deep-link to `#/processing` with no submission stranded users on a blank animation screen | Route guard redirects to service entry unless a submission is in flight or a result exists |
| A3 | Submit button accepted double-clicks → duplicate POSTs | `S.submitting` interlock + button disabled with "Submitting…" label; re-enabled on failure path |
| A4 | Rejected promises outside try/catch vanished into the console | Global `unhandledrejection` handler surfaces a visible error banner on the active surface |

### 3 · Backend/API reviewer — A-level defect FIXED
| # | Defect | Fix |
|---|---|---|
| A1 | Missing/malformed JSON bodies raised `RequestValidationError`, bypassing the §5.5 envelope and leaking FastAPI's default `{detail:[…]}` shape | Dedicated `RequestValidationError` handler returns the standard `{error_code: "VALIDATION_ERROR", message, path, app_version}` envelope; regression test added |

Also re-verified: no route conflicts across all 14 routes; `app_version` in
every error envelope; no external network dependency anywhere on the demo path.

### 4 · Policy/safety reviewer — NO CHANGES (by design)
Full 13-case outcome table regenerated and compared against the PRD: every
recommendation, path, fired-rule set, compliance chip, risk level, and
confidence band matches. Protected files diff vs `main`: **empty**.

### 5 · Test/QA reviewer
Suite grew 60 → **84**: +1 malformed-body envelope test, +17 graph
equivalence/fallback/contract tests, +6 observability/redaction tests.

### 6 · Tooling integration reviewer
T1 + T2 implemented, T3 + T4 intentionally skipped — full rationale and
verification commands in
[`TOOLING_IMPLEMENTATION_SUMMARY.md`](./TOOLING_IMPLEMENTATION_SUMMARY.md).

### 7 · Documentation/release reviewer
README, CODING_HANDOFF, ARCHITECTURE, JUDGE_QA, PRODUCTION_READINESS updated;
this report and the tooling summary added; PR opened with full QA checklist.

---

## Honest framing

This is a **production-shaped prototype / pilot-ready architecture**, not a
deployed production system. Deferred pilot work remains exactly as documented
in [`PRODUCTION_READINESS.md`](./PRODUCTION_READINESS.md): real UAE PASS OAuth,
real MOEI integrations, database persistence, deployment hardening,
compliance/security review, accessibility audit, production OCR pipeline.

The benchmark claim is unchanged and honest:

> Agent Sanad matches the officers' rescheduling path 94.6% of the time on
> held-out 2025 cases and every UPDATE plan it sets is within the 20% cap. It
> does not claim exact reproduction of every premium or duration.
