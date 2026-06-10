# Agent Sanad v1.5 Fairness Review

## Scope

This review assesses fairness of Agent Sanad's deterministic policy engine against 13 synthetic cases representing diverse beneficiary scenarios.

## Methodology

Each synthetic case exercises a different branch of the policy matrix:
- Income bands: 0 to 30,000 AED/month
- Family sizes: 1 to 8 members
- Obligations ratios: 0% to 80%
- Hardship states: none, unemployment, temporary circumstance
- Document states: present, missing, suspicious

## Findings

### 1. Same Rules Apply Uniformly
All cases pass through the same three governance gates (active request, nationality, documents) and the same two-path decision (UPDATE vs TRANSFER). No case receives special treatment based on demographics.

### 2. Cap Enforcement Is Universal
The 20% salary cap is hard-coded in deterministic Python. All UPDATE plans are guaranteed within cap by construction.

### 3. Hardship Cases Receive Different Paths
- Verified hardship (HARD-02): arrears transferred, no installment increase
- Unverified hardship (HARD-01): referred to human officer
This is by design — the policy treats hardship as a factual circumstance.

### 4. Family Size Sensitivity
FAM-01 rule lowers confidence for low per-member income but never blocks a case. This makes the system sensitivity-aware without being discriminatory.

### 5. Injection Safety
Prompt injection (RSK-01) is logged but never changes policy output. The PROMPT_INJECTION_ONLY case produces identical output with and without injection.

## Limitations

- 13 synthetic cases cannot represent full population diversity
- Real-world distribution of income/family/hardship combinations unknown
- No protected characteristic data collected or used
