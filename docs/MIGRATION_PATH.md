# Agent Sanad v1.7 Migration Path

## v1.7 (Current)
- Mock connectors, SQLite, single-file frontend
- 330+ tests, 35+ release gates

## v2.0 Target
- Replace mock connectors with real API integrations
- Migrate SQLite to PostgreSQL
- Add proper authentication (OAuth2/OIDC)
- Add production monitoring (Prometheus/Grafana)
- Split frontend into component framework (React/Vue)

## Migration Steps
1. Swap connector adapters (mock → real)
2. Migrate database schema
3. Add auth middleware
4. Deploy staging environment
5. Run full test suite
6. Deploy production
