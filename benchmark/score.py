"""Score the replay; report path-match + honest deviations — PRD 9. Holds out 2025."""
import numpy as np

def score(df, year=None):
    d = df if year is None else df[df["year"] == year]
    acc = (d["pred_path"] == d["APPROVED_REQUEST_TYPE"]).mean()
    upd = d[d["APPROVED_REQUEST_TYPE"] == "UPDATE_INSTALLMENT"]
    ta = d[d["APPROVED_REQUEST_TYPE"] == "TRANSFER_ARREARS"]
    pu, pt = d[d["pred_path"] == "UPDATE_INSTALLMENT"], d[d["pred_path"] == "TRANSFER_ARREARS"]
    m = d[(d["APPROVED_REQUEST_TYPE"] == "UPDATE_INSTALLMENT")
          & (d["pred_path"] == "UPDATE_INSTALLMENT") & (d["add_prem"] > 0)
          & (d["ADDITIONAL_MONTHS"].notna())]
    prem_err = (m["pred_prem"] - m["add_prem"]).abs()
    months_err = (m["pred_months"] - m["ADDITIONAL_MONTHS"]).abs()
    return {
        "n": int(len(d)),
        "path_match_accuracy": round(float(acc), 3),
        "update_recall": round(float((upd["pred_path"] == "UPDATE_INSTALLMENT").mean()), 3) if len(upd) else None,
        "update_precision": round(float((pu["APPROVED_REQUEST_TYPE"] == "UPDATE_INSTALLMENT").mean()), 3) if len(pu) else None,
        "transfer_recall": round(float((ta["pred_path"] == "TRANSFER_ARREARS").mean()), 3) if len(ta) else None,
        "transfer_precision": round(float((pt["APPROVED_REQUEST_TYPE"] == "TRANSFER_ARREARS").mean()), 3) if len(pt) else None,
        "twenty_pct_compliance_update_plans": round(float((pu["pred_ded_ratio"] <= 0.205).mean()), 3) if len(pu) else None,
        "premium_dev_median_aed": int(prem_err.median()) if len(m) else None,
        "months_dev_median": int(months_err.median()) if len(m) else None,
    }
