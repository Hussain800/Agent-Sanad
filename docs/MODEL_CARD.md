# Agent Sanad v1.5 Model Card

## System Identity

**Name**: Agent Sanad  
**Version**: 1.5.0  
**Type**: Deterministic policy engine with optional LLM explanation layer  
**Domain**: Housing loan arrears rescheduling  
**Jurisdiction**: UAE Ministry of Energy and Infrastructure  

## Intended Use

Automated assessment and recommendation drafting for housing loan arrears rescheduling applications under the Sheikh Zayed Housing Programme.

## Out-of-Scope Uses

- Final decisions without human review (officer owns exceptions)
- Credit scoring or credit decisions
- Loan origination or approval
- Any use without UAE PASS identity verification
- Any use with real beneficiary data without proper consent

## Architecture

| Component | Role | AI/Deterministic |
|-----------|------|-----------------|
| Policy Engine | decide() - 3 gates, 2-path decision | Deterministic Python |
| Rule Catalog | 14 rule IDs with fixed effects | Deterministic |
| Config | Externalized thresholds (20% cap) | Deterministic |
| LLM (optional) | Read documents, write reasoning, translate | LLM (read-only) |
| Officer | Final authority on exceptions | Human |

## Performance

- Path-match accuracy: 94.6% on held-out 2025 data (n=522)
- UPDATE plans within 20% cap: 100% by construction
- Draft latency: under 1 second
- Deterministic rerun: 100% consistent

## Training Data

No ML model training. The policy engine was reverse-engineered from approximately 2,000 real historical decisions (2023-2025).

## Evaluation

- 231 automated tests (v1.5)
- 13 synthetic case fixtures covering all policy branches
- 17 automated release gates
- Historical benchmark replay against held-out data

## Ethical Considerations

- No LLM decides any financial outcome
- Human officer owns all exceptions
- All decisions are audited and traceable
- Consent is purpose-bound, scoped, expiring, and revocable
- No demographic profiling

## Limitations

- Synthetic test cases only
- All connectors are mock
- No real-time data integration
- Officer discretion patterns may not be fully captured
