# Agent Sanad v1.6 LLM Safety Case

## Architecture Guarantee

Agent Sanad's LLM cannot decide financial outcomes by construction. The architecture enforces a hard boundary.

## Safety Controls

### 1. Read-Only LLM
- LLM only reads documents, extracts typed fields, and writes reasoning text
- LLM has no access to the policy engine
- LLM cannot write database state
- LLM cannot call API routes

### 2. Deterministic Money Path
- `decide()` is pure Python with no LLM dependency
- 20% cap, headroom calculation, path selection are all unit-tested
- All 13 cases have hand-traced expected outputs

### 3. Prompt Injection Resistance
- Document text with suspicious content triggers RSK-01
- RSK-01 is logged but never changes policy output
- The PROMPT_INJECTION_ONLY case produces identical output with and without injection

### 4. Template Fallback
- The cached reasoning template always produces valid output
- If LLM call fails, template fallback is used
- No degradation in decision quality occurs without LLM

### 5. Audit Traceability
- Every decision is recorded in SHA256 hash chain
- Evidence graph traces every fact feeding a recommendation
- Officer actions require reason codes for non-approve decisions

## Test Coverage
- 287 automated tests
- 13 fixture cases exercising every policy branch
- Prompt injection test proves RSK-01 doesn't alter output
- Graph equivalence tests prove LangGraph wrapper produces identical results

## Out of Scope
- LLM red-teaming against hallucination
- Adversarial prompt testing beyond RSK-01
- Multi-turn manipulation
