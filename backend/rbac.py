"""RBAC/ABAC mock middleware using x-sanad-role and x-sanad-user headers."""
from __future__ import annotations
from fastapi import Request, HTTPException

ROLES = {"beneficiary", "officer", "supervisor", "auditor", "admin"}

_ROUTE_PERMISSIONS: dict[str, set[str]] = {
    # beneficiary routes
    "GET /cases/": {"beneficiary", "officer", "supervisor", "auditor", "admin"},
    "GET /cases": {"beneficiary", "officer", "supervisor", "auditor", "admin"},
    "POST /cases/": {"beneficiary", "officer", "admin"},
    "GET /applications": {"beneficiary", "officer", "supervisor", "admin"},
    "GET /applications/": {"beneficiary", "officer", "supervisor", "admin"},
    "POST /applications/mock": {"beneficiary", "admin"},
    "POST /applications/mock/": {"beneficiary", "admin"},
    # officer routes
    "POST /demo/": {"officer", "supervisor", "admin"},
    "POST /cases//decide": {"officer", "supervisor", "admin"},
    "POST /cases//officer-action": {"officer", "supervisor", "admin"},
    "POST /cases//actions/": {"beneficiary", "officer", "admin"},
    "GET /cases//actions": {"beneficiary", "officer", "supervisor", "admin"},
    # supervisor routes
    "GET /supervisor/": {"supervisor", "auditor", "admin"},
    # auditor routes
    "GET /audit/": {"auditor", "admin"},
    # admin routes
    "POST /connectors/": {"admin"},
    # consent - beneficiary owns
    "POST /consents": {"beneficiary", "admin"},
    "GET /consents/": {"beneficiary", "officer", "supervisor", "auditor", "admin"},
    # connectors - anyone can read health
    "GET /connectors": {"beneficiary", "officer", "supervisor", "auditor", "admin"},
    "GET /connectors/": {"beneficiary", "officer", "supervisor", "auditor", "admin"},
}


def _route_key(method: str, path: str) -> str:
    """Normalize path for permission lookup: replace dynamic IDs with a placeholder."""
    known = {"cases", "actions", "connectors", "consents", "applications",
             "supervisor", "audit", "demo", "healthz", "architecture",
             "benchmark", "officer-actions", "privacy", "sessions",
             "notifications", "appeals", "decision-package", "signature",
             "decision_packages", "signatures", "plan-options", "simulate-plan",
             "simulate", "reset", "health"}
    parts = path.rstrip("/").split("/")
    normalized_parts = []
    for p in parts:
        if p in known:
            normalized_parts.append(p)
        elif p.isupper() or p.startswith(("CUSTOM-", "AGR-", "APP-", "UAEPASS-", "CONSENT-", "PKG-", "SIG-")):
            normalized_parts.append(":id")
        else:
            normalized_parts.append(p)
    normalized = "/".join(normalized_parts)
    # Collapse consecutive placeholders
    while "/:id/:id" in normalized:
        normalized = normalized.replace("/:id/:id", "/:id")
    return f"{method} {normalized}"


def check_access(method: str, path: str, role: str) -> None:
    """Raise HTTPException 403 if role lacks permission."""
    if role not in ROLES:
        raise HTTPException(403, "Unknown role")
    if role == "admin":
        return  # admin can do everything
    key = _route_key(method, path)
    # Check exact match first, then prefix match
    allowed = _ROUTE_PERMISSIONS.get(key)
    if allowed is None:
        # Try prefix match
        for rk, rv in _ROUTE_PERMISSIONS.items():
            if key.startswith(rk.rstrip("/")):
                allowed = rv
                break
    if allowed is None:
        # Default: allow authenticated roles
        allowed = {"beneficiary", "officer", "supervisor", "auditor", "admin"}
    if role not in allowed:
        raise HTTPException(403, f"Role '{role}' not allowed for {method} {path}")


def get_role(request: Request) -> str:
    return request.headers.get("x-sanad-role", "beneficiary")


def get_user(request: Request) -> str:
    return request.headers.get("x-sanad-user", "anonymous")
