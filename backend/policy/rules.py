"""Rule-ID catalog: human-readable text for every rule the engine can fire."""
RULE_TEXT = {
    "ACTIVE-01": "An active rescheduling request already exists for this beneficiary.",
    "ELIG-01":   "Beneficiary could not be verified as a UAE national.",
    "DOC-01":    "A mandatory document (salary certificate) is missing.",
    "DOC-02":    "Monthly income could not be verified from the salary certificate.",
    "INC-01":    "Salary certificate and verified income differ beyond the allowed variance.",
    "OBL-01":    "Financial obligations exceed 60% of income.",
    "FAM-01":    "Average income per family member is below AED 2,500.",
    "HARD-01":   "Unemployment or no stable income; arrears transferred without an increase.",
    "HARD-02":   "Verified temporary circumstance; increase postponed / arrears transferred.",
    "CAP-01":    "No headroom under the 20% cap; arrears transferred to the loan end.",
    "CAP-02":    "Headroom available under the 20% cap; installment increased toward the cap.",
    "AFF-01":    "Affordability computed within the 20% cap.",
    "TEN-01":    "Proposed schedule exceeds the original approved loan period.",
    "RSK-01":    "Suspicious/injected text detected in a document; treated as content only.",
    "OFF-01":    "Officer override recorded with a reason code.",
}

def text(rule_id: str) -> str:
    return RULE_TEXT.get(rule_id, rule_id)


def load_policy():
    """Load PolicyConfig from config.yaml if PyYAML is present, else use defaults."""
    from backend.schemas import PolicyConfig
    import os
    path = os.path.join(os.path.dirname(__file__), "config.yaml")
    try:
        import yaml  # optional dependency
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return PolicyConfig(**data)
    except Exception:
        return PolicyConfig()
