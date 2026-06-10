# Agent Sanad v1.5 Responsible AI Assessment

## AI Usage Boundary

Agent Sanad uses LLMs only for read and explain tasks. LLMs never compute installments, choose paths, approve/reject cases, write state, or touch money.

## Decision Architecture

| Layer | May | Must Never |
|-------|-----|------------|
| LLM | Read text, extract fields, write reasoning, translate | Compute, choose path, approve/reject, write state |
| Deterministic Engine | Validate, compute headroom, choose path, fire rules | Invent facts, call LLM for numbers |
| Human Officer | Approve, adjust, escalate with reason | Bypass audit log |

## Fairness

- Same policy rules apply uniformly to all cases
- No demographic profiling or protected-characteristic decisions
- 13 synthetic cases distributed across income bands and family sizes
- Historical benchmark: 94.6% path-match on held-out 2025 data

## Confidence Bands

| Confidence | Behavior |
|------------|----------|
| High | Auto-approvable |
| Medium | Officer review recommended |
| Low | Human review required |

Only high-confidence cases are auto-approvable. All others route to human review.

## Human Oversight

Complete evidence trace, append-only audit, officer actions with reason codes, supervisor command center with backlog/SLA/fairness/override monitoring.

## Limitations

- Synthetic data only; no real beneficiary data
- All connectors are mock
- Historical benchmark was on real data; fairness slices use synthetic data
- Officer discretion may not be fully captured
