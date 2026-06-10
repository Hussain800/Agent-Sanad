# Agent Sanad v1.6 Reasoning Quality Evaluations

## Evaluation Approach

The LLM is read-only: it reads documents, extracts fields, writes reasoning, and translates. It never makes decisions. But explanation quality still matters because officers, beneficiaries, and auditors read it.

## Golden Reasoning Snapshots

For each of the 13 demo cases, a canonical reasoning text exists as a test assertion:

| Case | Expected Reasoning (Key Phrase) |
|------|-------------------------------|
| GOLDEN | "income provides sufficient headroom" |
| NOHEAD | "no headroom under the 20% cap" |
| ACTIVE | "active rescheduling request exists" |
| MISSING | "salary certificate is missing" |
| CONTRA | "income contradiction detected" |

## Quality Gates

### 1. No Unsupported Facts
Reasoning must not invent numbers or facts not present in validated case data.

### 2. Arabic Explanation Snapshots
Arabic reasoning must contain no English-only terms, no transliteration without Arabic gloss.

### 3. Prompt-Injection Safety
Documents with suspicious text (RSK-01) must produce reasoning identical to the same case without injection.

### 4. Evidence-Reference Checks
Every claim in reasoning should be traceable to an adapter return, document field, or policy rule.

## Test Coverage
- `test_reasoning_evals.py`: Reasoning present in all 13 cases, Arabic keys coverage, recommendation validity
- `test_release_provenance.py`: Health version check, connector count, OpenAPI/Postman existence

## Limitations
- No LLM is called in tests (mocked offline)
- Arabic explanation quality is structural, not semantic
- Full hallucination detection requires LLM-in-the-loop (out of scope)
