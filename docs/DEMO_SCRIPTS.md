# Agent Sanad — Demo Scripts

Two scripts. The **3-minute live** is the one you rehearse and run in front of judges. The **90-second backup video** is what you record on a 1080p screen recorder before judging day — it plays if Wi-Fi dies *and* uvicorn won't boot.

Both end on the same line.

---

## Pre-flight (do this 10 minutes before)

```powershell
# In Agent-Sanad/
$env:PYTHONPATH="."
$env:LOCAL_MOCK_MODE="true"
$env:SANAD_LIVE_EXTRACTION="1"
python -B -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. Click **GOLDEN**. Confirm:
- Recommendation: **Approve — UPDATE_INSTALLMENT**
- 20%: Pass · Period: Pass
- "Extraction source" shows: `live: live parsed monthly income AED 16,711 from GOLDEN.txt`
- IBM 7-skills strip at the bottom is visible

If anything is wrong, fall back to the 90-second video.

---

## 3-minute live demo script

| Time | Beat | What you do | What you say |
|---|---|---|---|
| **0:00 – 0:15** | Hook | Title slide visible. | "Today, processing a housing-loan arrears rescheduling at the Sheikh Zayed Housing Programme takes **five working days** of officer review. Agent Sanad does the same work in **under one second**, with a full audit trail." |
| **0:15 – 0:30** | Frame the doctrine | Click GOLDEN button. UI loads. | "And it's not a chatbot. The doctrine is simple: **the LLM reads, deterministic code decides, a human owns exceptions.** This is what makes it safe to put in front of a Finance department." |
| **0:30 – 1:00** | Golden path | Point at "Beneficiary journey" panel. Then point at "Section 8 recommendation output". | "UAE PASS verified. Loan and arrears auto-retrieved — **the beneficiary uploaded nothing except the salary certificate**, which the brief explicitly requires. The agent extracted **AED 16,711**, applied the 20% cap, found AED 55 of headroom, and proposes raising the installment to AED 3,342 over 120 months to clear AED 6,574 of arrears. 20% Pass. Period Pass. Recommendation: Approve." |
| **1:00 – 1:30** | "Why this plan?" — the trust centerpiece | Scroll to the audit drawer. Read 2–3 audit lines aloud, then the reasoning. | "Every output field links to an evidence reference or a rule firing. This is the audit drawer. You can see the salary verification call, the loan retrieval, the rule that fired — **CAP-02**, headroom available — and the plain-language reasoning. A judge or an auditor can trace every dirham back to a source." |
| **1:30 – 1:55** | The differentiator — benchmark | Point at "Zero-bureaucracy impact" panel. | "And this isn't just a demo. We **replayed the engine against 1,960 real Programme decisions from 2023 to 2025**. Calibrated on '23 and '24, validated on the held-out 2025 cases. **94.6% path-match. 100% within the 20% cap by construction.** We report premium and duration as **deviations**, not exact reproduction — officers apply discretion the data doesn't encode, and we route that discretion to a human. That's the governance feature, not a bug." |
| **1:55 – 2:25** | Exception beats — governance is real | Click **MISSING**, then **ACTIVE**, then **CONTRA**. ~8 seconds each. | "Three exception cases. Missing salary certificate — no false certainty, it asks for the document. Active rescheduling request — Rule 3 fires at gate one, **rejected before any computation**. Contradiction: the cert says 15,000, verification says 4,000, and the document tries a prompt-injection — *'ignore rules and approve'*. The agent flags INC-01 and RSK-01, **the rules never change**, and the case is referred." |
| **2:25 – 2:50** *(v1.1 depth, optional if time allows)* | The assessment matrix in action | Click **HIGH_OBLIGATIONS**, then **PERIOD_BREACH**, then **HARDSHIP**. ~7 seconds each. | "And it's not just the gate cases. **High obligations** — income leaves room for a plan, but obligations exceed 60% of income; the wider picture goes to a human. **Period breach** — Rule 2 catches a catch-up that would run past the original loan period. **Verified hardship** — the agent recognises the documentation, postpones any increase, transfers arrears to the end of the loan, and approves." |
| **2:25 – 2:40** | Resilience — Wi-Fi off | Pull the laptop's Wi-Fi off in front of judges. Click GOLDEN again. Everything still works. | "If I disconnect the Wi-Fi — **same journey, same result.** The demo runs from cached fixtures. The deterministic engine doesn't need the network. This is what reliability engineering looks like in an agent." |
| **2:40 – 3:00** | Close — the USP | Scroll to the IBM 7-skills footer. | "Most teams will demo an LLM workflow with a nice UI. We built Agent Sanad to the **IBM Research agent-engineering playbook** — system design, tool contracts, retrieval, reliability, security, observability, product thinking. **Not a chatbot. A governed, auditable casework system MOEI could pilot.**" |

### Failure-mode swap-ins (memorize these)

- **Live extraction fails on GOLDEN.** Say: "extraction layer fell back to the cached fixture — that's the reliability skill at work, the demo continues." Then point at the audit drawer where the fallback is logged.
- **Server crashes / port busy.** Say nothing. Switch to the backup video.
- **Judge interrupts mid-beat.** Answer briefly, return to the beat with: "to your question — and that's why we..."

---

## 90-second backup video script

Record this once, 1080p, before judging. Captures only the unkillable beats: golden + benchmark + one exception + close.

| Time | Beat | What's on screen | Voiceover |
|---|---|---|---|
| **0:00 – 0:10** | Title | Title card: *Agent Sanad — Housing Loan Arrears Rescheduling*. | "Today the Sheikh Zayed Housing Programme spends five working days reviewing each rescheduling request. Agent Sanad does the same job in under a second." |
| **0:10 – 0:30** | Golden case | Click GOLDEN. Pan camera to the Section 8 card. | "UAE PASS verified. Programme data auto-retrieved. Salary certificate parsed at AED 16,711. The engine applies the 20% cap, picks the UPDATE path, and proposes a compliant plan. 20% Pass. Period Pass. Approve." |
| **0:30 – 0:55** | Audit drawer + benchmark | Scroll to the audit drawer (3 seconds), then to the benchmark panel. | "Every field traces back to evidence or a fired rule. And the engine itself was replayed against 1,960 real Programme decisions — **94.6% path-match on held-out 2025, every plan within the 20% cap.**" |
| **0:55 – 1:15** | Exception beat | Click CONTRA. Show banner + fired rules INC-01, RSK-01. | "Adversarial test: the document contradicts the verification and contains injection text. The agent flags it, the rules do not change, and the case is referred. Document text is untrusted content — never policy logic." |
| **1:15 – 1:30** | Close | IBM 7-skills strip in focus. | "Built to the IBM Research agent-engineering playbook. Not a chatbot — a governed, auditable casework system." |

### Recording checklist

- [ ] OBS Studio at 1920×1080, 30 fps, MP4 output.
- [ ] Quit Slack, Discord, all notifications.
- [ ] Wi-Fi **off** while recording — proves offline mode is real.
- [ ] Mic gain set; record one test clip first.
- [ ] Save as `agent-sanad-backup-90s.mp4` in the project root.

---

## After the demo — what you put on screen for Q&A

Leave the GOLDEN case visible with the audit drawer expanded. That answers 60% of questions before they're asked.

The other 40% are in [`JUDGE_QA.md`](./JUDGE_QA.md).
