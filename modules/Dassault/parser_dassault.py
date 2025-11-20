from __future__ import annotations
import re
import fitz  # PyMuPDF
import pandas as pd
from ..common import normalize_df, empty_result

HEADER_HINTS = ["status report", "dassault", "falcon", "camp systems"]

# eenvoudige regexes die je later mag verfijnen
PN_RE   = re.compile(r"\bPN[:\s]([A-Z0-9\-\/ ]+)", re.I)
SN_RE   = re.compile(r"\bSN[:\s]([A-Z0-9\-\/ ]+)", re.I)
ATA_RE  = re.compile(r"\bATA[:\s]?(\d{2}(?:\.\d{2})?)", re.I)
DESC_RE = re.compile(r"^\s*\d{5,}\s+(.+?)\s*$")  # regel met “345851  NO. 1 GPS SENSOR” → DESC
HRS_RE  = re.compile(r"\bHRS\b\s+([\d\.,]+)", re.I)
NEXT_RE = re.compile(r"\bNext Due\b.*?([0-9A-Z/:\-\. ]+)", re.I)

def is_dassault(text: str) -> bool:
    t = text.lower()
    return any(h in t for h in HEADER_HINTS)

def parse_dassault(pdf_path: str) -> pd.DataFrame:
    doc = fitz.open(pdf_path)
    rows = []

    for page in doc:
        text = page.get_text()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # blokken herkennen per onderdeel: lijn met groot nummer → omschrijving
        current_desc = ""
        current_pn = ""
        current_sn = ""
        current_ata = ""
        current_tsn = ""
        current_next = ""

        for ln in lines:
            # omschrijving
            m_desc = DESC_RE.match(ln)
            if m_desc:
                # als we bezig waren met vorige → pushen
                if current_desc or current_pn or current_sn:
                    rows.append({
                        "PN": current_pn.strip(),
                        "SN": current_sn.strip(),
                        "DESC": current_desc.strip(),
                        "ATA": current_ata,
                        "INTERVAL": "",
                        "TSN": current_tsn,
                        "TTSN": "",
                        "NEXT_DUE": current_next,
                        "LIMIT": "",
                        "REMAINING": "",
                    })
                current_desc = m_desc.group(1)
                current_pn = current_sn = current_ata = current_tsn = current_next = ""
                continue

            # PN / SN / ATA / HRS / Next Due
            if not current_pn:
                m = PN_RE.search(ln)
                if m: current_pn = m.group(1)

            if not current_sn:
                m = SN_RE.search(ln)
                if m: current_sn = m.group(1)

            if not current_ata:
                m = ATA_RE.search(ln)
                if m: current_ata = m.group(1)

            if not current_tsn:
                m = HRS_RE.search(ln)
                if m: current_tsn = m.group(1).replace(",", ".")

            if not current_next:
                m = NEXT_RE.search(ln)
                if m: current_next = m.group(1).strip()

        # laatste blok pushen
        if current_desc or current_pn or current_sn:
            rows.append({
                "PN": current_pn.strip(),
                "SN": current_sn.strip(),
                "DESC": current_desc.strip(),
                "ATA": current_ata,
                "INTERVAL": "",
                "TSN": current_tsn,
                "TTSN": "",
                "NEXT_DUE": current_next,
                "LIMIT": "",
                "REMAINING": "",
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return empty_result("Dassault")
    return normalize_df(df, "Dassault")
