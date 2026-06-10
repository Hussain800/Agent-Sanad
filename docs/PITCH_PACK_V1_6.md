# Agent Sanad v1.6 Pitch Pack

## 60-Second Product Pitch
Agent Sanad is a governed public-service workflow for housing loan arrears rescheduling. It proves identity through UAE PASS, retrieves loan data through GSB connectors, applies deterministic policy rules, explains every decision, and routes exceptions to human officers. 287 tests, 25 release gates, zero LLM decisions on money. Not a chatbot. A pilot-ready public service.

## 90-Second Judge Path
1. **Landing**: Branded service with UAE PASS entry
2. **Identity**: Mock UAE PASS verification (SOP2)
3. **Consent**: Purpose-bound data sharing
4. **Assessment**: 13 cases × deterministic policy engine
5. **Result**: Plain-language reasoning + next steps
6. **Officer**: Evidence trace, rule catalog, actions
7. **Supervisor**: Command center with SLA, fairness, incidents
8. **Auditor**: Audit export, evidence graph, package verification

## 3-Minute Technical Proof
- Deterministic `decide()`: 3 gates, 2-path, 14 rules, configurable
- No LLM touches money paths
- 94.6% path-match on held-out 2025 data
- SHA256 audit chain, Mermaid evidence graph
- ABAC ownership, consent guard v2, UAE PASS v3
- Contract-first API with Pydantic models
- Case lifecycle: 21 states, validated transitions

## 5-Minute Pilot-Readiness
- 7 mock connectors (contract-shaped, fixture-backed)
- Offline-first with SQLite persistence
- Arabic i18n (140+ keys), RTL support
- Accessibility: skip-links, focus-visible, high-contrast
- Responsible AI: model card, fairness review, reasoning evals
- Audit export, evidence graph, release provenance
- 25 automated release gates

## 7-Minute Security/Audit Story
- Consent guard v2 enforces purpose/scope/expiry/ownership
- UAE PASS session v3 prevents replay/wrong-nonce/code-reuse
- ABAC v2 denies unknown object access by default
- Signature integrity verifies package hash, detects tampering
- Audit chain is SHA256-hashed, immutable, verifiable
- Evidence graph traces every fact to its source
- No PII tracked, no real credentials stored

## Arabic Beneficiary Walkthrough
- تماماً بالعربية: الهوية عبر UAE PASS، الموافقة، التقديم، المعالجة، النتيجة
- خيارات الوصول: تخطي للمحتوى، تنقل بلوحة المفاتيح، تباين عالٍ
- حالة دورة الحياة مرئية في كل مرحلة

## Supervisor Command Walkthrough
- Backlog by status and age
- SLA risk board with breach tracking
- Fairness slices by income band
- Connector incidents with retry/circuit-breaker
- Officer workload distribution
- Override review with reason codes
