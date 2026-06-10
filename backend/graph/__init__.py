"""LangGraph orchestration wrapper (v1.1+ Tooling Addendum, T1).

The graph is an ORCHESTRATION layer only. It does NOT decide the money.
- Nodes call existing adapters and the existing decide() — no reimplementation.
- The plain orchestrator remains the default (SANAD_ORCHESTRATOR=plain) and the
  /demo/run route is unchanged; /demo/run-graph falls back to plain on failure.
- Equivalence with the plain route is asserted for all 13 sample cases by
  tests/test_graph_equivalence.py.
"""
from backend.graph.build_graph import (
    GRAPH_AVAILABLE, build_sanad_graph, graph_import_error, run_graph_case,
)

__all__ = ["GRAPH_AVAILABLE", "build_sanad_graph", "graph_import_error",
           "run_graph_case"]
