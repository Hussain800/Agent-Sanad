# Agent Sanad v1.7 Monitoring Plan

## Health Check: GET /ops/health
- App version, mock mode, connector count, case count, test/gate counts

## SLO Report: GET /ops/slo
- Decision latency (avg), connector error rate, SLA breaches, error count

## Traces: GET /ops/traces/{case_id}
- Per-case audit trail trace

## Incidents: GET /ops/incidents
- Open/closed incident list. Resolve via POST /ops/incidents/{id}/resolve

## Release Check: GET /ops/release-check/latest
- Current version, test count, gate count, status

## Security Drills: POST /security-drills/run
- 12 attack simulations. GET /security-drills/latest for results.
