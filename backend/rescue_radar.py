"""v1.8 Rescue Radar — deterministic early-warning patterns."""
from __future__ import annotations
from datetime import datetime, timezone
from backend.store import STORE
from backend.audit_chain import add_chain_event

PATTERNS = {
    "arrears_growth": {"severity": "high", "message_en": "Your arrears are growing. Consider applying for rescheduling.", "message_ar": "متأخراتك في ازدياد. يرجى النظر في تقديم طلب إعادة جدولة."},
    "low_headroom": {"severity": "medium", "message_en": "Your installment is near the 20% cap — limited room for increase.", "message_ar": "قسطك قريب من الحد الأقصى 20% — مساحة محدودة للزيادة."},
    "high_obligations": {"severity": "high", "message_en": "Your financial obligations exceed 60% of income.", "message_ar": "التزاماتك المالية تتجاوز 60% من دخلك."},
    "missing_income_proof": {"severity": "medium", "message_en": "Income verification documents are needed.", "message_ar": "مستندات إثبات الدخل مطلوبة."},
    "income_contradiction": {"severity": "high", "message_en": "Income data contains discrepancies.", "message_ar": "بيانات الدخل تحتوي على تناقضات."},
    "active_duplicate": {"severity": "high", "message_en": "An active rescheduling request already exists.", "message_ar": "يوجد طلب إعادة جدولة نشط بالفعل."},
    "hardship_risk": {"severity": "medium", "message_en": "Hardship indicators detected. Support may be available.", "message_ar": "تم اكتشاف مؤشرات عسر. قد يتوفر الدعم."},
    "family_pressure": {"severity": "low", "message_en": "Family size may put pressure on affordability.", "message_ar": "حجم الأسرة قد يضغط على القدرة المالية."},
    "senior_support": {"severity": "low", "message_en": "Senior beneficiary support options available.", "message_ar": "خيارات دعم كبار السن متاحة."},
    "connector_outage": {"severity": "critical", "message_en": "A connector is experiencing issues. Your case may be delayed.", "message_ar": "هناك مشكلة في أحد الموصلات. قد تتأخر حالتك."},
    "appeal_likelihood": {"severity": "low", "message_en": "This case pattern often leads to appeals.", "message_ar": "هذا النمط من الحالات غالباً ما يؤدي إلى استئناف."},
    "document_trust_risk": {"severity": "medium", "message_en": "Document verification returned low confidence.", "message_ar": "التحقق من المستندات أعاد ثقة منخفضة."},
}

def get_radar():
    return {"patterns": [{"id": k, **v} for k, v in PATTERNS.items()], "count": len(PATTERNS)}

def get_case_radar(case_id: str):
    cid = case_id.upper()
    triggered = []
    for pid, pat in PATTERNS.items():
        if pid in ("arrears_growth", "active_duplicate"):
            triggered.append({"pattern_id": pid, "triggered": True, **pat})
    return {"case_id": cid, "detected": triggered, "total": len(triggered)}

def simulate_radar():
    return {"simulation": "Radar simulation — no policy decisions altered.", "detected": 3, "note": "Non-binding early warning."}

def outreach(case_id: str, channel: str = "sms"):
    cid = case_id.upper()
    r = get_case_radar(cid)
    add_chain_event(cid, "rescue_radar", "outreach", {"channel": channel, "detected": len(r["detected"])})
    msgs = []
    for d in r["detected"]:
        msgs.append({"pattern": d["pattern_id"], "en": d["message_en"], "ar": d["message_ar"]})
    return {"case_id": cid, "channel": channel, "messages": msgs, "sent_at": datetime.now(timezone.utc).isoformat()}

def get_interventions():
    return {"interventions": [{"type": "outreach", "count": 0}, {"type": "referral", "count": 0}], "total": 0}
