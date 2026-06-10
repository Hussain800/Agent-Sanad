# Agent Sanad v1.7 Service Centre Scripts

## Beneficiary Calls
- "Your application has been received. Reference: {case_id}"
- "Additional documents required. Please upload: {doc_type}"
- "Your case is under officer review. Expected: {timeframe}"
- "Your appeal has been recorded. Reference: {appeal_id}"

## Officer Workflows
- Check assigned queue: GET /cases
- Review case evidence: GET /cases/{id}/evidence-graph/v2
- Take action: POST /cases/{id}/officer-action
- Schedule callback: POST /connectors/case-management/mock/schedule-callback

## Escalation
- Create escalation: POST /connectors/case-management/mock/create-escalation
- Supervisor approval: POST /appeals/{id}/supervisor-approve
