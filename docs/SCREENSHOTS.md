# Agent Sanad — Screenshot & Slide Plan

Two assets: **8 labeled screenshots** for the backup deck and submission, and **one polished benchmark slide** that you can drop into any deck or play standalone.

---

## 8 screenshots to capture

Pre-flight: `LOCAL_MOCK_MODE=true SANAD_LIVE_EXTRACTION=1 uvicorn ...`, browser at 1440×900, dark menubar hidden if possible.

Save as `docs/screenshots/NN-name.png`.

| # | File name | What's on screen | Notes |
|---|---|---|---|
| **1** | `01-golden-approve.png` | GOLDEN selected. Full page captured: status band (green), Section 8 table all 12 fields, beneficiary journey panel, 20%/Period chips. | The headline shot. This is what the rubric "Excellent" descriptor looks like in pixels. |
| **2** | `02-audit-drawer.png` | GOLDEN selected. Scroll the audit drawer into view; show 8+ audit events and the reasoning paragraph. | The "Why this plan?" trust beat. Capture so adapter calls + rule firings are both visible. |
| **3** | `03-extraction-live.png` | GOLDEN. "Retrieved and extracted" panel close-up. "Extraction source" row reads *"live: live parsed monthly income AED 16,711 from GOLDEN.txt"*. | Proves the live LLM/extraction touch is real, not staged. |
| **4** | `04-benchmark-panel.png` | GOLDEN. "Zero-bureaucracy impact" panel close-up. Manual ~5 days vs <1ms; path-match 94.6%; 20% compliance 100%; deviations. | The differentiator. This is the slide-ready capture. |
| **5** | `05-missing-doc.png` | MISSING selected. Status band (info blue), Section 8 shows Application Status = Incomplete, Recommendation = Request documents, DOC-01 in fired rules. | No false certainty. |
| **6** | `06-active-reject.png` | ACTIVE selected. Status band (danger red), badge says Reject, ACTIVE-01 in fired rules, plan = NONE. | Rule 3 fires at gate one — the governance proof. |
| **7** | `07-contradiction-injection.png` | CONTRA selected. Status band (warning amber), INC-01 + RSK-01 in fired rules, reasoning paragraph mentions the injected text. | Adversarial safety beat. |
| **8** | `08-ibm-7-skills-footer.png` | Any case, scrolled to bottom. The dark green USP strip with all 7 skills visible. | The architecture USP. Use this as the final slide too. |

**v1.1 functional expansion adds three more shots:**

| # | File name | What's on screen | Notes |
|---|---|---|---|
| **9** | `09-high-obligations.png` | HIGH_OBLIGATIONS selected. Amber scenario banner ("High obligations: …"), Section 8 shows Refer + UPDATE plan within cap, rule trace highlights OBL-01 as Refer effect. | Proves the assessment matrix considers obligations, not just salary. |
| **10** | `10-period-breach.png` | PERIOD_BREACH selected. Red scenario banner ("Period breach (Rule 2)…"), Period chip shows Fail, 20% shows Pass, calculation trace shows additional_months = 150 > 24 remaining. | Proves Rule 2 enforcement. |
| **11** | `11-hardship-approve.png` | HARDSHIP selected. Green scenario banner ("Verified temporary hardship (HARD-02)…"), Approve + TRANSFER_ARREARS, beneficiary status "Your verified circumstance has been recognised…". | Proves human-centred case handling. |
| **12** | `12-audit-drawer-v1-1.png` | Any case with audit drawer scrolled to show all 5 trace sections + raw feed. | The v1.1 trust upgrade. |

**Optional 13th:** `13-mobile-view.png` at 390×844 (iPhone size) showing the responsive collapse. Worth +1 point on Demo/UX if you have 30 seconds to set up Chrome devtools.

---

## The single benchmark slide

Make this in PowerPoint, Keynote, or just export from Figma. 16:9, 1920×1080. Five elements only — keep it ruthlessly clean.

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Agent Sanad — validated on real decisions                         │
│   ─────────────────────────────────────────                         │
│                                                                     │
│   We replayed our deterministic engine against 1,960 historical    │
│   Programme decisions from 2023–2025. Calibrated on 2023–2024,     │
│   validated on held-out 2025.                                       │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐                       │
│   │      94.6%       │  │       100%       │                       │
│   │  PATH MATCH      │  │  20% CAP         │                       │
│   │  (held-out 2025) │  │  COMPLIANCE      │                       │
│   │  n = 522         │  │  (by construction)│                      │
│   └──────────────────┘  └──────────────────┘                       │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐                       │
│   │   AED 557        │  │    10 months     │                       │
│   │  PREMIUM DEV     │  │  DURATION DEV    │                       │
│   │  (median)        │  │  (median)        │                       │
│   └──────────────────┘  └──────────────────┘                       │
│                                                                     │
│   We claim PATH MATCH + COMPLIANT TERMS, never exact reproduction. │
│   Officers apply discretion we deliberately route to a human.       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Slide copy (use verbatim)

**Title:** Agent Sanad — validated on real decisions

**Subhead:** Engine replayed against 1,960 historical decisions; calibrated 2023–24, validated on held-out 2025 (n=522).

**Big numbers (2×2):**
- **94.6%** Path-match (held-out 2025)
- **100%** within 20% cap (by construction)
- **AED 557** Premium deviation (median)
- **10 months** Duration deviation (median)

**Footer:** *We claim path-match and policy-compliant terms — never exact reproduction. Officers apply discretion the engine routes to a human officer.*

### Brand colors (federal-service palette)

| Use | Hex |
|---|---|
| Brand green (titles) | `#0b3d2e` |
| Brand gold (accent line) | `#b8902f` |
| Pass / success | `#177245` |
| Background | `#f4f6f8` |
| Body ink | `#172332` |
| Muted | `#5f6f82` |

---

## Optional: the architecture slide

If you have time for two slides, the second is the architecture diagram. Use the ASCII topology from [`ARCHITECTURE.md`](./ARCHITECTURE.md#system-topology) — render it as boxes, or just paste a screenshot of the IBM-skills mapping table.

The single line on the slide:
> **"LLM reads. Deterministic code decides. Human owns exceptions."**

---

## Submission packaging

Final folder structure for the submission ZIP:

```
agent-sanad-submission/
├── README.md                       (link to GitHub repo)
├── agent-sanad-backup-90s.mp4      (the 90s screencast)
├── benchmark-slide.png             (1920×1080 export)
├── architecture-slide.png          (optional)
├── screenshots/
│   ├── 01-golden-approve.png
│   ├── 02-audit-drawer.png
│   ├── 03-extraction-live.png
│   ├── 04-benchmark-panel.png
│   ├── 05-missing-doc.png
│   ├── 06-active-reject.png
│   ├── 07-contradiction-injection.png
│   ├── 08-ibm-7-skills-footer.png
│   └── 09-mobile-view.png          (optional)
└── docs/
    ├── ARCHITECTURE.md
    ├── DEMO_SCRIPTS.md
    └── JUDGE_QA.md
```

Hand the submission ZIP to the organizers; keep the GitHub repo as the source of truth for code.
