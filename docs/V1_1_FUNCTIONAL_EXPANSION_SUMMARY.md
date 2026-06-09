# Agent Sanad — v1.1 Functional Expansion Summary

**Branch:** `v1.1-functional-expansion`
**Base:** stable v0.8 on `main`
**Scope:** product depth, not industry tooling

> **Note:** This document covers the **first** expansion step (3 cases: HIGH_OBLIGATIONS, PERIOD_BREACH, HARDSHIP). The branch has since grown to **13 cases** with a state-machine audit timeline, a security trace, and safe v1.1 endpoints. For the complete, current picture see [`V1_1_COMPLETION_SUMMARY.md`](./V1_1_COMPLETION_SUMMARY.md).

---

## What this expansion is — and is not

**It is**

- Three new realistic demo cases derived from the original v1.1 PRD assessment matrix.
- A v1.1-style audit drawer with **five trace sections** (state timeline, adapter map, rule trace, calculation trace, period trace) plus the original raw-feed view.
- Per-scenario officer banners that explain *why* the case landed where it did.
- Per-scenario beneficiary copy that never reveals internal financial math.
- A small impact-panel honesty note.

**It is not**

- LangGraph, LangSmith, LangChain, LlamaIndex / LlamaParse, MCP, CrewAI, AutoGen, Semantic Kernel, DSPy, or any other industry agent framework. The v1.1+ tooling addendum is paused.
- A schema rewrite. The official Section-8 `RecommendationReport` shape is unchanged.
- A manager dashboard or new endpoint.
- A change to the money path. `decide()`, `period.py`, `config.yaml`, `rules.py`, `replay.py`, `score.py` are byte-identical to v0.8.

---

## The three new cases

Every expected value below is what `backend/policy/engine.py decide()` actually outputs for the new fixture — the test assertions are derived from a hand-traced run, not guessed.

### HIGH_OBLIGATIONS — proves the assessment matrix considers obligations

| Field | Value |
|---|---|
| Income / EMI / arrears | AED 20,000 · AED 1,800 · AED 5,500 |
| 20% cap · headroom | AED 4,000 · AED 2,200 |
| Obligations ratio | 0.65 (over 0.60 threshold → OBL-01) |
| **Recommendation** | **Refer to employee** |
| Path | UPDATE_INSTALLMENT (plan still computed within cap) |
| Fired rules | CAP-02 · AFF-01 · OBL-01 |
| 20% compliance · Period compliance | Pass · Pass |
| Risk · Confidence | medium · high |

### PERIOD_BREACH — proves Rule 2 is enforced

| Field | Value |
|---|---|
| Income / EMI / arrears | AED 10,000 · AED 1,800 · AED 30,000 |
| 20% cap · headroom | AED 2,000 · AED 200 |
| Remaining term | 24 months |
| add_premium · add_months | 200 · 150 → exceeds 24 → period_ok=False |
| **Recommendation** | **Refer to employee** |
| Path | UPDATE_INSTALLMENT (plan computed; period fails) |
| Fired rules | CAP-02 · AFF-01 · TEN-01 |
| 20% compliance · Period compliance | Pass · **Fail** |
| Risk · Confidence | high · high |

### HARDSHIP — proves human-centred case handling

| Field | Value |
|---|---|
| Income / EMI / arrears | AED 15,000 · AED 2,000 · AED 8,000 |
| Hardship | `temporary_circumstance_flag=true`, `unverified=false`, note attached |
| **Recommendation** | **Approve** (verified temporary circumstance → HARD-02 branch) |
| Path | TRANSFER_ARREARS · installment unchanged · arrears to loan end |
| Fired rules | HARD-02 |
| 20% compliance · Period compliance | Pass · Pass |

---

## What changed in the audit drawer

The drawer was a single dark scrolling feed in v0.8. In v1.1 it is structured into five sections that map to the v1.1 PRD §7 state machine and §4 rule catalog:

1. **State timeline** — pill chain from `Submitted` through the case's terminal state (Approved / Refer / NeedsDocuments / Rejected). Final state highlighted in brand green.
2. **Adapter source map** — the five integrations (UAE PASS, Loan, Arrears, Document Validation, Salary Verification) with what each returns.
3. **Rule trace** — every fired rule as `ID · meaning · effect`, with the effect (Approve / Refer / Reject / Request / Note) colour-coded.
4. **Calculation trace (Rule 1)** — verified income · current installment · 20% cap · headroom · arrears · additional premium · months · proposed deduction rate · 20% compliance chip.
5. **Period rule trace (Rule 2)** — remaining term · proposed additional months · path · whether the schedule extends past the original end · period compliance chip.

The raw audit feed is preserved beneath the trace as the bottom section, so judges can still see every adapter call and rule firing.

---

## Officer card banners

Above the Section-8 table, a scenario banner now states the case in plain language. Banners are derived from the **report's fired rules** (not the case_id), so the explanation reflects what the engine actually decided. Tones:

| Tone | Cases |
|---|---|
| Danger (red) | ACTIVE, PERIOD_BREACH, NOHEAD/HARD-01 |
| Warning (amber) | MISSING, CONTRA, HIGH_OBLIGATIONS, CAP-01 transfer |
| OK (green) | HARDSHIP (verified temporary circumstance) |

---

## Beneficiary view

Per the v1.1 PRD §12.1, the beneficiary still never sees internal financial calculations — only status + one plain-language reason. The reason now varies per scenario (verified hardship → "your verified circumstance has been recognised"; period breach → "specialist review for timing"; etc).

---

## Impact panel

Numbers are unchanged from v0.8 (panel still pulled from the static `BENCHMARK` block in `app.py`):

- Manual process: ~5 working days
- Agent Sanad draft: <90s (measured per request via `latency_ms`)
- Path-match (held-out 2025): **94.6%**
- UPDATE 20% compliance: **100%** (by construction)
- Premium deviation median: AED 557
- Months deviation median: 10
- Deterministic rerun: 100%

New honesty note printed under the panel: *"Path-match is the honest benchmark claim. Exact premium and duration remain officer-discretion-sensitive."*

---

## File diff against `main`

| File | Status | Notes |
|---|---|---|
| `backend/policy/engine.py` | **untouched** | protected |
| `backend/policy/period.py` | **untouched** | protected |
| `backend/policy/config.yaml` | **untouched** | protected |
| `backend/policy/rules.py` | **untouched** | protected |
| `benchmark/replay.py` · `benchmark/score.py` | **untouched** | protected |
| `backend/schemas.py` | additive — `HardshipEvidence.note` field (per v1.1 PRD §6) |
| `backend/adapters/__init__.py` | additive — 3 new fixtures, `obligations_ratio` + `hardship` knobs |
| `backend/reasoning.py` | additive — cached reasoning for 3 new cases |
| `seeds/cases_v1.json` | additive — 3 new entries |
| `frontend/index.html` | additive — trace sections, scenario banners, per-case journeys, honest-claim note |
| `tests/test_policy.py` | additive — 5 new tests; original 5 still asserted |
| `docs/V1_1_FUNCTIONAL_EXPANSION_SUMMARY.md` | **new** | this file |

Test result: **18 / 18 passing** (13 v0.8 baseline + 5 v1.1 expansion).

---

## Honest benchmark claim wording — unchanged

> *Agent Sanad matches the officers' rescheduling path 94.6% of the time on held-out 2025 cases and every UPDATE plan it sets is within the 20% cap. It does not claim exact reproduction of every premium or duration.*

---

## What is deliberately deferred

- All industry agent tooling (LangGraph, LangSmith, etc.) — addendum paused.
- The remaining v1.1 cases (we shipped 3 of 12 by design; quality > quantity for the demo).
- A separate manager dashboard (zero rubric points; impact panel covers it).
- A bilingual Arabic UI.
- Live PDF OCR for non-golden cases.

---

*Built on the stable v0.8 base. The deterministic policy engine is unchanged. The expansion only deepens what the demo shows about each case.*
