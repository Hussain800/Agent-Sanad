# Agent Sanad — Architecture & Engineering Depth

**Track 1 · Sheikh Zayed Housing Programme · UAE MOEI**
**Agentera Hackathon · 2026**

---

## Why this exists

Most hackathon agents are a prompt loop wrapping a chat model. They demo well for 90 seconds and collapse on the second question. Agent Sanad is built to the **IBM Research agent-engineering playbook** ([7 skills to build AI Agents by IBM Research](../7%20skills%20to%20build%20AI%20Agents%20by%20IBM%20Research.md)) — the seven disciplines that separate a demo from a system a ministry can actually pilot.

This document is the architecture map. Every subsystem ties back to one or more of the seven skills, and to a rubric criterion.

---

## The LLM / deterministic / human boundary

The single most important diagram in the project.

```
┌─────────────────────────────────────────────────────────────────┐
│  LLM                  Deterministic code           Human officer │
│  (read-only)          (decides everything          (exceptions   │
│                        financial)                   only)        │
├─────────────────────────────────────────────────────────────────┤
│  - read text          - validate completeness     - approve      │
│  - extract fields     - compute 20% headroom      - adjust       │
│    into typed JSON    - choose path               - escalate     │
│  - write reasoning    - fire rule IDs             - sign off     │
│    text               - classify risk/conf                       │
│                       - enforce Rules 1-3                        │
│                       - route escalation                         │
│                                                                  │
│  MUST NEVER:          MUST NEVER:                 MUST NEVER:    │
│  - compute money      - invent facts not in       - bypass the   │
│  - decide a path        validated schemas           audit log    │
│  - approve/reject     - call the LLM for a                       │
│  - write state          number                                   │
└─────────────────────────────────────────────────────────────────┘
```

This is what makes the system **credible for a Finance department**. The LLM cannot move money. The deterministic engine cannot hallucinate.

---

## System topology

```
                          Beneficiary             Officer
                              │                      │
                              ▼                      ▼
                  ┌───────────────────────────────────────┐
                  │       Frontend (single-page)          │
                  │   beneficiary journey + officer card  │
                  │   audit drawer + impact panel         │
                  └────────────────┬──────────────────────┘
                                   │  POST /demo/run/{case_id}
                                   ▼
                  ┌───────────────────────────────────────┐
                  │           FastAPI app (one endpoint)  │
                  └──┬──────────────────────────────────┬─┘
                     │                                  │
                     ▼                                  ▼
        ┌─────────────────────────┐         ┌─────────────────────┐
        │  Orchestrator           │         │  Append-only        │
        │  (case assembly)        │────────▶│  audit log          │
        └─┬───────────────────────┘         └─────────────────────┘
          │
          ├──▶ UAE PASS adapter ──┐
          ├──▶ Loan adapter ──────┤  fixture-backed,
          ├──▶ Arrears adapter ───┤  contract-true
          ├──▶ Doc Validation ────┤  (5 adapters)
          └──▶ Salary Verify ─────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  Extraction layer       │ ── live PDF parse OR
        │  (cached fallback)      │    cached fixture; never blocks
        └─┬───────────────────────┘
          │
          ▼
        ┌─────────────────────────┐
        │  Deterministic engine   │ ── decide()
        │  (the moat)             │    Rules 1-3 + assessment matrix
        └─┬───────────────────────┘
          │
          ▼
        ┌─────────────────────────┐
        │  Confidence + risk      │
        │  + report builder       │
        └─┬───────────────────────┘
          │
          ▼
        Section-8 RecommendationReport (12 official fields)
        + audit events + benchmark metrics
```

---

## IBM Research's 7 skills → where Agent Sanad ships each one

| # | Skill (IBM) | What it means | Where it lives in Agent Sanad |
|---|---|---|---|
| **1** | **System design** | Orchestrate LLM, tools, state, sub-services without spaghetti | Hard LLM/deterministic/human boundary (above) · single FastAPI orchestrator at `backend/app.py` · explicit state assembly in `adapters/build_case` · no agent framework — just a typed pipeline |
| **2** | **Tool & contract design** | Strict, typed schemas so the model can't fill gaps with imagination | Every payload is a Pydantic v2 model with `extra="forbid"` ([`backend/schemas.py`](../backend/schemas.py)) · the 5 adapters expose typed contracts ([`backend/adapters/__init__.py`](../backend/adapters/__init__.py)) · policy rules externalized in [`config.yaml`](../backend/policy/config.yaml) with `PolicyConfig` validation |
| **3** | **Retrieval engineering** | Make sure the agent works on signal, not noise | Five fixture-backed adapters retrieve the 7 fields the brief says are "already available within the Programme" — no manual entry, no RAG ambiguity · salary cert extraction either parses live (`SANAD_LIVE_EXTRACTION=1`) or falls back to the verified fixture ([`backend/extraction.py`](../backend/extraction.py)) |
| **4** | **Reliability engineering** | Survive when components fail | `LOCAL_MOCK_MODE=true` default — demo runs offline · extraction has cached fallback on any parse error ([`extraction.py:79–85`](../backend/extraction.py)) · LLM reasoning has cached fallback on any error ([`reasoning.py:65–98`](../backend/reasoning.py)) · runtime-error banner + retry in the UI ([`frontend/index.html`](../frontend/index.html)) |
| **5** | **Security & safety** | Treat input as adversarial; keep the agent un-weaponizable | Document text is **untrusted** — `RSK-01` flag fires on instruction-like text but the rules never change · LLM is read-only: cannot decide, cannot write state, cannot call the engine · all UI strings escaped against XSS ([`index.html` `esc()`](../frontend/index.html)) · raw workbook gitignored; PII never displayed · CONTRA test case asserts injection doesn't bend policy |
| **6** | **Evaluation & observability** | "It seems better" is not a deployment criterion | **Historical benchmark** ([`benchmark/`](../benchmark/)) — replays the engine over 1,960 real 2023–25 decisions; 94.6% path-match on held-out 2025 · append-only audit log surfaces every adapter call, rule firing, and decision step · 11 pytest cases cover 5 demo scenarios + extraction modes + API contract · every `AuditEvent` stamps `latency_ms` and `mock_mode` |
| **7** | **Product thinking** | Build for the human on the other end | Two surfaces: beneficiary (status only) and officer (full evidence) · plain-language reasoning per case · confidence band visible next to recommendation · exception cases get distinct visual treatment (success/warning/danger/info bands) · "Why this plan?" drawer is the trust centerpiece |

---

## How this maps to the 100-point rubric

| Rubric criterion (weight) | Skills it leans on | Proven by |
|---|---|---|
| **Agentic Decision Intelligence (25)** | 1, 2, 3 | Golden case runs end-to-end with zero human input · 5 adapters retrieve all Programme data · the engine — not the LLM — picks the path |
| **Policy Compliance & Governance (25)** | 1, 5, 6, 7 | Rules 1–3 in deterministic code ([`engine.py`](../backend/policy/engine.py)) · audit trail · confidence band · officer escalation · injection blocked · 11 tests |
| **Technical Excellence & Data Integration (20)** | 1, 2, 3, 4 | Five labeled adapters with typed contracts · single endpoint · FastAPI + Pydantic v2 · offline-mode resilience |
| **Impact on Service Transformation (15)** | 6 | 5 days → <1 second measured · benchmark panel (94.6%) · zero-bureaucracy framing |
| **Demo, Explainability & UX (15)** | 4, 7 | Audit drawer · distinct exception banners · beneficiary journey · runs with Wi-Fi off |

The **two 25-point criteria** (50 points) are the heart of the rubric, and they're exactly what skills 1, 2, 5, and 6 unlock. Most teams will optimize for skills 4 and 7 (demo + product). Agent Sanad optimizes for **all seven**, with the historical benchmark as the single asset that pushes three criteria at once.

---

## The honest claims

| Claim | Number | Source |
|---|---|---|
| Path-match accuracy on unseen 2025 cases | **94.6%** | `benchmark/run.py` on the real workbook (n=522) |
| 20% cap compliance on plans the engine actively sets | **100%** | by construction — the engine targets ≤ 20% |
| Premium deviation vs officer (median) | AED 557 | benchmark — officers chose gentler premiums in 79.8% of UPDATE cases |
| Months deviation vs officer (median) | 10 | benchmark — same discretion as above |
| Determinism on re-run | **100%** | temperature 0; no randomness on the decision path |
| Manual processing time → Agent Sanad draft | ~5 working days → **<1 second** | brief vs. measured `latency_ms` |

**What we do not claim:** exact reproduction of the officer's premium and months. Officers apply discretion the data doesn't fully encode (see PRD v1.1 §9.5). That discretion is *deliberately* routed to a human — it's the governance feature, not a bug.

---

## v1.1 functional completion (current branch)

The branch grew the demo from 5 to **13 deterministic cases**, all derived from the v1.1 PRD assessment matrix, exercising every branch of `decide()`.

| Case | Fires | Recommendation | Path |
|---|---|---|---|
| HIGH_OBLIGATIONS | OBL-01 + CAP-02 + AFF-01 | Refer to employee | UPDATE_INSTALLMENT |
| PERIOD_BREACH    | TEN-01 + CAP-02 + AFF-01 | Refer to employee | UPDATE_INSTALLMENT (period Fail) |
| HARDSHIP         | HARD-02                  | Approve           | TRANSFER_ARREARS |
| ZERO_OR_MISSING_INCOME | DOC-02             | Request documents | NONE |
| LOW_INCOME_PER_MEMBER  | FAM-01 + CAP-02 + AFF-01 | Approve     | UPDATE_INSTALLMENT (confidence lowered) |
| UNVERIFIED_HARDSHIP    | HARD-01           | Refer to employee | TRANSFER_ARREARS |
| PROMPT_INJECTION_ONLY  | RSK-01 + CAP-02 + AFF-01 | Approve     | UPDATE_INSTALLMENT (policy unchanged by injection) |
| HIGH_CAPACITY_UPDATE   | CAP-02 + AFF-01   | Approve           | UPDATE_INSTALLMENT (real headroom) |

### Audit drawer — six evidence-linked trace sections

1. **State timeline** — derived from real `AuditEvent.state_to` transitions (v1.1 §7, full 8-state journey): Submitted → IdentityLinked → DataRetrieved → Extracting → Validating → PolicyRun → RecommendationReady / NeedsDocuments / Refer / Rejected → Closed.
2. **Adapter source map** — the five integrations and what each returns.
3. **Rule trace** — every fired rule with plain-language meaning + colour-coded effect.
4. **Calculation trace** (Rule 1) — income, EMI, 20% cap, headroom, arrears, premium, months, deduction rate.
5. **Period trace** (Rule 2) — remaining term, additional months, pass/fail + explanation.
6. **Security trace** — injection flag, income variance, contradiction flag, extraction source, and the explicit statement that document text never overrides policy.

### v1.1 app experience (multi-screen flow)

The frontend is a hash-routed multi-screen SPA (one offline file, no frameworks):
**Landing → UAE PASS (mock) → Application stepper (Programme data → Financial
details → Documents → Review) → Processing (animated from real audit
transitions) → Beneficiary result**, plus a separate **Officer portal** with a
case-queue sidebar that holds all dense evidence (Section-8, 6-section trace,
audit feed, benchmark, officer actions, IBM strip).

Custom applications: `MockApplication` (Pydantic, `extra="forbid"`, no PII
fields) → `backend/applications.py` builds a synthetic Case with canonical
state transitions → the **existing** `decide()` rules. Endpoints:
`POST /applications/mock` (snapshot) and `POST /applications/mock/decide`
(same envelope as `/demo/run`). The beneficiary sees status + one plain
sentence; the officer sees everything.

### v1.1 §5.5 endpoints

`/demo/run/{case_id}` remains the main demo path. Added: `GET /benchmark`, `GET /cases/{id}`, `GET /cases/{id}/audit`, `POST /cases/{id}/decide` (same envelope as `/demo/run`), and `POST /cases/{id}/officer-action` (stateless human action — validates an `OfficerAction`, records an OFF-01 audit event; adjust/escalate require a reason code). Case-creation lifecycle write endpoints and persistence are deferred — see [`V1_1_COMPLETION_SUMMARY.md`](./V1_1_COMPLETION_SUMMARY.md).

The officer card shows a per-scenario banner derived from fired rules. The beneficiary view still hides all internal math; the plain-language reason varies per scenario.

Full design rationale and per-case expected outputs: [`V1_1_COMPLETION_SUMMARY.md`](./V1_1_COMPLETION_SUMMARY.md) and [`V1_1_FUNCTIONAL_EXPANSION_SUMMARY.md`](./V1_1_FUNCTIONAL_EXPANSION_SUMMARY.md).

The deterministic policy engine, period module, rule catalog, config, and benchmark scripts are **unchanged**. Honest benchmark claim wording is **unchanged**. No tooling addendum (LangGraph / LangSmith / LlamaIndex / etc.) was added.

---

## v1.1+ tooling layer (final hardening branch)

Per the Tooling Addendum, executed under the rule *"frameworks may orchestrate,
trace, observe — they must never decide the money"*:

- **LangGraph (T1)** — `backend/graph/` wraps the same workflow as the plain
  orchestrator in 10 explicit nodes; `run_policy_engine` calls the existing
  `decide()`. `POST /demo/run-graph/{id}` mirrors `/demo/run`'s envelope and
  falls back to plain on any failure. Equivalence for **all 13 cases** is
  test-enforced and demonstrable live via `GET /demo/compare/{id}`. Default
  orchestrator stays `plain` (`SANAD_ORCHESTRATOR`).
- **Observability (T2)** — `backend/observability/` adds a LangSmith-ready
  trace adapter behind mandatory PII redaction (allow-list + Emirates-ID /
  Arabic / document-text scrubbing). `LANGSMITH_TRACING=false` by default;
  redaction-off + tracing-on refuses to emit. Local audit remains the source
  of truth.
- **Not implemented by decision:** LlamaIndex/LlamaParse (duplicates the
  existing Pydantic-gated extraction for one synthetic certificate), LangChain
  (no boilerplate to remove), CrewAI/AutoGen/Semantic Kernel/DSPy/OpenAI
  Agents SDK (wrong shape for a single governed pipeline). **MCP remains a
  production roadmap item** — the five adapter boundaries are MCP-shaped for a
  future pilot. Full rationale: [`TOOLING_IMPLEMENTATION_SUMMARY.md`](./TOOLING_IMPLEMENTATION_SUMMARY.md).

---

## Files of record

| Concern | File |
|---|---|
| The money path (review personally) | [`backend/policy/engine.py`](../backend/policy/engine.py) |
| Rule 2 (period compliance) | [`backend/policy/period.py`](../backend/policy/period.py) |
| Rule IDs catalog | [`backend/policy/rules.py`](../backend/policy/rules.py) |
| Externalized thresholds | [`backend/policy/config.yaml`](../backend/policy/config.yaml) |
| Typed schemas (single source of truth) | [`backend/schemas.py`](../backend/schemas.py) |
| Five fixture-backed adapters | [`backend/adapters/__init__.py`](../backend/adapters/__init__.py) |
| Live + cached salary extraction | [`backend/extraction.py`](../backend/extraction.py) |
| Cached reasoning per case (offline-safe) | [`backend/reasoning.py`](../backend/reasoning.py) |
| Append-only audit | [`backend/audit.py`](../backend/audit.py) |
| Confidence + risk band | [`backend/confidence.py`](../backend/confidence.py) |
| API surface (one endpoint) | [`backend/app.py`](../backend/app.py) |
| Demo UI (single page) | [`frontend/index.html`](../frontend/index.html) |
| Historical benchmark harness | [`benchmark/`](../benchmark/) |
| Test suite (11 passing) | [`tests/`](../tests/) |

---

*Built to the IBM Research agent-engineering playbook — not a prompt-craft experiment.*
