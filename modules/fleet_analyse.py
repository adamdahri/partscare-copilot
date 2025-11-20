from __future__ import annotations
import re
from pathlib import Path
from typing import Optional, List
import pandas as pd
import traceback

# =========================
# Helpers
# =========================
TAIL_RE = re.compile(r"(?:[A-Z0-9]{1,2}-?[A-Z0-9]{2,6}|N[0-9]{1,5}[A-Z]{0,2})$")

def is_tail(v) -> bool:
    if pd.isna(v): return False
    s = str(v).strip().upper()
    return bool(TAIL_RE.fullmatch(s))

def is_cn(v) -> bool:
    if pd.isna(v): return False
    s = str(v).strip()
    return bool(re.fullmatch(r"\d{4,6}", s))

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip())

def extract_status(raw: str) -> Optional[str]:
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.lower()
    allowed = [
        "on order","broken up","stored","withdrawn from use",
        "written off","status n/a","current"
    ]
    for phrase in allowed:
        if phrase in text:
            return phrase
    return None

# =========================
# Sheet-detectie robuust
# =========================
def load_download_sheet(xlsx_path: Path) -> pd.DataFrame:
    try:
        xls = pd.ExcelFile(xlsx_path)
        sheets = xls.sheet_names
        target = None
        for s in sheets:
            if any(k in s.lower() for k in ["download", "data", "export", "sheet1", "tab"]):
                target = s
                break
        if target is None:
            target = sheets[0]
        print(f"→ Geselecteerd sheet: {target}")

        # Lees zonder headers om consistentie te houden
        df = pd.read_excel(xlsx_path, sheet_name=target, header=None)
        df.columns = [f"col_{i}" for i in range(1, df.shape[1] + 1)]
        return df
    except Exception as e:
        raise RuntimeError(f"Fout bij het inlezen van Excel: {e}")

# =========================
# Dynamische kolomdetectie
# =========================
def guess_tail_and_cn_columns(df: pd.DataFrame) -> tuple[int, int]:
    possible_tail_cols, possible_cn_cols = [], []

    for col in df.columns[:6]:  # enkel eerste 6 kolommen scannen
        col_vals = df[col].dropna().astype(str).head(50)
        if col_vals.map(is_tail).any():
            possible_tail_cols.append(col)
        if col_vals.map(is_cn).any():
            possible_cn_cols.append(col)

    if not possible_tail_cols:
        possible_tail_cols = ["col_1"]
    if not possible_cn_cols:
        possible_cn_cols = ["col_3"]

    print(f"→ Gedetecteerde TAIL kolom: {possible_tail_cols[0]} | CN kolom: {possible_cn_cols[0]}")
    return possible_tail_cols[0], possible_cn_cols[0]

# =========================
# Fleet-tabel bouwen
# =========================
def build_fleet_table(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    tail_col, cn_col = guess_tail_and_cn_columns(df)
    anchors: List[int] = []

    for i, row in df.iterrows():
        if is_tail(row.get(tail_col)) and is_cn(row.get(cn_col)):
            anchors.append(i)

    if not anchors:
        print("⚠️ Geen TAIL/CN combinaties gevonden.")
        return pd.DataFrame(columns=[
            "TAIL","TYPE","CN","in'2cn","ENGINE","AIRFRAME_NOTE","OPERATOR","YEAR","STATUS"
        ])

    records = []
    for j, start in enumerate(anchors):
        end = anchors[j+1] - 1 if j+1 < len(anchors) else len(df)-1

        a = df.loc[start]
        tail = str(a.get(tail_col) or "").strip()
        typ  = str(a.get("col_2") or "").strip()
        cn   = str(a.get(cn_col) or "").strip()
        engine = str(a.get("col_5") or "").strip() if "col_5" in df else ""
        airframe_note = str(a.get("col_6") or "").strip() if "col_6" in df else ""
        operator = str(a.get("col_7") or "").strip() if "col_7" in df else ""
        year = a.get("col_8") if "col_8" in df else ""

        desc_lines = []
        for r in range(start+1, end+1):
            v = df.at[r, tail_col]
            if isinstance(v, str) and v.strip() and not is_tail(v):
                desc_lines.append(normalize_text(v))
        in2cn = " | ".join(desc_lines)

        status_val = None
        for r in range(start, end+1):
            st = extract_status(" ".join(map(str, df.loc[r].values)))
            if st: status_val = st; break
        if not status_val: status_val = "current"

        if pd.notna(year):
            try: year = int(float(year))
            except Exception: year = str(year).strip()
        else:
            year = ""

        records.append({
            "TAIL": tail,
            "TYPE": typ,
            "CN": cn,
            "in'2cn": in2cn,
            "ENGINE": engine,
            "AIRFRAME_NOTE": airframe_note,
            "OPERATOR": operator,
            "YEAR": year,
            "STATUS": status_val
        })

    out = pd.DataFrame.from_records(records)
    def cn_as_int(x):
        try: return int(str(x))
        except: return 0
    out = out.sort_values(by="CN", key=lambda s: s.map(cn_as_int)).reset_index(drop=True)
    return out

# =========================
# Wegschrijven naar Excel
# =========================
def write_fleet_sheet(input_path: Path) -> Path:
    try:
        raw = load_download_sheet(input_path)
        clean = build_fleet_table(raw)
        safe_name = input_path.stem.replace(" ", "_")
        output_path = input_path.with_name(f"{safe_name}_FLEET_ANALYSE.xlsx")

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            raw.to_excel(writer, index=False, header=False, sheet_name="raw_data")
            clean.to_excel(writer, index=False, sheet_name="FleetAnalyse")

        print(f"✅ Fleet Analyse voltooid: {output_path}")
        return output_path
    except Exception as e:
        error_file = input_path.with_name("fleet_error_log.txt")
        with open(error_file, "w") as f:
            f.write(traceback.format_exc())
        print(f"❌ Fout bij uitvoeren analyse: {e}\nTraceback opgeslagen in {error_file}")
        return error_file
 