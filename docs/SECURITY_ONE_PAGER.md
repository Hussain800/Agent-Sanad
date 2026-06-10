# Agent Sanad v1.5 Security One-Pager

## Architecture

Agent Sanad is a governed public-service operating system for arrears rescheduling. The core doctrine: **LLM reads and explains. Deterministic code decides. Human owns the exception.**

No LLM ever touches money paths, computes installments, chooses a path, or approves/rejects a case.

## Security Controls

### Consent Guard v2
- Purpose enforcement: connector calls validated against registered purpose codes
- Scope enforcement: data access restricted to consented connector scopes
- Expiry enforcement: expired consents rejected
- Revocation enforcement: revoked consents rejected
- Beneficiary ownership: cross-beneficiary access blocked
- Denied-access auditing: all denied attempts recorded in audit chain

### UAE PASS Session v3
- Stored nonce with session binding
- Expiry timestamps with TTL enforcement
- Consumed callback detection (replay rejection)
- Wrong nonce rejection
- Reused code rejection

### ABAC Ownership
- Object-level access control for cases, consents, actions, packages, appeals, notifications
- Beneficiary sees only own data
- Officer sees assigned queue
- Supervisor sees all + metrics
- Auditor sees immutable records
- Admin configures mocks but cannot silently alter decisions

### Signature Integrity v2
- Package hash binding: signatures tied to package_id and package_hash
- Tamper detection: modified packages fail verification
- Expiry enforcement: expired signatures rejected
- Revocation support

### Audit Chain (SHA256)
- Immutable hash chain for all events
- Verifiable end-to-end
- Tampered events detected

### RBAC
- 5 roles via `x-sanad-role` header: beneficiary, officer, supervisor, auditor, admin
- Route-level permission enforcement

### Security Headers
- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Rate limiting by role

### PII Discipline
- Synthetic identifiers only (APP-*, AGR-*, masked names)
- No real Emirates IDs, UAE PASS credentials, or beneficiary data
- Real workbook gitignored and verified untracked
- Automated PII pattern scanning in release checks

### Error Contract
- Uniform error envelope: `{error_code, message, path, app_version}`
- No stack traces exposed to clients

## Non-Goals
- No real UAE PASS OAuth
- No real GSB/TDRA integration
- No production secrets
- No runtime policy editing
- No LLM decisioning on eligibility, money, or compliance
