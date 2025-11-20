from __future__ import annotations
import fitz, pandas as pd
from ..common import normalize_df, empty_result

def is_gulfstream(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in ["gulfstream", "gv", "g500", "g550", "camp systems"])

def parse_gulfstream(pdf_path: str) -> pd.DataFrame:
    # TODO: later echte extractie; nu lege tabel om de flow te testen
    return empty_result("Gulfstream")
