"""Replay the SAME deterministic rule used in production over historical rows — PRD 9.3."""
import math, pandas as pd

CAP, MIN_HEADROOM = 0.20, 50

def replay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["headroom"] = CAP * df["CURRENT_SALARY"] - df["CURRENT_EMI_AMT"].fillna(0)
    df["pred_path"] = df["headroom"].apply(
        lambda h: "UPDATE_INSTALLMENT" if h > MIN_HEADROOM else "TRANSFER_ARREARS")
    df["pred_prem"] = df["headroom"].apply(lambda h: math.floor(max(0.0, h)))
    df["pred_months"] = df.apply(
        lambda r: math.ceil(r["OVER_DUE_AMT"] / r["pred_prem"])
        if (r["pred_prem"] > 0 and r["OVER_DUE_AMT"] > 0) else 0, axis=1)
    df["new_total"] = df["CURRENT_EMI_AMT"].fillna(0) + df["pred_prem"]
    df["pred_ded_ratio"] = df["new_total"] / df["CURRENT_SALARY"]
    return df
