# Agent Sanad v1.6 Release Provenance

## Release Metadata
- **Version**: 1.6.0
- **Date**: June 2026
- **Commit**: 7103923 (merge), 8e8a194 (build)
- **Branch**: main (via PR #8 from v1.6-release)

## Build Artifacts
| Artifact | Path | Status |
|----------|------|--------|
| OpenAPI JSON | docs/api/openapi.json | Generated |
| Postman Collection | docs/POSTMAN_COLLECTION.json | 107 items |
| API Guide | docs/API_GUIDE.md | Current |
| Release Notes | docs/RELEASE_NOTES_V1_5.md | Present |

## Test Evidence
- **287 passing tests** across 30+ test files
- **25/25 release gates** passing
- **1 third-party warning** (pytz deprecation, not our code)
- Policy engine unchanged from v1.4

## Changed Files
28 files: 12 modified, 16 new. +2,730 / −33 lines.

## Security Review
- No PII in tracked files
- No real workbook committed
- APP_VERSION == CLIENT_BUILD == 1.6.0
- Decision packages use current app version

## Known Limitations
- All connectors are mock
- Frontend v1.6 is structural (full UI rebuild TBD)
- pytz third-party deprecation warning
