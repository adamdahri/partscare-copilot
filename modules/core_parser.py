from __future__ import annotations
from pathlib import Path
import fitz
import pandas as pd

from .Dassault.parser_dassault import is_dassault, parse_dassault
from .Gulfstream.parser_gulfstream import is_gulfstream, parse_gulfstream
from .Bombardier.parser_bombardier import is_bombardier, parse_bombardier
from .JetWorks.parser_jetworks import is_jetworks, parse_jetworks
from .common import STANDARD_COLUMNS, empty_result

def detect_vendor(pdf_path: Path) -> str:
    text = ""
    with fitz.open(str(pdf_path)) as doc:
        # 2 pagina's lezen is vaak genoeg voor header/keywords
        for page in doc[:2]:
            text += page.get_text()

    if is_jetworks(text):
        return "JetWorks"
    if is_dassault(text):
        return "Dassault"
    if is_gulfstream(text):
        return "Gulfstream"
    if is_bombardier(text):
        return "Bombardier"
    return "UNKNOWN"

def parse_status_report(pdf_path: Path) -> pd.DataFrame:
    vendor = detect_vendor(pdf_path)
    if vendor == "JetWorks":
        return parse_jetworks(str(pdf_path))
    elif vendor == "Dassault":
        return parse_dassault(str(pdf_path))
    elif vendor == "Gulfstream":
        return parse_gulfstream(str(pdf_path))
    elif vendor == "Bombardier":
        return parse_bombardier(str(pdf_path))
    else:
        return empty_result("UNKNOWN")

def parse_many(paths: list[Path]) -> pd.DataFrame:
    frames = []
    for p in paths:
        df = parse_status_report(p)
        df = df.copy()
        df["FILE"] = p.name
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=STANDARD_COLUMNS + ["FILE"])
    return pd.concat(frames, ignore_index=True)
