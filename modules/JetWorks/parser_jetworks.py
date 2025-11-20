import fitz
import pandas as pd
import re
from pathlib import Path


# ----------------------------
# Regex patronen
# ----------------------------
DATE_RE = re.compile(
    r"\b\d{1,2}[-/ ]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]?\d{2,4}\b",
    re.I,
)
# exact ATA met -900- zoals in JetWorks
ATA_RE = re.compile(r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b")
PN_RE  = re.compile(r"(?:P/N|PN|PART\s*NO\.?|PART\s*NUMBER)[:=\s\-]*([A-Z0-9][A-Z0-9\-\/\.]+)", re.I)
SN_RE  = re.compile(r"(?:S/N|SN)[:=\s\-]*([A-Z0-9][A-Z0-9\-\/\.]+)", re.I)

DESC_HEAD_RE = re.compile(r"^(REMOVAL|INSTALLATION|REPLACEMENT|INSPECTION|OVERHAUL)\b", re.I)
NOISE_RE = re.compile(r"\b(MOS/MSC|HRS|AFL|TSN|TSR|TSX|PROC\.?\s*REF|MANUFACTURER|MODEL|UNIT|C/W)\b", re.I)


# ----------------------------
# Helpers
# ----------------------------
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def read_lines(pdf_path: str):
    """Leest tekst en geeft nette regels terug."""
    with fitz.open(pdf_path) as doc:
        text = "\n".join(p.get_text("text") for p in doc)
    return [norm(l) for l in text.splitlines() if norm(l)]


def first_match(pattern: re.Pattern, text: str, group: int = 1):
    m = pattern.search(text)
    return m.group(group) if m else ""


# ----------------------------
# Bouwen van ATA-blokken
# ----------------------------
def split_ata_blocks(lines):
    """
    Maak blokken op elke ATA-regel met -900-.
    DESCRIPTION:
      - eerst de tekst achter ATA op dezelfde regel
      - anders de eerstvolgende regel die begint met REMOVAL/INSTALLATION/...
      - anders eerste 'mooie' zin (zonder ruis) tussen ATA en PN/SN
    """
    blocks = []
    cur = None
    waiting_desc = False

    for ln in lines:
        m = ATA_RE.search(ln)
        if m:
            # sluit vorige af
            if cur:
                blocks.append(cur)

            cur = {"ATA REF": m.group(1), "DESCRIPTION": "", "lines": []}

            tail = norm(ln[m.end():])
            if tail:
                cur["DESCRIPTION"] = tail
            else:
                waiting_desc = True
            continue

        if cur:
            if waiting_desc:
                if DESC_HEAD_RE.match(ln):
                    cur["DESCRIPTION"] = norm(ln)
                    waiting_desc = False
                else:
                    # geen headword -> probeer alsnog later iets te vinden
                    waiting_desc = False
            else:
                cur["lines"].append(ln)

    if cur:
        blocks.append(cur)

    # Tweede kans voor lege descriptions: zoek eerste 'mooie' zin zonder ruis
    for b in blocks:
        if not b.get("DESCRIPTION"):
            for ln in b["lines"]:
                if NOISE_RE.search(ln):
                    continue
                # moet er een beetje "zin" uitzien en niet PN/SN
                if len(ln) > 10 and not re.search(r"^(PN|P/N|PART NO|PART NUMBER|SN)\b", ln, re.I):
                    b["DESCRIPTION"] = ln
                    break

    return blocks


# ----------------------------
# Extractie uit ATA-blok
# ----------------------------
def extract_from_block(block):
    """
    Haal PN, SN, DATE, HRS, AFL, INTERVAL uit een blok.
    Regels:
      - DATE: datum van het stuk (eerste datum in de eerste ~6 regels)
      - HRS/AFL: laatste waarde die we tegenkomen (als er meerdere staan)
      - INTERVAL: 'O/C' indien aanwezig, anders eerste 'los' getal
                 (geen TSN/TSR/TSX en niet PN/SN/PROC REF).
    """
    lines = block["lines"]
    buf = " ".join(lines)

    # PN & SN
    pn = first_match(PN_RE, buf)
    sn = first_match(SN_RE, buf)

    # DATE (vroeg in het blok)
    date_val = ""
    for ln in lines[:6]:
        md = DATE_RE.search(ln)
        if md:
            date_val = md.group(0)
            break

    # HRS & AFL
    hrs = ""
    afl = ""
    for ln in lines:
        mh = re.search(r"\bHRS\b[:\s]*([0-9]+(?::[0-9]{2})?|[0-9]+(?:[.,][0-9]{1,2})?)", ln, re.I)
        if mh:
            hrs = mh.group(1).replace(",", "")
        ma = re.search(r"\bAFL\b[:\s]*([0-9,]+)", ln, re.I)
        if ma:
            afl = ma.group(1).replace(",", "")

    # INTERVAL
    interval = ""
    if any("O/C" in x.upper() for x in lines):
        interval = "O/C"
    else:
        for ln in lines:
            if re.search(r"\bTSN|TSR|TSX\b", ln, re.I):
                continue
            if re.search(r"\b(PN|P/N|PART NO|PART NUMBER|SN|PROC\.?\s*REF)\b", ln, re.I):
                continue
            mg = re.search(r"\b(\d{1,6})\b", ln)  # integer
            if mg:
                interval = mg.group(1)
                break

    # Laatste fallbacks
    if not date_val:
        md = DATE_RE.search(buf)
        if md:
            date_val = md.group(0)

    if not hrs:
        mh = re.search(r"\b(?:ENG\.\s*)?HRS\b[:\s]*([0-9]+(?::[0-9]{2})?|[0-9]+(?:[.,][0-9]{1,2})?)", buf, re.I)
        if mh:
            hrs = mh.group(1).replace(",", "")

    if not afl:
        ma = re.search(r"\bAFL\b[:\s]*([0-9,]+)", buf, re.I)
        if ma:
            afl = ma.group(1).replace(",", "")

    # Bouw resultaat
    ata_ref = block.get("ATA REF", "")
    ata = ata_ref.split("-")[0] if ata_ref else ""

    return {
        "ATA": ata,
        "ATA REF": ata_ref,
        "DESCRIPTION": block.get("DESCRIPTION", ""),
        "PN": pn,
        "SN": sn,
        "DATE": date_val,
        "HRS": hrs,
        "AFL": afl,
        "INTERVAL": interval
    }


# ----------------------------
# Hoofdfuncties
# ----------------------------
def parse_jetworks(pdf_path: str) -> pd.DataFrame:
    lines = read_lines(pdf_path)
    ata_blocks = split_ata_blocks(lines)

    rows = []
    for b in ata_blocks:
        row = extract_from_block(b)

        # acceptatie: moet minstens kerninfo + usage hebben
        has_core = (row["PN"] or row["SN"] or row["DESCRIPTION"])
        has_usage = (row["HRS"] or row["AFL"])
        if has_core and has_usage:
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[["ATA", "ATA REF", "DESCRIPTION", "PN", "SN", "DATE", "HRS", "AFL", "INTERVAL"]]
    return df


def export_to_excel(pdf_path: str, output_path: str):
    df = parse_jetworks(pdf_path)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        print("⚠️ Geen onderdelen gevonden. (Controleer PDF-layout of pagina’s met ATA 900-blokken)")
    else:
        df.to_excel(out, index=False)
        print(f"✅ Bestand opgeslagen als: {out}  |  Regels: {len(df)}")
    return df


if __name__ == "__main__":
    pdf_in = r"data/input/7x Status Report.pdf"
    excel_out = r"data/output/JetWorks_Test.xlsx"
    export_to_excel(pdf_in, excel_out)
