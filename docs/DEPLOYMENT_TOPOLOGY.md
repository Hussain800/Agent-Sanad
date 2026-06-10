# Agent Sanad v1.7 Deployment Topology

## Demo / Mock Profile
- Single FastAPI process (uvicorn, port 8000)
- SQLite database (stdlib, zero deps)
- Single-file frontend (vanilla HTML/CSS/JS)
- No external network calls required
- All 7 connectors are mock

## Production Profile (Documented, Not Implemented)
- FastAPI behind reverse proxy (nginx/Caddy)
- PostgreSQL or Supabase
- Real UAE PASS OAuth integration
- Real GSB/TDRA connectors
- Real document verification
- Redis for rate limiting
- Prometheus for metrics
- Kubernetes or VM deployment
