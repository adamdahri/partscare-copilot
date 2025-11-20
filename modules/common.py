from __future__ import annotations
import pandas as pd

STANDARD_COLUMNS = ["PN", "SN", "DESC", "ATA", "INTERVAL", "TSN", "TTSN", "NEXT_DUE", "LIMIT", "REMAINING", "SOURCE"]

def empty_result(source: str) -> pd.DataFrame:
    return pd.DataFrame(columns=STANDARD_COLUMNS).assign(SOURCE=source)

def normalize_df(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """
    Zet kolommen naar het standaard schema; ontbrekende kolommen worden toegevoegd.
    Verwacht minstens PN of DESC aanwezig te zijn.
    """
    df = df.copy()
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df["SOURCE"] = source
    return df[STANDARD_COLUMNS]
