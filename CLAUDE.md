# CLAUDE.md — Operating Rules for Agent Sanad

> Read first, every session. Most important rules at the top. Be a disciplined
> senior engineer, not a chatbot. Verify facts from files/commands — never from
> commit messages or memory. Deep contributor detail is in `AGENTS.md`.

## 1. Current release — source of truth (VERIFIED from code, 2026, not from messages)

| Fact | Verified value | Where to confirm |
|---|---|---|
| Version | **1.8.0** | `backend/app.py` `APP_VERSION`; `frontend/index.html` `CLIENT_BUILD`; `docs/RELEASE_FACTS.json` |
| Tests | **431 passing** (`pytest -q` → `431 passed`) | run the suite; do not trust doc counts |
| Test files | **52** | `ls tests/*.py \| wc -l` |
| Mounted routes | **189** API routes | `len([r for r in app.routes if hasattr(r,'methods')])` |
| Doctrine | "LLM reads and explains. Deterministic code decides. Human owns the exception." | `docs/RELEASE_FACTS.json` |

**Release-doc rule:** `docs/RELEASE_FACTS.json` + a freshly-run `pytest` are the
truth. **Never downgrade** version/test/route/badge claims using stale local
context. When docs disagree, fix the docs UP to verified reality — never edit
verified code/badges DOWN to match a stale doc. `RELEASE_FACTS.json`
`tests_target` is a TARGET (currently 420; actual 431 ≥ target) — do not conflate
it with the actual count. README badge, `CURRENT_RELEASE.md`, and `AGENTS.md`
were refreshed to 431/v1.8.0 — re-verify before each release and keep them in sync.

## 2. Repo freshness (do this before any work)

```bash
git fetch origin --prune
git rev-parse HEAD; git rev-parse origin/main   # MUST be equal
```
- Local branch must equal `origin/main` before starting. Always work on the
  latest. If `HEAD != origin/main` or the tree is dirty → **stop and ask**.
- Work on a fresh branch (`claude/<task>`). Never commit to `main` without
  explicit approval. Any merge conflict → stop and ask. Never resolve a
  conflict by accepting an older local file over newer `origin/main`.

## 3. Doctrine — the boundary (never cross it)

Agent Sanad is a **governed MOEI housing-loan arrears rescheduling casework
system**. Not a chatbot, not an autonomous AI judge, not generic RAG.

| Layer | May | Must never |
|---|---|---|
| **LLM** | extract facts, summarize evidence, draft explanations, translate/format already-computed output | decide recommendations, invent thresholds, approve/reject money, change benchmark claims, bypass policy |
| **Deterministic Python** | 20% deduction cap · repayment-period compliance · active-request blocking · document-completeness gates · update/transfer/referral path · risk/escalation | call the LLM for a number |
| **Human officer** | exceptions · contradictions · hardship/unemployment · overrides · final complex review | bypass the audit log |

## 4. Protected files — STOP and ask before editing

```
backend/policy/engine.py    backend/policy/period.py
backend/policy/config.yaml   backend/policy/rules.py
benchmark/replay.py          benchmark/score.py
```
To touch one, first state: (1) the exact bug, (2) why it can't be fixed in
adapters/schemas/UI/report-formatting/tests, (3) tests proving no regression.
Then wait for approval.

> **Known issue:** the admin "live policy config" feature (`backend/admin.py`)
> rewrites `config.yaml` at runtime; several tests trigger it and leave the file
> dirty (trailing blank lines; policy values unchanged). Before committing, run
> `git checkout -- backend/policy/config.yaml` if it shows as modified after a
> test run. Do **not** commit that whitespace churn.

## 5. Validation — never say "done" without it

```bash
$env:PYTHONPATH="."
python -B -m pytest tests\ -q -p no:cacheprovider     # expect: 431 passed
git checkout -- backend/policy/config.yaml            # if dirtied by tests
```
- Backend/test/doc-claim change → run the full suite.
- Demo-behavior change → boot (`.\run.ps1`) and smoke `/healthz`, `/`,
  `POST /demo/run/GOLDEN` (expect 200; `app_version` == `CLIENT_BUILD`).
- After docs edits → grep for stale version/test/route claims you may have
  introduced or missed.
- Always end with `git status` + a diff summary. Fix failures unless the fix
  needs a protected-file change (then stop and ask).

## 6. Honesty guards

- Benchmark claim is fixed: *"matches the officers' rescheduling path 94.6% on
  held-out 2025 cases; every UPDATE plan within the 20% cap; does not claim
  exact reproduction of premium or duration."* Never inflate.
- Classify the product as a **production-shaped prototype**, not a deployed
  system. Don't hide pilot gaps (real UAE PASS OAuth, real MOEI integrations,
  persistence at scale, deployment, monitoring, security/compliance review,
  pilot validation). Mock adapters are mocks — say so.
- Synthetic identifiers only (`APP-*`, `AGR-*`, masked names). Never commit
  `RescheduleArrears*.xlsx`. No Emirates IDs / Arabic narratives in output.

## 7. Git safety

Before any commit/PR: show changed files, state whether **protected files
changed**, summarize the diff, propose a message, say whether it's safe — then
wait for explicit approval. Do not commit, push, or open/merge PRs unprompted.
Never force-push.
