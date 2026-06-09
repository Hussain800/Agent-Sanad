"""Normalize the historical workbook (handles year-to-year schema drift) — PRD 9.2."""
import pandas as pd

def load(path: str) -> pd.DataFrame:
    frames = []
    for sheet in ["2023", "2024", "2025"]:
        d = pd.read_excel(path, sheet_name=sheet)
        d.columns = [c.strip() for c in d.columns]
        d["year"] = int(sheet)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    for c in ["CURRENT_SALARY", "OVER_DUE_AMT", "CURRENT_EMI_AMT",
              "NEW_EMI_AMT", "ADDITIONAL_MONTHS", "ADDITIONAL_PREMIUM"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # keep the two approved paths and rows with a usable salary
    df = df[df["APPROVED_REQUEST_TYPE"].isin(["UPDATE_INSTALLMENT", "TRANSFER_ARREARS"])]
    df = df[df["CURRENT_SALARY"].notna() & (df["CURRENT_SALARY"] > 0)].copy()
    df["add_prem"] = df["ADDITIONAL_PREMIUM"].fillna(0)   # canonical increment across years
    return df
