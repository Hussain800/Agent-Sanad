# Agent Sanad v1.5 Event Catalog

## Audit Events

Every state transition and action produces an audit event. Events are recorded in the SHA256 hash chain.

### Policy Engine Events
| Event | Actor | Description |
|-------|-------|-------------|
| `policy.decide` | policy | Deterministic decide() completed |
| `policy.transition` | policy | State machine transition |

### Consent Events
| Event | Actor | Description |
|-------|-------|-------------|
| `consent.created` | beneficiary | New consent record |
| `consent.revoked` | beneficiary | Consent revoked |
| `consent.denied` | consent_guard | Access denied (v1.5) |
| `consent.validated` | consent_guard | Consent validation (v1.5) |

### Action Events
| Event | Actor | Description |
|-------|-------|-------------|
| `action.uploaded` | beneficiary | Evidence uploaded |
| `action.rejected` | officer | Action rejected |
| `action.resubmitted` | beneficiary | Action resubmitted |
| `action.waived` | supervisor | Action waived |
| `action.completed` | system | Action marked complete |

### Appeal Events
| Event | Actor | Description |
|-------|-------|-------------|
| `appeal.created` | beneficiary | Appeal created |
| `appeal.evidence_submitted` | beneficiary | Evidence submitted |
| `appeal.review_started` | officer | Officer review started |
| `appeal.decided_upheld` | officer | Decision: upheld |
| `appeal.decided_reversed` | officer | Decision: reversed |
| `appeal.supervisor_approved` | supervisor | Supervisor approval |

### Officer Events
| Event | Actor | Description |
|-------|-------|-------------|
| `officer.action` | officer | Officer approve/adjust/escalate |

### Connector Events
| Event | Actor | Description |
|-------|-------|-------------|
| `connector.call` | connector | Connector invocation logged |
| `connector.simulated` | admin | Failure mode simulated |
| `connector.reset` | admin | Connector reset |

### Signature Events
| Event | Actor | Description |
|-------|-------|-------------|
| `signature.requested` | system | Signature requested |
| `signature.verified` | system | Signature verified |
| `package.created` | system | Decision package created |
| `package.revoked` | system | Package revoked |
| `package.sealed` | system | E-seal applied |

### State Machine Transitions

Submitted → IdentityLinked → DataRetrieved → Extracting → Validating → PolicyRun → RecommendationReady/NeedsDocuments/Refer/Rejected → Closed
