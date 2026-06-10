# Agent Sanad v1.7 Data Processing Record

## Data Categories
- Identity (synthetic): name_masked, nationality, family_size
- Financial (synthetic): income, installment, arrears, balance  
- Documents (synthetic): salary_certificate_present, document_hash
- Consent: purpose_code, connector_scopes, granted_at, expires_at, revoked_at

## Processing Purpose
Housing loan arrears rescheduling assessment under Sheikh Zayed Housing Programme

## Legal Basis
Consent (purpose-bound, scoped, expiring, revocable)

## Retention
SQLite demo database. Delete to reset. No real PII persisted.

## Data Transfers
None. All connectors are mock. Offline-first mode.
