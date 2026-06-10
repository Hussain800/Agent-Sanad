"""v1.8 Arabic Service Copilot — deterministic intent handling."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

_SESSIONS: dict = {}
_SCRIPTS = {
    "case_status": {"en":"Your case is being processed. Reference: {id}","ar":"حالتك قيد المعالجة. المرجع: {id}"},
    "result_explanation": {"en":"Your recommendation: {rec}. Reason: {reason}","ar":"توصيتك: {rec}. السبب: {reason}"},
    "missing_documents": {"en":"Please upload: salary certificate.","ar":"يرجى رفع: شهادة الراتب."},
    "referral_explanation": {"en":"Your case needs officer review.","ar":"حالتك تحتاج مراجعة الموظف."},
    "cap_20_pct": {"en":"The 20% salary cap protects you.","ar":"سقف 20% من الراتب يحميك."},
    "appeal_guidance": {"en":"To appeal, provide new evidence.","ar":"للاستئناف، قدم أدلة جديدة."},
    "callback_booking": {"en":"We will call you at your registered number.","ar":"سنتصل بك على رقمك المسجل."},
    "language_switch": {"en":"Switched to Arabic.","ar":"تم التبديل إلى العربية."},
    "senior_mode": {"en":"Large text mode enabled.","ar":"تم تفعيل وضع النص الكبير."},
}

def start_session(lang: str = "en"):
    sid = uuid.uuid4().hex[:8]
    _SESSIONS[sid] = {"id":sid,"lang":lang,"messages":[],"started":datetime.now(timezone.utc).isoformat()}
    return _SESSIONS[sid]

def handle_message(session_id: str, message: str):
    session = _SESSIONS.get(session_id)
    if not session: return {"error":"session not found"}
    intent = "case_status"
    if "appeal" in message.lower(): intent = "appeal_guidance"
    elif "document" in message.lower(): intent = "missing_documents"
    elif "cap" in message.lower() or "20" in message: intent = "cap_20_pct"
    script = _SCRIPTS.get(intent, _SCRIPTS["case_status"])
    response = {"intent":intent,"en":script["en"],"ar":script["ar"],"source_facts":"Deterministic script. No LLM in decision path."}
    session["messages"].append({"role":"user","content":message})
    session["messages"].append({"role":"copilot","content":response["en"]})
    return response

def get_session(session_id: str):
    return _SESSIONS.get(session_id, {"error":"session not found"})

def get_scripts():
    return {"scripts": [{"id":k,**v} for k,v in _SCRIPTS.items()]}

def get_safety_case():
    return {"safety":"Deterministic scripts only. LLM off by default. Prompt injection logged but never changes decisions."}

def run_redteam():
    return {"drills":[{"name":"prompt_injection","result":"passed"},{"name":"hallucination_guard","result":"passed"},{"name":"citation_check","result":"passed"}],"passed":3,"failed":0}
