# Agent Sanad v1.8 Release Provenance

## Release Metadata

- **Version**: 1.8.0
- **Date**: June 10, 2026
- **Commit**: 8eaf4a0
- **Branch**: main
- **Release name**: National Housing Resilience OS

## Build Artifacts

| Artifact | Path | Status |
|---|---|---|
| OpenAPI JSON | docs/api/openapi.json | Generated for v1.8.0 |
| Postman Collection | docs/POSTMAN_COLLECTION.json | Generated |
| Current Release | docs/CURRENT_RELEASE.md | Current |
| Release Facts | docs/RELEASE_FACTS.json | Current |
| Release Notes | docs/RELEASE_NOTES_V1_8.md | Present |
| v1.8 PRD | docs/V1_8_WINNING_PRD.md | Present |

## Test Evidence

- **431 passing tests** across 45+ test files
- **45/45 release gates** targeted by `scripts/release-check.ps1`
- **1 approved third-party warning**: `pytz` deprecation warning from Python 3.13 dependency code
- Policy engine unchanged for v1.8 release verification

## v1.8 Product Surfaces

- Release Brain
- Rescue Radar
- Policy Digital Twin
- Evidence Vault and Trust Receipt
- Interop Certification Lab
- Arabic Service Copilot
- Mission Control
- Red Team Chaos Lab

## Security Review

- No PII in tracked files
- No real workbook committed
- APP_VERSION == CLIENT_BUILD == 1.8.0
- Real UAE PASS, GSB, UAE Verify, bank, and notification integrations remain mocked
- LLM remains read-only and cannot decide policy outcomes

## Known Limitations

- Connectors are mock implementations
- v1.8 advanced product surfaces are deterministic pilot simulations, not production integrations
- The Python 3.13 `pytz` deprecation warning is approved as third-party noise
