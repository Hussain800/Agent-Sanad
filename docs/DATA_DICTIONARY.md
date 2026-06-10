# Agent Sanad v1.5 Data Dictionary

## SQLite Tables

### applications
Custom beneficiary applications. `id` is a synthetic UUID.

### recommendations  
Policy engine decision results linked to applications.

### audit_events
Per-application audit trail entries.

### officer_actions
Human officer decisions (approve/adjust/escalate) with reason codes.

### sessions
UAE PASS authentication sessions. Stores nonce, expiry, state (started/consumed/expired/revoked).

### consents
Purpose-bound data sharing consent records. Tracks beneficiary_ref, purpose_code, connector_scopes, granted_at, expires_at, revoked_at.

### connector_calls
All connector invocations with status, latency, consent validation, and failure modes.

### connector_state
Current connector health state and failure mode.

### case_actions
Repair actions per case with status (open/uploaded/submitted/accepted/rejected/resubmitted/waived/expired/closed), owner, due date.

### document_checks
Document verification results with tamper_result, signature_valid, confidence, trust_status.

### decision_packages
Digital closeout packages with package_hash, decision_summary, Arabic/English letters, signed_at.

### signatures
Mock digital signatures with signatory_ref, signature_value, status (pending/verified/revoked).

### audit_chain
SHA256 hash chain for immutable audit verification. Each entry chains to previous via previous_hash.

### appeals
Beneficiary appeals with reason, new_evidence, status (draft/submitted/officer_review/supervisor_review/upheld/reversed/closed), decision, decision_by.

### notifications
Notification dispatch records with channel (sms/email/push), template, status.

### case_assignments (v1.5)
Officer case assignments with officer_ref, priority, sla_hours, due_date, status.

### case_sla (v1.5)  
SLA tracking per case stage with deadline and breach flag.

### action_events (v1.5)
Repair action event timeline recording uploads, rejections, resubmissions, waives.

### appeal_events (v1.5)
Appeal event timeline recording evidence submission, reviews, decisions, supervisor approvals.

### notification_events (v1.5)
Notification lifecycle events.

### fairness_slices (v1.5)
Fairness analysis slices with metric name, value, sample size.

### material_exports (v1.5)
Generated material tracking (OpenAPI, Postman, guides) with checksums.
