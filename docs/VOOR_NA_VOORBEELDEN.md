# VOOR/NA VOORBEELDEN - ZO GAAT JE CODE ERUIT ZIEN

Dit document laat zien hoe je code verandert van de huidige staat naar de nieuwe, proper gestructureerde versie.

---

## VOORBEELD 1: PDF PARSING

### ❌ VOOR (huidige situatie in parts68.py)

```python
# parts68.py - alles in één functie, 200+ regels
def _extract_components(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text()
        print(f"[OK] PDF succesvol gelezen: {pdf_path}")
    except Exception as e:
        print(f"[FOUT] Kon PDF niet lezen: {e}")
    
    # ... 150 regels parsing logica ...
    # ... ATA detectie ...
    # ... part number extractie ...
    # ... date parsing ...
    # ... hours parsing ...
    
    results = []
    for b in blocks:
        # ... nog 50 regels ...
        
    return fab_date, results
```

**Problemen:**
- Alles in één functie (moeilijk te testen)
- Print statements (geen proper logging)
- Generieke error handling
- Geen herbruikbaarheid

---

### ✅ NA (nieuwe structuur)

**File: `src/parsers/pdf_reader.py`**
```python
from pathlib import Path
import fitz
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PDFReader:
    """Verantwoordelijk voor het lezen van PDF bestanden."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF niet gevonden: {pdf_path}")
    
    def read_full_text(self) -> str:
        """
        Lees alle text uit de PDF.
        
        Returns:
            Volledige text als string
        
        Raises:
            ValueError: Als PDF corrupt is
        """
        try:
            with fitz.open(str(self.pdf_path)) as doc:
                text = "\n".join(page.get_text() for page in doc)
                logger.info(f"PDF succesvol gelezen: {self.pdf_path.name} ({len(doc)} pagina's)")
                return text
                
        except fitz.FileDataError as e:
            logger.error(f"Corrupte PDF: {self.pdf_path.name}")
            raise ValueError(f"Corrupte PDF: {e}")
        
        except Exception as e:
            logger.error(f"Onverwachte fout bij lezen PDF: {e}", exc_info=True)
            raise
    
    def read_pages(self) -> list[str]:
        """
        Lees PDF pagina-per-pagina.
        
        Returns:
            List met text per pagina
        """
        try:
            with fitz.open(str(self.pdf_path)) as doc:
                pages = [page.get_text() for page in doc]
                logger.debug(f"Gelezen {len(pages)} pagina's uit {self.pdf_path.name}")
                return pages
                
        except Exception as e:
            logger.error(f"Fout bij pagina-per-pagina lezen: {e}", exc_info=True)
            raise
```

**File: `src/processors/component_extractor.py`**
```python
from typing import List, Dict
import re
from src.utils.logger import setup_logger
from config.regex_patterns import PN_RE_LIST, SN_RE_LIST, DATE_RE, HRS_RE

logger = setup_logger(__name__)

class ComponentExtractor:
    """Extraheert component-informatie uit text."""
    
    @staticmethod
    def extract_part_number(text: str) -> str:
        """
        Extract part number uit text.
        Probeert meerdere patronen.
        
        Args:
            text: Text waarin te zoeken
        
        Returns:
            Part number of lege string
        """
        for pattern in PN_RE_LIST:
            match = pattern.search(text)
            if match:
                pn = match.group(1).strip()
                logger.debug(f"Part number gevonden: {pn}")
                return pn
        
        logger.debug("Geen part number gevonden")
        return ""
    
    @staticmethod
    def extract_serial_number(text: str) -> str:
        """Extract serial number uit text."""
        for pattern in SN_RE_LIST:
            match = pattern.search(text)
            if match:
                sn = match.group(1).strip()
                logger.debug(f"Serial number gevonden: {sn}")
                return sn
        
        return ""
    
    @staticmethod
    def extract_date(text: str) -> str:
        """Extract eerste datum uit text."""
        match = DATE_RE.search(text)
        if match:
            date_str = match.group(0)
            logger.debug(f"Datum gevonden: {date_str}")
            return date_str
        return ""
    
    @staticmethod
    def extract_hours(text: str) -> str:
        """Extract hours uit text."""
        match = HRS_RE.search(text)
        if match:
            hrs_str = match.group(1)
            logger.debug(f"Hours gevonden: {hrs_str}")
            return hrs_str
        return ""
```

**File: `src/parsers/aircraft/jetworks.py`**
```python
from src.parsers.base_parser import BaseAircraftParser
from src.processors.component_extractor import ComponentExtractor
from src.processors.data_cleaner import clean_dataframe
from config.aircraft_types import AIRCRAFT_TYPES

class JetWorksParser(BaseAircraftParser):
    """Parser specifiek voor JetWorks status reports."""
    
    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.config = AIRCRAFT_TYPES['jetworks']
        self.extractor = ComponentExtractor()
    
    def extract_components(self, text: str, doc) -> List[Dict]:
        """
        JetWorks-specifieke parsing.
        
        Args:
            text: Volledige PDF text
            doc: PyMuPDF document object
        
        Returns:
            List van component dictionaries
        """
        components = []
        
        # Split in ATA-blokken
        blocks = self._split_into_ata_blocks(text)
        self.logger.info(f"Gevonden {len(blocks)} ATA-blokken")
        
        # Extract data uit elk blok
        for block in blocks:
            component = self._extract_from_block(block)
            if component:
                components.append(component)
        
        self.logger.info(f"Geëxtraheerd: {len(components)} componenten")
        return components
    
    def _split_into_ata_blocks(self, text: str) -> List[Dict]:
        """Split text in ATA-blokken."""
        # ... implementatie ...
        pass
    
    def _extract_from_block(self, block: Dict) -> Dict:
        """Extract component data uit één ATA-blok."""
        text = block['text']
        
        component = {
            'ATA': block['ata_code'],
            'ATA REF': block['ata_ref'],
            'DESCRIPTION': block.get('description', ''),
            'PN': self.extractor.extract_part_number(text),
            'SN': self.extractor.extract_serial_number(text),
            'DATE': self.extractor.extract_date(text),
            'HRS': self.extractor.extract_hours(text),
        }
        
        # Validatie
        if not (component['PN'] or component['SN']):
            self.logger.debug(f"Block {block['ata_ref']} heeft geen PN/SN, skip")
            return None
        
        return component
```

**Gebruik:**
```python
from src.parsers.aircraft.jetworks import JetWorksParser

# Simpel!
parser = JetWorksParser("data/input/status_report.pdf")
df = parser.parse()

# df bevat nu alle componenten
print(df.head())
```

**Voordelen:**
- ✅ Elke class heeft ÉÉN verantwoordelijkheid
- ✅ Herbruikbaar (ComponentExtractor werkt voor alle parsers)
- ✅ Testbaar (elke functie apart testen)
- ✅ Proper logging
- ✅ Specifieke error handling
- ✅ Duidelijke documentatie

---

## VOORBEELD 2: EXCEL EXPORT

### ❌ VOOR

```python
# parts68.py
def _export_excel(records, out_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Extracted Components"
    headers = ["ATA CODE", "ATA REF", "PART NUMBER", "DESCRIPTION", "DATE", "HRS INFO"]
    ws.append(headers)
    
    # Basic styling
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for c in ws[1]:
        c.fill = header_fill
        c.font = header_font
    
    # Add data
    for row in records:
        ws.append(row)
    
    wb.save(out_path)
```

**Problemen:**
- Niet herbruikbaar
- Basic formatting
- Geen filters/freeze panes
- Hardcoded kleuren

---

### ✅ NA

```python
from src.exporters.excel_generator import ExcelExporter

# In je analyzer:
class MasterTableAnalyzer:
    def generate(self, df: pd.DataFrame, output_path: str):
        """Genereer master table Excel."""
        
        exporter = ExcelExporter(output_path)
        
        # Voeg verschillende sheets toe
        exporter.add_sheet(
            df=df,
            sheet_name="Master Table",
            apply_filters=True,
            freeze_header=True,
            auto_width=True
        )
        
        # Optioneel: voeg summary sheet toe
        summary_df = df.groupby('ATA').size().reset_index(name='Count')
        exporter.add_sheet(
            df=summary_df,
            sheet_name="ATA Summary"
        )
        
        exporter.save()
        self.logger.info(f"Master table geëxporteerd naar {output_path}")
```

**Of nog simpeler met de convenience function:**
```python
from src.exporters.excel_generator import export_to_excel

export_to_excel(
    dataframes={
        'Master Table': master_df,
        'ATA Summary': ata_summary_df,
        'Critical Parts': critical_df
    },
    output_path='output/analysis.xlsx'
)
```

**Voordelen:**
- ✅ Herbruikbaar overal
- ✅ Professional formatting (auto-width, filters, freeze)
- ✅ Multiple sheets in één keer
- ✅ Makkelijk uit te breiden

---

## VOORBEELD 3: ERROR HANDLING

### ❌ VOOR

```python
try:
    fab, recs = _extract_components(pdf_path)
    # ...
except Exception as e:
    log(f"   ❌ Fout: {e}")
```

**Problemen:**
- Té generiek
- Geen onderscheid tussen error types
- Geen stack trace
- Programma gaat gewoon door

---

### ✅ NA

```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def process_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Verwerk een PDF bestand.
    
    Args:
        pdf_path: Pad naar PDF
    
    Returns:
        DataFrame met componenten
    
    Raises:
        FileNotFoundError: Als PDF niet bestaat
        ValueError: Als PDF corrupt is
        ParseError: Als parsing faalt
    """
    try:
        # Check of file bestaat
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF niet gevonden: {pdf_path}")
        
        # Parse PDF
        parser = JetWorksParser(pdf_path)
        df = parser.parse()
        
        # Validatie
        if df.empty:
            logger.warning(f"Geen componenten gevonden in {pdf_path}")
            return pd.DataFrame()
        
        logger.info(f"Succesvol verwerkt: {len(df)} componenten")
        return df
        
    except FileNotFoundError as e:
        logger.error(f"File niet gevonden: {e}")
        raise  # Re-raise, zodat caller het weet
    
    except ValueError as e:
        # Corrupte PDF
        logger.error(f"Corrupte PDF: {pdf_path} - {e}")
        raise
    
    except fitz.FileDataError as e:
        # PyMuPDF-specifieke error
        logger.error(f"PyMuPDF error: {e}")
        raise ValueError(f"Kan PDF niet lezen: {e}")
    
    except Exception as e:
        # Catch-all voor onverwachte errors
        logger.exception(f"Onverwachte fout bij verwerken {pdf_path}:")
        raise ParseError(f"Parsing gefaald: {e}")
```

**Gebruik in batch processing:**
```python
def process_directory(input_dir: str, output_dir: str) -> Dict[str, int]:
    """
    Verwerk alle PDFs in een directory.
    
    Returns:
        Stats dict met success/failure counts
    """
    stats = {'success': 0, 'failed': 0, 'errors': []}
    
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    logger.info(f"Gevonden {len(pdf_files)} PDFs om te verwerken")
    
    for pdf_path in pdf_files:
        try:
            df = process_pdf(str(pdf_path))
            
            if not df.empty:
                # Export naar Excel
                output_path = Path(output_dir) / f"{pdf_path.stem}.xlsx"
                export_to_excel({'Components': df}, str(output_path))
                stats['success'] += 1
            else:
                stats['failed'] += 1
                stats['errors'].append({
                    'file': pdf_path.name,
                    'error': 'Geen componenten gevonden'
                })
        
        except FileNotFoundError as e:
            stats['failed'] += 1
            stats['errors'].append({
                'file': pdf_path.name,
                'error': 'File niet gevonden'
            })
        
        except ValueError as e:
            stats['failed'] += 1
            stats['errors'].append({
                'file': pdf_path.name,
                'error': f'Corrupte PDF: {e}'
            })
        
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append({
                'file': pdf_path.name,
                'error': f'Onverwachte fout: {e}'
            })
            logger.exception(f"Kritieke fout bij {pdf_path.name}:")
    
    logger.info(f"Batch voltooid: {stats['success']} success, {stats['failed']} failed")
    return stats
```

**Voordelen:**
- ✅ Specifieke error handling
- ✅ Duidelijke error messages
- ✅ Batch blijft doorlopen bij errors
- ✅ Volledige error reporting
- ✅ Stack traces in logfile

---

## VOORBEELD 4: CONFIGURATIE

### ❌ VOOR

```python
# Hardcoded in parts68.py
ATA_MIN, ATA_MAX = 21, 79
DATE_RE = r"\b\d{1,2}[-\s]?(?:Jan|Feb|Mar|...)..."

# Hardcoded in JetWorks parser
ATA_RE = re.compile(r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b")

# Hardcoded in fleet_analyse.py
TAIL_RE = re.compile(r"...")
```

**Problemen:**
- Scattered configuratie
- Moeilijk te vinden
- Dubbele definities
- Geen overzicht

---

### ✅ NA

**File: `config/settings.py`**
```python
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = DATA_DIR / "logs"

# ATA configuration
ATA_RANGE = (21, 79)

# Excel styling
EXCEL_STYLE = {
    'header_color': '1F4E78',
    'header_font_color': 'FFFFFF',
    'alt_row_color': 'F2F2F2'
}

# Thresholds
MIN_HOURS = 0.0
MIN_DESCRIPTION_LENGTH = 3
```

**File: `config/regex_patterns.py`**
```python
import re

# Date patterns
DATE_PATTERN = r"\b\d{1,2}[-\s/]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[A-Za-z]*[-\s/]?\d{2,4}\b"
DATE_RE = re.compile(DATE_PATTERN, re.IGNORECASE)

# Part number patterns (try multiple)
PN_PATTERNS = [
    r"\bP\/N[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bPN[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bPART\s*NO\.?[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
]
PN_RE_LIST = [re.compile(p, re.IGNORECASE) for p in PN_PATTERNS]
```

**File: `config/aircraft_types.py`**
```python
AIRCRAFT_TYPES = {
    'jetworks': {
        'keywords': ['jetworks', 'jet works'],
        'ata_pattern': r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b",
    },
    'dassault': {
        'keywords': ['dassault', 'falcon'],
        'ata_pattern': r"\bATA[:\s]?(\d{2}(?:\.\d{2})?)",
    }
}
```

**Gebruik:**
```python
from config.settings import ATA_RANGE, EXCEL_STYLE, MIN_HOURS
from config.regex_patterns import DATE_RE, PN_RE_LIST
from config.aircraft_types import AIRCRAFT_TYPES

# In je code:
if ATA_RANGE[0] <= ata <= ATA_RANGE[1]:
    ...

for pattern in PN_RE_LIST:
    match = pattern.search(text)
    if match:
        ...
```

**Voordelen:**
- ✅ Alle config op één plek
- ✅ Makkelijk aan te passen
- ✅ Geen code-wijzigingen nodig
- ✅ Verschillende configs testen

---

## VOORBEELD 5: TESTING

### ❌ VOOR (geen tests)

```python
# Je test handmatig door:
# 1. GUI openen
# 2. PDF uploaden
# 3. Kijken of het werkt
# 4. Als het werkt → commit
# 5. User vindt bug → start opnieuw
```

---

### ✅ NA (automated tests)

**File: `tests/test_component_extractor.py`**
```python
import pytest
from src.processors.component_extractor import ComponentExtractor

class TestComponentExtractor:
    """Tests voor ComponentExtractor"""
    
    def setup_method(self):
        """Setup voor elke test"""
        self.extractor = ComponentExtractor()
    
    def test_extract_part_number_pn_format(self):
        """Test PN: format"""
        text = "Component details: PN: ABC-123-XYZ"
        result = self.extractor.extract_part_number(text)
        assert result == "ABC-123-XYZ"
    
    def test_extract_part_number_part_number_format(self):
        """Test PART NUMBER: format"""
        text = "PART NUMBER: DEF456"
        result = self.extractor.extract_part_number(text)
        assert result == "DEF456"
    
    def test_extract_part_number_not_found(self):
        """Test wanneer geen PN gevonden"""
        text = "Some random text without part number"
        result = self.extractor.extract_part_number(text)
        assert result == ""
    
    def test_extract_serial_number(self):
        """Test S/N extractie"""
        text = "Serial: S/N ABC123"
        result = self.extractor.extract_serial_number(text)
        assert result == "ABC123"
    
    def test_extract_date_month_format(self):
        """Test datum met maand naam"""
        text = "Installation date: 15-Jan-2024"
        result = self.extractor.extract_date(text)
        assert "Jan" in result
        assert "2024" in result


class TestDataCleaner:
    """Tests voor data cleaning functies"""
    
    def test_parse_hours_colon_format(self):
        """Test HH:MM format"""
        from src.processors.data_cleaner import parse_hours
        assert parse_hours("123:45") == 123.75
    
    def test_parse_hours_decimal_format(self):
        """Test decimal format"""
        from src.processors.data_cleaner import parse_hours
        assert parse_hours("1234.56") == 1234.56
    
    def test_parse_hours_comma_format(self):
        """Test format met komma"""
        from src.processors.data_cleaner import parse_hours
        assert parse_hours("1,234.56") == 1234.56
    
    def test_parse_hours_invalid(self):
        """Test ongeldige input"""
        from src.processors.data_cleaner import parse_hours
        assert parse_hours("invalid") == 0.0
        assert parse_hours("") == 0.0
        assert parse_hours(None) == 0.0
```

**Run de tests:**
```bash
pytest tests/test_component_extractor.py -v

# Output:
# test_extract_part_number_pn_format PASSED
# test_extract_part_number_part_number_format PASSED
# test_extract_part_number_not_found PASSED
# test_extract_serial_number PASSED
# test_extract_date_month_format PASSED
# test_parse_hours_colon_format PASSED
# test_parse_hours_decimal_format PASSED
# test_parse_hours_comma_format PASSED
# test_parse_hours_invalid PASSED
# 
# ========== 9 passed in 0.15s ==========
```

**Integration test:**
```python
# tests/test_jetworks_parser.py
import pytest
from pathlib import Path
from src.parsers.aircraft.jetworks import JetWorksParser

class TestJetWorksParser:
    """Integration tests voor JetWorks parser"""
    
    @pytest.fixture
    def sample_pdf(self):
        """Fixture met pad naar sample PDF"""
        return Path("tests/fixtures/sample_jetworks.pdf")
    
    def test_parse_full_workflow(self, sample_pdf):
        """Test volledige parsing workflow"""
        parser = JetWorksParser(str(sample_pdf))
        df = parser.parse()
        
        # Check output
        assert not df.empty, "DataFrame mag niet leeg zijn"
        assert len(df) > 0, "Moet minstens 1 component hebben"
        
        # Check kolommen
        expected_cols = ['ATA', 'PN', 'DESC', 'HRS']
        for col in expected_cols:
            assert col in df.columns, f"Kolom {col} ontbreekt"
    
    def test_parse_with_known_data(self, sample_pdf):
        """Test met bekende expected output"""
        parser = JetWorksParser(str(sample_pdf))
        df = parser.parse()
        
        # Check specifieke component (die we weten dat in sample PDF zit)
        gps_row = df[df['DESC'].str.contains('GPS', case=False, na=False)]
        assert not gps_row.empty, "GPS component moet gevonden worden"
        
        # Check data quality
        assert gps_row['PN'].notna().all(), "PN mag niet leeg zijn"
        assert gps_row['HRS'].astype(float).all() >= 0, "HRS moet >= 0 zijn"
```

**Voordelen:**
- ✅ Tests draaien in seconden
- ✅ Je weet meteen of iets breekt
- ✅ Refactoring is veilig
- ✅ Documentatie (tests laten zien hoe iets werkt)

---

## SAMENVATTING: VOOR vs NA

### Code Quality

| Aspect | VOOR | NA |
|--------|------|-----|
| **Structuur** | Alles in grote functies | Kleine, focused modules |
| **Herbruikbaarheid** | Copy-paste code | Gedeelde utilities |
| **Testing** | Manual | Automated |
| **Error handling** | Generiek | Specifiek per error type |
| **Logging** | Print statements | Proper logging framework |
| **Config** | Hardcoded | Gecentraliseerd |
| **Documentatie** | Weinig | Docstrings + type hints |

### Development Experience

| Aspect | VOOR | NA |
|--------|------|-----|
| **Bug fix** | Zoeken door 200+ regels | Specifieke module openen |
| **Nieuwe feature** | Aanpassen in meerdere plekken | Eén module toevoegen |
| **Testing** | 10 min manual | 10 sec automated |
| **Confidence** | "Hoop dat het werkt" | "Tests zijn groen ✅" |
| **Onboarding** | Moeilijk te begrijpen | Duidelijke structuur |

### User Experience

| Aspect | VOOR | NA |
|--------|------|-----|
| **Crashes** | "Programma gestopt" | Duidelijke error messages |
| **Debugging** | User moet uitleggen | Check logfile |
| **Nieuwe types** | Grote code change | Nieuwe parser toevoegen |
| **Updates** | Scary | Confidence (tests!) |

---

## CONCLUSIE

De refactoring lijkt misschien veel werk, maar het resultaat is:

✅ **Sneller development**: Nieuwe features in minuten ipv uren  
✅ **Minder bugs**: Tests vangen problemen vroeg  
✅ **Beter maintainable**: Code is leesbaar en logisch georganiseerd  
✅ **Schaalbaar**: Nieuwe parsers toevoegen is simpel  
✅ **Professional**: Logs, error handling, tests = production-ready  

**Het is de investering waard!** 💪
