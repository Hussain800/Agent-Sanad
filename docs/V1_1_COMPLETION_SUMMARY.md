# Agent Sanad — v1.1 Product Completion Summary

**Branch:** `v1.1-functional-expansion`
**Base:** `main` (stable v0.8)
**Scope:** functional/product completion of the original v1.1 PRD. **No** industry tooling addendum (LangGraph / LangSmith / LangChain / LlamaIndex / MCP / CrewAI / AutoGen / Semantic Kernel / DSPy / OpenAI Agents SDK) was added.

---

## TL;DR

The branch now ships **13 deterministic demo cases** that exercise every branch of `decide()` plus the assessment matrix, an officer drawer with **6 evidence-linked trace sections** including a complete v1.1 §7 state-machine timeline (**8 states**: Submitted → IdentityLinked → DataRetrieved → Extracting → Validating → PolicyRun → terminal → Closed), **6 safe v1.1 API endpoints** (including a stateless officer-action) on top of the v0.8 `/demo/run` route, and updated docs. The protected money path is untouched. **44 of 44 tests pass** (v1.1 milestone snapshot; current suite: **139 tests, 9 files**). Benchmark wording is unchanged.

### Fourth pass — production hardening

- **Build-version handshake** — frontend pins `CLIENT_BUILD`; `/healthz` returns
  `app_version`; a mismatch (stale uvicorn serving new static files with old
  routes — the cause of the "404 on /cases/GOLDEN" report) shows an actionable
  yellow banner instead of raw errors. A regression test forbids the pins drifting.
- **PRD §5.5 error contract** — every error now returns
  `{error_code, message, path, app_version}`; no framework defaults leak.
- **One-command launchers** — `run.ps1` / `run.sh` set the environment and
  refuse to start on top of an already-bound port 8000 (stale-process trap).
- **`docs/PRODUCTION_READINESS.md`** — honest committee-grade assessment:
  what is production-grade now, what is mocked by design with its pilot
  replacement, and the genuine pilot gap list (persistence, real UAE PASS,
  real integrations, deployment, compliance).
- README rewritten around the real app flow.

### Third pass — the app experience rebuild

The one-page "case-button simulator" UI was replaced with a proper multi-screen
government-service flow (still a single offline HTML file, zero frameworks):

1. **Landing** — branded service entry with "Continue with UAE PASS".
2. **UAE PASS mock** — simulated verification (clearly labeled; no credentials).
3. **Application stepper** — Programme data (retrieved) → Financial details
   (editable) → Documents (status cards) → Review & submit. Sample-case prefill
   or fully custom values.
4. **Processing** — animated agent timeline driven by the real audit states.
5. **Beneficiary result** — status + plain-language reason only.
6. **Officer portal** — queue sidebar (13 samples + last submitted application),
   Section-8, all 6 trace sections, audit feed, benchmark, officer actions, IBM strip.

New custom-application flow (engine untouched): `MockApplication` schema →
`backend/applications.py` → `POST /applications/mock` + `POST /applications/mock/decide`
(same envelope as `/demo/run`). `GET /cases` now also returns picker metadata.
New test file `tests/test_applications.py` proves the app works from **user
input**, including: custom approve, missing-certificate request-docs, active-request
reject, high-obligations refer, period-breach refer, and injection-cannot-override.

### Second completion pass (previous iteration)

- **State machine completed** — added the `Extracting` and `Closed` states so the audit timeline shows the full canonical v1.1 §7 journey.
- **Officer action endpoint** — `POST /cases/{id}/officer-action` (stateless): validates an `OfficerAction` (approve / adjust / escalate; reason code required on adjust/escalate), records an OFF-01 officer-actor audit event, and returns the unchanged deterministic report. Completes the "human owns exceptions" governance story without persistence.
- **Section-8 field-presence tests** — every case's API output is asserted to carry all 12 official fields with non-empty summaries.
- **NONE-path UI cleanup** — gated/rejected/incomplete cases now show "Not generated" / "Not applicable" instead of `0.0%` or empty plan rows.
- **Governance test file** — `tests/test_governance.py`: raw workbook is gitignored and untracked, fixtures are all-synthetic, risky cases route to a human, referred cases carry a fired rule.

---

## What is now complete from v1.1 PRD

| PRD section | What | Where |
|---|---|---|
| §1–§3 framing, scope, default-autonomous routing | ✔ done | docs/ARCHITECTURE.md |
| §4 deterministic engine (Rules 1–3 + assessment matrix + rule catalog) | ✔ done | backend/policy/* — **untouched** |
| §5 architecture (FastAPI + Pydantic + 5 adapters + LLM/det/human boundary) | ✔ done | backend/ |
| §5.5 REST endpoints (10 endpoints listed; the safe subset + stateless officer-action shipped) | ✔ mostly — see below | backend/app.py |
| §6 typed schemas including `HardshipEvidence.note` | ✔ done | backend/schemas.py |
| §7 state machine — Submitted → IdentityLinked → DataRetrieved → Validating → PolicyRun → terminal | ✔ done as audit events | backend/audit.py, backend/adapters/__init__.py, backend/app.py |
| §8 document extraction with cached fallback + live golden | ✔ done | backend/extraction.py |
| §9 historical benchmark — replays engine on 1,960 real decisions | ✔ done | benchmark/* — **untouched** |
| §10 governance + audit + injection defense + PII discipline | ✔ done | backend/policy/engine.py, backend/audit.py, frontend/index.html |
| §10.3 confidence band | ✔ done | backend/confidence.py |
| §11 evaluation / observability (regression tests + audit trail + LOCAL_MOCK_MODE) | ✔ done | tests/, app.py |
| §12 officer workbench + thin beneficiary view + Impact panel | ✔ done | frontend/index.html |
| §13 demo cases | ✔ **13 of 12+** cases (see below) | backend/adapters/__init__.py, tests/test_policy.py |
| §14 demo script (3-min live + 90-sec backup) | ✔ done | docs/DEMO_SCRIPTS.md |
| §15 slide assets | ✔ done | docs/SCREENSHOTS.md |
| §17 repo structure | ✔ done | — |
| §19 judge Q&A | ✔ done + v1.1 questions added | docs/JUDGE_QA.md |
| §20 go/no-go | ✔ checklist below | this file |

---

## Total number of demo cases: **13**

### Original v0.8 (5)
1. `GOLDEN` — Approve via UPDATE_INSTALLMENT
2. `NOHEAD` — Refer via TRANSFER_ARREARS (HARD-01 + CAP-01)
3. `MISSING` — Request documents (DOC-01)
4. `ACTIVE` — Reject at Rule 3 gate (ACTIVE-01)
5. `CONTRA` — Refer (INC-01 + RSK-01)

### v1.1 functional expansion (3)
6. `HIGH_OBLIGATIONS` — Refer (OBL-01); UPDATE plan still computed within cap
7. `PERIOD_BREACH` — Refer (TEN-01); 20% Pass · Period Fail
8. `HARDSHIP` — Approve via TRANSFER_ARREARS (verified HARD-02)

### v1.1 completion (5)
9. `ZERO_OR_MISSING_INCOME` — Request documents (DOC-02); cert received but income unverifiable
10. `LOW_INCOME_PER_MEMBER` — Approve (FAM-01 lowers confidence); plan still within cap
11. `UNVERIFIED_HARDSHIP` — Refer (HARD-01 + unverified)
12. `PROMPT_INJECTION_ONLY` — Approve with RSK-01 logged; **policy unchanged by injected text**
13. `HIGH_CAPACITY_UPDATE` — Approve via UPDATE; engine uses real headroom (AED 4,000)

Each expected output is **derived from a hand-traced run of `decide()`** before the test was written, not guessed. The fixtures live in [`backend/adapters/__init__.py`](../backend/adapters/__init__.py) with engine-trace comments above each block.

---

## What full v1.1 items remain deferred

| Item | Why deferred |
|---|---|
| `POST /cases` / `POST /cases/{id}/retrieve` / `POST /cases/{id}/documents` / `POST /cases/{id}/extract` (case-creation lifecycle write endpoints) | The demo journey is deterministic and case-id-keyed; building real upload/persistence adds risk without rubric value. The safe **read** subset of v1.1 §5.5 (`GET /cases/{id}`, `GET /cases/{id}/audit`, `GET /benchmark`) plus a stateless `POST /cases/{id}/officer-action` are shipped. |
| Persistent officer-action history (writing OfficerAction to a store) | The endpoint exists and is validated/audited statelessly; durable persistence needs a database we deliberately don't ship. |
| SQLite case store | Stateless fixtures are sufficient for the demo. |
| Real UAE PASS / OAuth | Mock identity per PRD §3.2. |
| Multi-agent orchestration | Per PRD §3.2 — explicitly cut. |
| Bilingual Arabic UI | Stretch goal. |
| Real OCR for arbitrary PDFs | Fragile; cached extraction with live-golden-only stays. |
| Manager / KPI dashboard | Zero rubric points (PRD §3.2 cut). |
| Remaining v1.1 §13 cases beyond the 13 above | Diminishing returns; current 13 already cover every branch of `decide()`. |
| Real LangSmith / LangGraph / LlamaIndex (tooling addendum) | User explicitly forbade until the product is rehearsed. |

---

## Protected files status — **all unchanged**

```
backend/policy/engine.py        ✓ untouched
backend/policy/period.py        ✓ untouched
backend/policy/config.yaml      ✓ untouched
backend/policy/rules.py         ✓ untouched
benchmark/replay.py             ✓ untouched
benchmark/score.py              ✓ untouched
```

Verify with: `git diff main -- backend/policy/engine.py backend/policy/period.py backend/policy/config.yaml backend/policy/rules.py benchmark/replay.py benchmark/score.py` → **empty**.

---

## Tests: 44 / 44 passing

```
tests/test_demo_api.py        (24 tests)
  ├─ healthz / demo-run contract / static-UI surfaces / request-id roundtrip
  ├─ architecture IBM-7 mapping
  ├─ state machine: full Submitted→…→Closed journey per case   (v1.1 §7)
  ├─ phase5 required cases show all state markers
  ├─ audit events carry actor + mock_mode                       (v1.1 §6)
  ├─ GET /benchmark honest claim + metrics                      (v1.1 §5.5)
  ├─ GET /cases/{id} · GET /cases/{id}/audit · POST /cases/{id}/decide
  ├─ officer-action: approve audits OFF · adjust requires reason · 404
  ├─ every case returns all 12 Section-8 fields
  ├─ NONE-path cases show clean N/A compliance
  ├─ no real PII in any case payload
  └─ prompt-injection does not change decision via API

tests/test_policy.py          (18 tests)
  ├─ 5 original v0.8 cases + extraction (cached + live)
  ├─ cases 6–8  (HIGH_OBLIGATIONS, PERIOD_BREACH, HARDSHIP)
  ├─ cases 9–13 (ZERO_OR_MISSING_INCOME, LOW_INCOME_PER_MEMBER,
  │              UNVERIFIED_HARDSHIP, PROMPT_INJECTION_ONLY, HIGH_CAPACITY_UPDATE)
  ├─ original-five-unchanged regression
  └─ all-8 + all-13 route-through-endpoint

tests/test_governance.py      (2 tests in this file group; 5 assertions)
  ├─ raw workbook gitignored + not tracked
  ├─ fixtures use only synthetic identifiers
  ├─ risky cases route to human (never auto-approve)
  └─ referred cases carry a fired rule

============ 44 passed ============
```

---

## How to run the app

```powershell
cd "C:\Hussain new\Agent-Sanad"
$env:PYTHONPATH = "."
$env:LOCAL_MOCK_MODE = "true"
$env:SANAD_LIVE_EXTRACTION = "1"
python -B -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` and click any of the 13 case buttons. The demo runs fully offline; no live LLM or external service is required.

---

## How to verify all cases

### Automated

```powershell
python -B -m pytest tests\ -q -p no:cacheprovider
```

Expect: `44 passed`.

### Live API (in PowerShell)

```powershell
$cases = @(
  "GOLDEN","NOHEAD","MISSING","ACTIVE","CONTRA",
  "HIGH_OBLIGATIONS","PERIOD_BREACH","HARDSHIP",
  "ZERO_OR_MISSING_INCOME","LOW_INCOME_PER_MEMBER",
  "UNVERIFIED_HARDSHIP","PROMPT_INJECTION_ONLY","HIGH_CAPACITY_UPDATE"
)
foreach ($c in $cases) {
  $r = Invoke-RestMethod -Method Post "http://127.0.0.1:8000/demo/run/$c"
  Write-Host "$c  →  $($r.report.recommendation) / $($r.report.proposed_plan.path)"
}
```

Also exercise the v1.1 endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/benchmark
Invoke-RestMethod http://127.0.0.1:8000/cases/GOLDEN
Invoke-RestMethod http://127.0.0.1:8000/cases/GOLDEN/audit
Invoke-RestMethod -Method Post http://127.0.0.1:8000/cases/GOLDEN/decide
Invoke-RestMethod -Method Post http://127.0.0.1:8000/cases/GOLDEN/officer-action -Body '{"action":"approve"}' -ContentType 'application/json'
```

### Full endpoint list (10)

| Method · Path | Purpose |
|---|---|
| `GET /healthz` | liveness + mock_mode + policy_version |
| `GET /` | single-page demo UI |
| `GET /architecture` | IBM 7-skills mapping (USP surface) |
| `GET /cases` | list the 13 seeded case ids |
| `GET /benchmark` | benchmark metrics + honest claim wording |
| `GET /cases/{id}` | assembled Case snapshot (no policy run) |
| `GET /cases/{id}/audit` | audit trail for the assembled case |
| `POST /demo/run/{id}` | **main demo path** — full retrieve→decide→report envelope |
| `POST /cases/{id}/decide` | same envelope as /demo/run (v1.1 route name) |
| `POST /cases/{id}/officer-action` | stateless human action; validates + OFF-01 audit |

---

## Honest benchmark wording — **unchanged**

> *Agent Sanad matches the officers' rescheduling path 94.6% of the time on held-out 2025 cases and every UPDATE plan it sets is within the 20% cap. It does not claim exact reproduction of every premium or duration.*

Numbers (also unchanged):
- Path-match (held-out 2025): **94.6%** (n=522)
- UPDATE 20% compliance: **100%** (by construction)
- Premium dev median: AED 557
- Months dev median: 10
- Deterministic rerun: 100%

The benchmark script was not rerun — the numbers continue to come from the prior offline run against the workbook, surfaced in [`/benchmark`](../backend/app.py) and the impact panel.

---

## Tooling addendum — explicitly NOT added

No LangGraph. No LangSmith. No LangChain. No LlamaIndex. No LlamaParse. No MCP. No CrewAI. No AutoGen. No Semantic Kernel. No DSPy. No OpenAI Agents SDK. The v1.1+ Tooling Addendum (`Agent_Sanad_PRD_v1.1_Tooling_Addendum.md`) remains paused.

The doctrine — **LLM reads, deterministic code decides, human owns exceptions** — is unchanged.

---

## Final architecture line

> *Agent Sanad is a governed casework agent for housing-loan arrears rescheduling. The deterministic Python engine applies the 20% cap, picks the rescheduling path, computes the plan, and fires rule IDs. The LLM only extracts and explains. The officer owns the final sign-off. We validated the engine against 1,960 real Programme decisions and matched the officers' path 94.6% of the time on the held-out 2025 set.*
