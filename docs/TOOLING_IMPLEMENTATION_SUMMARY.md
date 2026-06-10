# Agent Sanad — Tooling Addendum Implementation Summary

How the v1.1+ Tooling Addendum was executed, what was deliberately skipped, and
how to verify the framework never decides the money.

> **The doctrine is unchanged:** frameworks orchestrate / trace / observe.
> The deterministic policy engine decides. The human officer owns exceptions.

---

## T1 — LangGraph orchestration wrapper · IMPLEMENTED

| Piece | Where |
|---|---|
| Typed graph state | `backend/graph/state.py` |
| 10 nodes (addendum §4.4) | `backend/graph/nodes.py` |
| Compiled StateGraph + sync runner | `backend/graph/build_graph.py` |
| Equivalence diff helpers | `backend/graph/compare_outputs.py` |
| Graph route | `POST /demo/run-graph/{case_id}` |
| Equivalence proof endpoint | `GET /demo/compare/{case_id}` |
| Orchestrator flag | `SANAD_ORCHESTRATOR=plain\|graph` (default **plain**) |
| Officer UI | "Run via LangGraph orchestrator" toggle + orchestrator chip (shows fallback) |

**Safety properties, all test-enforced:**
- `run_policy_engine` calls the existing `decide()` — policy is never reimplemented.
- Pre-policy nodes are inspect-only labels; the Rule-1/2/3 gates still fire
  inside `decide()`, which is what guarantees equivalence.
- **All 13 sample cases produce byte-equivalent reports** on plain vs graph
  (recommendation, path, fired rules, 20% and period compliance, plan numbers)
  — `tests/test_graph_equivalence.py`.
- The §7 state timeline (Submitted → … → Closed) is identical on both routes.
- If LangGraph import or execution fails, the route returns the **plain**
  envelope with `impact.fallback_used=true` — proven by a forced-failure test.
  The beneficiary flow never touches the graph route at all.

## T2 — LangSmith-ready tracing with PII redaction · IMPLEMENTED (off by default)

| Piece | Where |
|---|---|
| Allow-list + pattern redaction | `backend/observability/redaction.py` |
| Trace adapter (stub exporter) | `backend/observability/langsmith_trace.py` |
| Flags | `LANGSMITH_TRACING=false` (default) · `TRACE_REDACTION=true` · `LANGSMITH_PROJECT=agent-sanad-demo` |

**Safety properties, all test-enforced (`tests/test_observability.py`):**
- Tracing is **disabled by default**; the app is fully functional without it.
- Redaction is **unconditional** — every payload passes `redact_for_trace()`;
  setting `TRACE_REDACTION=false` while tracing is on makes the adapter
  **refuse to emit** rather than send unredacted data.
- Redaction drops: name-like keys, Emirates-ID patterns (`784-…` / 15-digit),
  Arabic narratives, document text, identifier-bearing filenames, and **any
  key not on the allow-list** (workbook rows can never slip through).
- A trace payload may contain only: synthetic case/application ids, node
  names, recommendation, path, fired rules, latency, mock flag, orchestrator.
- No hard `langsmith` dependency: with the package absent, enabled tracing
  degrades to redacted structured log lines — external auth never gates the demo.

## T3 — LlamaIndex / LlamaParse · INTENTIONALLY NOT IMPLEMENTED

The addendum conditions T3 on "stable and useful". Verdict: **neither**, here.
- The only approved parse target is one synthetic salary certificate —
  `backend/extraction.py` already parses it live with a Pydantic gate and a
  cached fallback. LlamaParse would add a heavy dependency tree and an
  external-service dependency to replicate an existing, tested, offline path.
- Policy-clause retrieval over a 15-rule catalog needs no vector index; the
  rule text is already surfaced verbatim in the drawer's rule trace.
Pilot note: if MOEI supplies a real policy-manual corpus, LlamaIndex becomes
the right tool — behind the same "explanatory, never authoritative" guardrail.

## T4 — LangChain wrappers · INTENTIONALLY NOT IMPLEMENTED

`reasoning.py` already isolates the optional LLM call behind a cached
fallback in ~10 lines. A LangChain wrapper would add an abstraction layer and
dependency surface without removing any boilerplate. Revisit in pilot if
multi-provider routing is needed.

## Explicitly excluded (addendum §9)

CrewAI · AutoGen · Semantic Kernel · DSPy · OpenAI Agents SDK — not needed for
a single governed casework pipeline. **MCP remains a production roadmap item
only** (addendum §8): in pilot, the five adapter boundaries could be exposed as
MCP servers after security review; nothing in the hackathon build depends on it.

## How to verify the framework never decides

```powershell
# 1) Equivalence across every sample case (13 parametrized tests):
python -B -m pytest tests/test_graph_equivalence.py -q
# 2) Live proof endpoint:
Invoke-RestMethod http://127.0.0.1:8000/demo/compare/GOLDEN   # equivalent: true
# 3) Tracing is off and redaction is enforced:
python -B -m pytest tests/test_observability.py -q
```
