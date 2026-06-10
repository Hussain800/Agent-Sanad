# Agent Sanad v1.5 UAE Integration Map

## Current State

All connectors are **mock** (contract-shaped, fixture-backed, test-enforced). Each connector maps to a real UAE government service integration point.

## Integration Points

### 1. UAE PASS (uaepass)
**Real service**: UAE PASS digital identity platform  
**Purpose**: Citizen identity verification, digital signing, e-Seal  
**Mock scope**: Simulated SOP2 authentication, stateful session v3 with replay protection  
**Production path**: OAuth 2.0 / OpenID Connect integration with UAE PASS sandbox

### 2. Government Service Bus (gsb)  
**Real service**: TDRA Government Service Bus  
**Purpose**: Cross-entity data exchange (SZHP loan data, arrears, financial data)  
**Mock scope**: Provider/service routing with consent enforcement  
**Production path**: TDRA GSB API integration with proper authentication

### 3. SZHP Core Systems (szhp-core)
**Real service**: Sheikh Zayed Housing Programme internal systems  
**Purpose**: Applicant profiles, loan accounts, arrears ledger, payment history  
**Mock scope**: Fixture-backed data retrieval  
**Production path**: SZHP internal API integration

### 4. UAE Verify (uae-verify)
**Real service**: TDRA UAE Verify document verification platform  
**Purpose**: Document authenticity verification (salary certificates)  
**Mock scope**: Hash-based document verification with trust status  
**Production path**: UAE Verify API with document submission

### 5. Financial Capacity (financial-capacity)
**Real service**: Emirates Credit Bureau / Central Bank  
**Purpose**: Salary verification, obligations summary, credit risk assessment  
**Mock scope**: Income verification with risk band calculation  
**Production path**: ECB API integration

### 6. Notifications (notifications)
**Real service**: National Instant Alert / SMS gateway  
**Purpose**: Multi-channel citizen notifications (SMS, email, push)  
**Mock scope**: Template-based notification dispatch  
**Production path**: NIA API integration

### 7. Case Management (case-management) [v1.5]
**Real service**: SZHP service centre operations  
**Purpose**: Officer assignment, callback scheduling, case notes, SLA tracking, escalation  
**Mock scope**: Full lifecycle operations  
**Production path**: SZHP case management system integration

## Architecture Note

The deterministic policy engine, rule catalog, schemas, and audit model are **independent** of connector implementations. Swapping mock adapters for real integrations requires no changes to core logic.
