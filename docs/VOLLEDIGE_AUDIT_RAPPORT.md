# 🔍 PARTSCARE COPILOT - VOLLEDIGE TECHNISCHE AUDIT

**Datum:** 22 december 2024  
**Auditor:** Claude (Anthropic AI)  
**Project:** PartsCare Copilot v4.0  
**Eigenaar:** Adam Dahri / PartsCare

---

## 📋 EXECUTIVE SUMMARY

PartsCare Copilot is een **functionele en waardevolle tool** die al veel tijd bespaart voor het team. De huidige code werkt, maar er zijn belangrijke verbetermogelijkheden om:

✅ **Robuustheid te verhogen** (betere error handling, logging)  
✅ **Schaalbaarheid te verbeteren** (meer PDF-types toevoegen zonder alles te breken)  
✅ **Onderhoud te vereenvoudigen** (duidelijkere structuur, betere documentatie)  
✅ **Voorbereiding voor AI** (document indexatie, RAG-architectuur)

**Belangrijkste bevindingen:**
- ✅ Goede modulaire basis (type-specifieke parsers)
- ✅ Werkende GUI met professionele uitstraling
- ⚠️ Sommige modules zijn nog stubs (leeg)
- ⚠️ Inconsistente error handling
- ⚠️ Ontbrekende logging-strategie
- ⚠️ Geen unit tests
- ⚠️ Config hardcoded in verschillende modules

---

## 📊 DEEL 1: HUIDIGE STAAT VAN HET PROJECT

### 1.1 Wat werkt al goed? ✅

#### A. Projectstructuur
```
partscare-copilot-dev/
├── main.py                    # Console-versie met login
├── gui_main.py               # GUI-versie (macOS geoptimaliseerd)
├── requirements.txt          # Dependencies goed gedocumenteerd
├── data/
│   ├── database.json        # Gebruikersbeheer
│   ├── input/               # Test PDFs
│   └── output/              # Gegenereerde Excel bestanden
└── modules/
    ├── Bombardier/          # Type-specifieke parser
    ├── Dassault/            # Type-specifieke parser
    ├── Gulfstream/          # Type-specifieke parser
    ├── JetWorks/            # Type-specifieke parser (meest compleet)
    ├── common.py            # Gedeelde functies
    ├── database.py          # Gebruikersbeheer
    ├── fleet_analyse.py     # Fleet-analyse tool
    ├── parts68.py           # Hoofdanalyse (PDF → Excel)
    └── pdf_reader.py        # PDF-lezer
```

**✅ Positief:**
- Logische scheiding tussen verschillende vliegtuigtypes
- Herbruikbare `common.py` voor standaardisatie
- Duidelijke `data/` map voor input/output

#### B. Dependencies (requirements.txt)
```txt
PyMuPDF==1.26.5          # PDF-lezen (beste library!)
pandas==2.3.3            # Data-manipulatie
openpyxl==3.1.5          # Excel-generatie
matplotlib==3.10.7       # Visualisatie (nog niet gebruikt)
numpy, pillow, etc.      # Support libraries
```

**✅ Positief:**
- Moderne, stabiele versies
- PyMuPDF (fitz) is een uitstekende keuze voor PDF-parsing
- Pandas voor data-manipulatie is industriestandaard

#### C. Functionele features

**1. Parts68 Analyse (hoofd-module)**
- Leest PDF's pagina-per-pagina
- Extraheert: ATA, Part Number, Description, Date, Hours
- Genereert gestructureerde Excel met filtering
- Detecteert fabrication date automatisch
- Filters op ATA-code (21-79)

**2. Fleet Analyse**
- Verwerkt Excel-bestanden met vliegtuigdata
- Herkent automatisch TAIL en CN kolommen
- Extraheert status (on order, stored, current, etc.)
- Genereert clean output met extra sheet voor raw data

**3. GUI (gui_main.py)**
- Professionele uitstraling met gradient backgrounds
- Splash screen tijdens opstarten
- Auto-installer voor ontbrekende packages
- Thread-safe operaties (macOS fix)
- Progress bars tijdens verwerking

**4. Type-specifieke parsers**
- JetWorks: Meest complete parser met ATA-900 detectie
- Dassault: Parser voor Falcon status reports
- Bombardier & Gulfstream: Basis-structuur aanwezig

---

### 1.2 Wat kan beter? ⚠️

#### A. Ontbrekende of incomplete modules

**1. Lege/stub bestanden:**
```python
# modules/parts_analyse.py - bijna leeg
# modules/full_parts_analyse.py - bijna leeg  
# modules/core_parser.py - bestaat maar wordt nergens gebruikt
```

**Waarom is dit een probleem?**
- Verwarring: je weet niet welke modules actief zijn
- Maintenance: oude code blijft rondslingeren
- Import errors: als je deze probeert te gebruiken

**Oplossing:**
- Verwijder wat niet gebruikt wordt
- Of implementeer volledig met duidelijke documentatie

#### B. Error handling

**Huidige situatie:**
```python
# parts68.py - regel 200-201
except Exception as e:
    log(f"   ❌ Fout: {e}")
```

**Probleem:**
- Té generiek: je weet niet WAT er fout ging
- Geen stack trace: debugging wordt moeilijk
- Geen recovery: programma gaat gewoon door

**Wat je zou moeten hebben:**
```python
try:
    fab, recs = _extract_components(pdf_path)
except FileNotFoundError:
    log(f"   ❌ PDF niet gevonden: {pdf_path}")
    continue
except fitz.FileDataError as e:
    log(f"   ❌ Corrupte PDF: {e}")
    continue
except Exception as e:
    log(f"   ❌ Onverwachte fout: {e}")
    log(traceback.format_exc())
    continue
```

#### C. Logging

**Huidige situatie:**
- Console prints (`print()`)
- GUI heeft `log()` functie maar alleen in GUI
- Geen logbestand voor later debuggen

**Probleem:**
- Als iets faalt in productie, heb je geen geschiedenis
- Geen timestamps bij logs
- Moeilijk te debuggen zonder de user erbij

**Wat je zou moeten hebben:**
- Python's `logging` module
- Logbestanden in `logs/` map
- Verschillende log-levels (DEBUG, INFO, WARNING, ERROR)

#### D. Configuratie

**Huidige situatie - hardcoded overal:**
```python
# parts68.py
ATA_MIN, ATA_MAX = 21, 79
DATE_RE = r"\b\d{1,2}[-\s]?..."

# JetWorks parser
ATA_RE = re.compile(r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b")

# fleet_analyse.py
TAIL_RE = re.compile(r"...")
```

**Probleem:**
- Als je een regel wilt aanpassen, moet je door verschillende bestanden zoeken
- Moeilijk om verschillende configuraties te testen
- Geen overzicht van alle parameters

**Wat je zou moeten hebben:**
Een `config/settings.py`:
```python
# ATA-codes
ATA_RANGE = (21, 79)

# Regex patterns
PATTERNS = {
    'date': r"\b\d{1,2}[-\s]?...",
    'part_number': r"...",
    'serial_number': r"...",
}

# Vliegtuigtype-specifieke regels
AIRCRAFT_TYPES = {
    'jetworks': {
        'ata_format': r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b",
        'min_hrs': 0,
    },
    'dassault': {
        'keywords': ['falcon', 'dassault'],
    }
}
```

#### E. Database security

**Huidige situatie:**
```python
# database.py
{"username": "ADA", "password": "Adam2024$"}  # Plain text!
```

**Probleem:**
- Wachtwoord staat in plain text in JSON
- GitHub commit = iedereen kan inloggen
- Geen password hashing

**Wat je zou moeten hebben:**
```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# In database:
{"username": "ADA", "password_hash": "abc123..."}
```

#### F. Geen unit tests

**Huidige situatie:**
- Geen `tests/` map
- Alles is manual testing

**Probleem:**
- Als je iets wijzigt, weet je niet of oude functionaliteit breekt
- Nieuwe features introduceren bugs
- Refactoring is scary

**Wat je zou moeten hebben:**
```python
# tests/test_parts68.py
def test_extract_date():
    text = "Installation: 15-Jan-2024"
    date = _parse_date_any("15-Jan-2024")
    assert date == "15-Jan-2024"

def test_hours_conversion():
    assert _hours_to_float("123:45") == 123.75
    assert _hours_to_float("1,234.56") == 1234.56
```

---

### 1.3 Kritieke bevindingen 🚨

#### 1. PDF-parsing is fragiel

**Waarom faalt het soms?**

A. **Layout-verschillen:**
```python
# parts68.py - regel 83-86
for b in sorted(blocks, key=lambda x: (x[1], x[0])):
    text = _norm(b[4])
```

**Probleem:**
- PDF's kunnen text blocks in verschillende volgorde hebben
- Kolommen kunnen verschuiven
- Tabellen worden niet altijd correct herkend

**Voorbeeld scenario:**
```
PDF 1:           PDF 2:
ATA  | PN        PN  | ATA
23   | ABC123    ABC123 | 23
```

Je sorteert op Y-positie, maar als de kolommen andersom staan, haalt je parser de verkeerde data eruit.

**Oplossing:**
- Eerst de header-rij detecteren (bevat "ATA", "P/N", etc.)
- Dan kolommen herkennen op basis van header-labels
- Pas daarna data extraheren

B. **Regex te strikt:**
```python
ATA_REF_RE = re.compile(r"^\s*(\d{5,6})\b")
```

**Probleem:**
- Moet beginnen met 5-6 cijfers
- Wat als een PDF spaties heeft?
- Wat als het formaat net iets anders is?

**Oplossing:**
- Meerdere patronen proberen
- Fallback-strategie
- Confidence scoring

#### 2. Excel-output is basic

**Huidige situatie:**
```python
# parts68.py - regel 143-168
ws.append(headers)
# ... basic formatting ...
wb.save(out_path)
```

**Wat ontbreekt:**
- Geen filtering/sort knoppen in Excel
- Geen data validation
- Geen conditionele formatting (bijv. oude dates rood)
- Geen formulas (bijv. berekening van remaining hours)

#### 3. Geen duplicate detection

**Probleem:**
Als een onderdeel 2x in een PDF staat, komt het 2x in de Excel.

**Oplossing:**
```python
# Deduplicatie op basis van (ATA, PN, SN)
df = df.drop_duplicates(subset=['ATA', 'PN', 'SN'], keep='first')
```

---

## 🏗️ DEEL 2: VOORGESTELDE NIEUWE ARCHITECTUUR

### 2.1 High-level overzicht

```
partscare-copilot/
├── README.md
├── requirements.txt
├── requirements-dev.txt        # Voor development (pytest, black, etc.)
├── .gitignore
├── .env.example               # Template voor environment variables
├── setup.py                   # Voor installatie als package
│
├── config/                    # 📁 Configuratie
│   ├── __init__.py
│   ├── settings.py           # Algemene settings
│   ├── regex_patterns.py     # Alle regex patronen centraal
│   └── aircraft_types.py     # Type-specifieke configuratie
│
├── src/                       # 📁 Source code (alles wat executable is)
│   ├── __init__.py
│   │
│   ├── parsers/              # 📁 PDF-extractie
│   │   ├── __init__.py
│   │   ├── base_parser.py   # Abstract base class
│   │   ├── pdf_reader.py    # Core PDF-lezen
│   │   ├── text_extractor.py # Text + layout extractie
│   │   └── aircraft/        # Type-specifieke parsers
│   │       ├── __init__.py
│   │       ├── jetworks.py
│   │       ├── dassault.py
│   │       ├── bombardier.py
│   │       └── gulfstream.py
│   │
│   ├── processors/           # 📁 Data processing
│   │   ├── __init__.py
│   │   ├── data_cleaner.py  # Normalisatie, opschoning
│   │   ├── data_validator.py # Validatie van extracted data
│   │   └── deduplicator.py  # Duplicate detection
│   │
│   ├── analyzers/            # 📁 De 5 analyses
│   │   ├── __init__.py
│   │   ├── base_analyzer.py # Abstract base class
│   │   ├── master_table.py  # Analyse 1: Volledige tabel
│   │   ├── ata_summary.py   # Analyse 2: Per ATA
│   │   ├── critical_parts.py # Analyse 3: Kritieke onderdelen
│   │   ├── decision_synthesis.py # Analyse 4: Business view
│   │   └── partscare_export.py # Analyse 5: Intern formaat
│   │
│   ├── exporters/            # 📁 Excel-generatie
│   │   ├── __init__.py
│   │   ├── excel_generator.py # Core Excel functionaliteit
│   │   └── excel_formatter.py # Styling, formatting
│   │
│   ├── database/             # 📁 Database & auth
│   │   ├── __init__.py
│   │   ├── models.py        # Data models
│   │   ├── auth.py          # Login + password hashing
│   │   └── operations.py    # CRUD operations
│   │
│   ├── gui/                  # 📁 User interface
│   │   ├── __init__.py
│   │   ├── main_window.py   # Hoofd GUI
│   │   ├── login_window.py  # Login scherm
│   │   ├── splash_screen.py # Splash
│   │   └── widgets/         # Custom widgets
│   │       ├── __init__.py
│   │       ├── progress.py
│   │       └── log_viewer.py
│   │
│   ├── utils/                # 📁 Utilities
│   │   ├── __init__.py
│   │   ├── logger.py        # Logging setup
│   │   ├── file_handler.py  # File operations
│   │   └── validators.py    # Input validation
│   │
│   └── main.py               # Entry point
│
├── tests/                     # 📁 Unit tests
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── test_parsers/
│   │   ├── test_pdf_reader.py
│   │   ├── test_jetworks.py
│   │   └── ...
│   ├── test_processors/
│   ├── test_analyzers/
│   └── fixtures/             # Test data
│       ├── sample_pdfs/
│       └── expected_outputs/
│
├── data/                      # 📁 Data (NOT in Git)
│   ├── database.json
│   ├── input/
│   ├── output/
│   └── logs/                 # NEW: Log files
│
├── docs/                      # 📁 Documentatie
│   ├── user_guide.md
│   ├── developer_guide.md
│   ├── api_reference.md
│   └── changelog.md
│
└── scripts/                   # 📁 Helper scripts
    ├── setup_env.sh          # Environment setup
    ├── run_tests.sh          # Test runner
    └── build_exe.sh          # PyInstaller build
```

### 2.2 Waarom deze structuur?

#### A. Separation of Concerns

**Principe:** Elk onderdeel heeft één verantwoordelijkheid.

**Voorbeeld:**
- `parsers/` → alleen PDF lezen en text extractie
- `processors/` → alleen data cleaning en validatie
- `analyzers/` → alleen business logic (de 5 analyses)
- `exporters/` → alleen Excel generatie

**Voordeel:**
- Als je Excel-formatting wilt aanpassen → alleen in `exporters/`
- Als je een nieuwe parser wilt → alleen in `parsers/aircraft/`
- Tests zijn makkelijker (elke module apart testen)

#### B. Config vs Code

**Principe:** Instellingen zijn niet hardcoded, maar in config files.

**Voorbeeld:**
```python
# ❌ FOUT (hardcoded in code)
if ata >= 21 and ata <= 79:
    ...

# ✅ GOED (uit config)
from config.settings import ATA_RANGE
if ATA_RANGE[0] <= ata <= ATA_RANGE[1]:
    ...
```

**Voordeel:**
- Eén plek om alle regels te zien
- Makkelijk om te testen met verschillende configs
- Geen code-wijzigingen nodig voor parameter aanpassingen

#### C. Base classes

**Principe:** Herbruikbare basis-logica in abstract classes.

**Voorbeeld:**
```python
# parsers/base_parser.py
class BaseAircraftParser(ABC):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    def extract_components(self) -> pd.DataFrame:
        """Moet geïmplementeerd worden door subclass"""
        pass
    
    def validate_output(self, df: pd.DataFrame) -> bool:
        """Gedeelde validatie voor alle parsers"""
        if df.empty:
            self.logger.warning("Geen data geëxtraheerd")
            return False
        return True

# parsers/aircraft/jetworks.py
class JetWorksParser(BaseAircraftParser):
    def extract_components(self) -> pd.DataFrame:
        # Specifieke JetWorks logica
        ...
```

**Voordeel:**
- Minder code duplicatie
- Nieuwe parsers zijn makkelijker te bouwen
- Consistency: alle parsers werken hetzelfde

---

## 🔧 DEEL 3: STAP-VOOR-STAP REFACTORING PLAN

### Fase 1: Fundament (Week 1-2)

#### ✅ Stap 1: Virtual Environment + Git

**Wat je doet:**
```bash
# 1. Maak een schone venv
cd partscare-copilot
python -m venv venv

# 2. Activeer (Windows)
venv\Scripts\activate

# 3. Installeer dependencies
pip install -r requirements.txt

# 4. Git setup
git init
git add .
git commit -m "Initial commit - before refactoring"
git branch refactor/phase1
git checkout refactor/phase1
```

**Waarom?**
- Venv isoleert je project (geen conflicts met andere Python projecten)
- Git branch = je kunt altijd terug als iets breekt
- Clean state om mee te beginnen

**Tijd:** 30 minuten

---

#### ✅ Stap 2: Logging implementeren

**Nieuwe file: `src/utils/logger.py`**
```python
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_dir: str = "data/logs") -> logging.Logger:
    """
    Maakt een logger aan met beide console en file output.
    
    Args:
        name: Naam van de logger (meestal __name__ van je module)
        log_dir: Map waar logbestanden komen
    
    Returns:
        Configured logger instance
    """
    # Maak logs directory als die niet bestaat
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Logger aanmaken
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Voorkom duplicate handlers als logger al bestaat
    if logger.handlers:
        return logger
    
    # Console handler (alleen INFO en hoger)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (alles, inclusief DEBUG)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        f"{log_dir}/partscare_{today}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Handlers toevoegen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

**Hoe gebruik je dit?**
```python
# In elk bestand waar je logs wilt:
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Dan gebruik je:
logger.debug("Debugging info (alleen in logfile)")
logger.info("Normale info (console + logfile)")
logger.warning("Waarschuwing (console + logfile)")
logger.error("Fout (console + logfile)")

# Met exception info:
try:
    # something
except Exception as e:
    logger.exception("Er ging iets fout:")  # print ook stack trace
```

**Update in bestaande code:**
```python
# parts68.py - VOOR
print(f"[OK] PDF succesvol gelezen: {file_path}")
print(f"[FOUT] Kon PDF niet lezen: {e}")

# parts68.py - NA
logger.info(f"PDF succesvol gelezen: {file_path}")
logger.error(f"Kon PDF niet lezen: {e}", exc_info=True)
```

**Waarom?**
- Je hebt nu een geschiedenis van wat er gebeurde
- Debug-info staat in het bestand, niet in de console
- Professioneler (timestamps, log-levels)

**Tijd:** 2-3 uur (implementeren + testen)

---

#### ✅ Stap 3: Configuratie centraliseren

**Nieuwe files:**

**A. `config/settings.py`**
```python
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = DATA_DIR / "logs"
DATABASE_PATH = DATA_DIR / "database.json"

# ATA configuration
ATA_RANGE = (21, 79)  # Min en max ATA codes

# Excel configuration
EXCEL_ENGINE = "openpyxl"
EXCEL_STYLE = {
    'header_color': '1F4E78',
    'header_font_color': 'FFFFFF',
    'alt_row_color': 'F2F2F2'
}

# Parsing thresholds
MIN_HOURS = 0.0
MIN_DESCRIPTION_LENGTH = 3

# Duplicate detection
DUPLICATE_COLUMNS = ['ATA', 'PN', 'SN']
```

**B. `config/regex_patterns.py`**
```python
import re

# Date patterns
DATE_PATTERN = r"\b\d{1,2}[-\s/]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[A-Za-z]*[-\s/]?\d{2,4}\b"
DATE_RE = re.compile(DATE_PATTERN, re.IGNORECASE)

# Part number patterns
PN_PATTERNS = [
    r"\bP\/N[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bPN[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bPART\s*NO\.?[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bPART\s*NUMBER[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)"
]
PN_RE_LIST = [re.compile(p, re.IGNORECASE) for p in PN_PATTERNS]

# Serial number patterns
SN_PATTERNS = [
    r"\bS\/N[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
    r"\bSN[:\s]*([A-Z0-9][A-Z0-9\-\/\.]+)",
]
SN_RE_LIST = [re.compile(p, re.IGNORECASE) for p in SN_PATTERNS]

# Hours patterns
HRS_RE = re.compile(r"\bHRS[:\s]*([0-9.,:]+)", re.IGNORECASE)

# ATA reference pattern (5-6 digits)
ATA_REF_RE = re.compile(r"^\s*(\d{5,6})\b")
```

**C. `config/aircraft_types.py`**
```python
import re

AIRCRAFT_TYPES = {
    'jetworks': {
        'keywords': ['jetworks', 'jet works'],
        'ata_pattern': r"\b(\d{2}-\d{2}-\d{2}-900-\d{3}-\d{2})\b",
        'description_keywords': ['REMOVAL', 'INSTALLATION', 'REPLACEMENT', 'INSPECTION', 'OVERHAUL']
    },
    'dassault': {
        'keywords': ['dassault', 'falcon', 'camp systems'],
        'ata_pattern': r"\bATA[:\s]?(\d{2}(?:\.\d{2})?)",
        'description_pattern': r"^\s*\d{5,}\s+(.+?)\s*$"
    },
    'bombardier': {
        'keywords': ['bombardier', 'challenger', 'global'],
        'ata_pattern': r"\bATA[:\s]?(\d{2})",
    },
    'gulfstream': {
        'keywords': ['gulfstream'],
        'ata_pattern': r"\bATA[:\s]?(\d{2})",
    }
}

def detect_aircraft_type(text: str) -> str:
    """
    Detecteer welk vliegtuigtype dit PDF is op basis van keywords.
    
    Args:
        text: Eerste pagina's van de PDF als string
    
    Returns:
        Aircraft type key (bijv. 'jetworks') of 'unknown'
    """
    text_lower = text.lower()
    
    for type_name, config in AIRCRAFT_TYPES.items():
        for keyword in config['keywords']:
            if keyword in text_lower:
                return type_name
    
    return 'unknown'
```

**Update bestaande code:**
```python
# parts68.py - VOOR
ATA_MIN, ATA_MAX = 21, 79
DATE_RE = r"\b\d{1,2}[-\s]?..."

# parts68.py - NA
from config.settings import ATA_RANGE
from config.regex_patterns import DATE_RE, PN_RE_LIST

# In de functie:
if not (ata.isdigit() and ATA_RANGE[0] <= int(ata) <= ATA_RANGE[1]):
    continue
```

**Waarom?**
- Eén plek om alle regels te zien en aan te passen
- Makkelijk om te testen met verschillende configuraties
- Geen scattered magic numbers door de code

**Tijd:** 3-4 uur

---

### Fase 2: Code refactoring (Week 2-3)

#### ✅ Stap 4: Base Parser implementeren

**Doel:** Alle parsers werken hetzelfde, met dezelfde interface.

**Nieuwe file: `src/parsers/base_parser.py`**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import fitz

from src.utils.logger import setup_logger
from config.settings import MIN_HOURS, MIN_DESCRIPTION_LENGTH

class BaseAircraftParser(ABC):
    """
    Abstract base class voor alle aircraft-specific parsers.
    
    Elk vliegtuigtype (JetWorks, Dassault, etc.) implementeert deze class.
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.logger = setup_logger(self.__class__.__name__)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF niet gevonden: {pdf_path}")
    
    def parse(self) -> pd.DataFrame:
        """
        Hoofd-methode die alle stappen uitvoert.
        
        Returns:
            DataFrame met geëxtraheerde componenten
        """
        self.logger.info(f"Start parsing: {self.pdf_path.name}")
        
        try:
            # Stap 1: PDF openen
            doc = self._open_pdf()
            
            # Stap 2: Text extractie
            text = self._extract_text(doc)
            
            # Stap 3: Type-specifieke parsing (moet subclass implementeren)
            components = self.extract_components(text, doc)
            
            # Stap 4: Data cleaning
            df = self._clean_dataframe(components)
            
            # Stap 5: Validatie
            if self._validate_output(df):
                self.logger.info(f"Succesvol: {len(df)} componenten gevonden")
                return df
            else:
                self.logger.warning("Validatie gefaald")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.exception(f"Fout tijdens parsing: {e}")
            return pd.DataFrame()
    
    def _open_pdf(self) -> fitz.Document:
        """Open PDF met error handling"""
        try:
            return fitz.open(str(self.pdf_path))
        except fitz.FileDataError as e:
            raise ValueError(f"Corrupte PDF: {e}")
    
    def _extract_text(self, doc: fitz.Document) -> str:
        """Haal alle text uit de PDF"""
        return "\n".join(page.get_text() for page in doc)
    
    @abstractmethod
    def extract_components(self, text: str, doc: fitz.Document) -> List[Dict]:
        """
        Type-specifieke parsing logic.
        Moet geïmplementeerd worden door subclass.
        
        Args:
            text: Volledige text van PDF
            doc: PyMuPDF document object (voor page-by-page access)
        
        Returns:
            List van dictionaries met component data
        """
        pass
    
    def _clean_dataframe(self, components: List[Dict]) -> pd.DataFrame:
        """Zet list of dicts om naar clean DataFrame"""
        if not components:
            return pd.DataFrame()
        
        df = pd.DataFrame(components)
        
        # Filter op minimale voorwaarden
        if 'HRS' in df.columns:
            df = df[df['HRS'].astype(float) >= MIN_HOURS]
        
        if 'DESC' in df.columns:
            df = df[df['DESC'].str.len() >= MIN_DESCRIPTION_LENGTH]
        
        # Duplicates verwijderen
        from config.settings import DUPLICATE_COLUMNS
        cols_present = [c for c in DUPLICATE_COLUMNS if c in df.columns]
        if cols_present:
            df = df.drop_duplicates(subset=cols_present, keep='first')
        
        return df
    
    def _validate_output(self, df: pd.DataFrame) -> bool:
        """Check of output valide is"""
        if df.empty:
            self.logger.warning("Geen componenten gevonden")
            return False
        
        # Check required columns
        required = ['ATA', 'PN']
        missing = [col for col in required if col not in df.columns]
        if missing:
            self.logger.error(f"Missende kolommen: {missing}")
            return False
        
        return True
```

**Implementeer in JetWorks:**

**Nieuwe file: `src/parsers/aircraft/jetworks.py`**
```python
from src.parsers.base_parser import BaseAircraftParser
from config.aircraft_types import AIRCRAFT_TYPES
import re

class JetWorksParser(BaseAircraftParser):
    """Parser voor JetWorks status reports"""
    
    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.config = AIRCRAFT_TYPES['jetworks']
        self.ata_re = re.compile(self.config['ata_pattern'])
    
    def extract_components(self, text: str, doc) -> List[Dict]:
        """JetWorks-specific parsing logic"""
        components = []
        
        # Splits text in lijnen
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Bouw ATA-blokken
        blocks = self._split_ata_blocks(lines)
        
        # Extract data uit elk blok
        for block in blocks:
            component = self._extract_from_block(block)
            if component:
                components.append(component)
        
        return components
    
    def _split_ata_blocks(self, lines: List[str]) -> List[Dict]:
        """Splits lijnen in ATA-blokken"""
        # ... (je huidige logica vanuit JetWorks parser)
        pass
    
    def _extract_from_block(self, block: Dict) -> Optional[Dict]:
        """Haal data uit één ATA-blok"""
        # ... (je huidige logica vanuit JetWorks parser)
        pass
```

**Waarom?**
- Elke parser werkt nu consistent (open PDF → extract → clean → validate)
- Nieuwe parsers zijn veel makkelijker (copy template, implementeer extract_components())
- Testing is simpeler (elke stap apart testen)

**Tijd:** 1 dag

---

#### ✅ Stap 5: Processors implementeren

**Data cleaning in aparte module.**

**Nieuwe file: `src/processors/data_cleaner.py`**
```python
import re
import pandas as pd
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def normalize_text(s: str) -> str:
    """
    Normaliseer text: remove dubbele spaties, strip whitespace.
    
    Args:
        s: Input string
    
    Returns:
        Genormaliseerde string
    """
    if not isinstance(s, str):
        return str(s).strip()
    return re.sub(r"\s+", " ", s).strip()

def parse_date(date_str: str) -> str:
    """
    Parse een datum string naar gestandaardiseerd formaat DD-MMM-YYYY.
    
    Args:
        date_str: Datum in willekeurig formaat
    
    Returns:
        Gestandaardiseerde datum of lege string als parsing faalt
    
    Examples:
        >>> parse_date("15/Jan/2024")
        "15-Jan-2024"
        >>> parse_date("01-02-2024")
        "01-Feb-2024"
    """
    if not date_str or pd.isna(date_str):
        return ""
    
    # Normaliseer separators
    date_str = str(date_str).replace("/", "-").replace(".", "-")
    date_str = re.sub(r"\s+", "-", date_str).strip()
    
    # Probeer verschillende formaten
    formats = [
        "%d-%b-%Y",    # 15-Jan-2024
        "%d-%b-%y",    # 15-Jan-24
        "%d-%B-%Y",    # 15-January-2024
        "%d-%B-%y",    # 15-January-24
        "%d-%m-%Y",    # 15-01-2024
        "%d-%m-%y",    # 15-01-24
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.title(), fmt)
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            continue
    
    logger.warning(f"Kon datum niet parsen: {date_str}")
    return ""

def parse_hours(hours_str: str) -> float:
    """
    Parse hours string naar float.
    Ondersteunt formats: "123:45", "1,234.56", "1234"
    
    Args:
        hours_str: Hours als string
    
    Returns:
        Hours als float, of 0.0 als parsing faalt
    
    Examples:
        >>> parse_hours("123:45")
        123.75
        >>> parse_hours("1,234.56")
        1234.56
    """
    if not hours_str or pd.isna(hours_str):
        return 0.0
    
    hours_str = str(hours_str).replace(",", ".").strip()
    
    # Format HH:MM
    m = re.match(r"^(\d+):(\d{2})$", hours_str)
    if m:
        hrs = int(m.group(1))
        mins = int(m.group(2))
        return hrs + (mins / 60.0)
    
    # Format met decimalen
    try:
        return float(re.sub(r"[^\d.]", "", hours_str))
    except ValueError:
        logger.warning(f"Kon hours niet parsen: {hours_str}")
        return 0.0

def clean_part_number(pn: str) -> str:
    """Cleanup part number: uppercase, remove extra spaces"""
    if not pn or pd.isna(pn):
        return ""
    return normalize_text(str(pn)).upper()

def clean_serial_number(sn: str) -> str:
    """Cleanup serial number: uppercase, remove extra spaces"""
    return clean_part_number(sn)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean een DataFrame met component data.
    
    Args:
        df: Raw DataFrame met componenten
    
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Text kolommen normaliseren
    text_cols = ['DESC', 'DESCRIPTION']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)
    
    # Part numbers & serial numbers
    if 'PN' in df.columns:
        df['PN'] = df['PN'].apply(clean_part_number)
    if 'SN' in df.columns:
        df['SN'] = df['SN'].apply(clean_serial_number)
    
    # Dates
    if 'DATE' in df.columns:
        df['DATE'] = df['DATE'].apply(parse_date)
    
    # Hours
    if 'HRS' in df.columns:
        df['HRS'] = df['HRS'].apply(parse_hours)
    if 'AFL' in df.columns:
        df['AFL'] = df['AFL'].apply(parse_hours)  # Cycles ook als float
    
    # Remove volledig lege rijen
    df = df.dropna(how='all')
    
    # Remove rijen waar alle key fields leeg zijn
    key_fields = ['PN', 'SN', 'DESC', 'DESCRIPTION']
    present_keys = [k for k in key_fields if k in df.columns]
    if present_keys:
        df = df.dropna(subset=present_keys, how='all')
    
    logger.info(f"DataFrame cleaned: {len(df)} rijen behouden")
    return df
```

**Waarom?**
- Data cleaning is nu herbruikbaar door alle parsers
- Tests zijn makkelijk (input → output voor elke functie)
- Consistency: alle dates, hours, etc. worden hetzelfde behandeld

**Tijd:** 3-4 uur

---

### Fase 3: Features (Week 3-4)

#### ✅ Stap 6: Excel export verbeteren

**Nieuwe file: `src/exporters/excel_generator.py`**
```python
import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

from src.utils.logger import setup_logger
from config.settings import EXCEL_STYLE

logger = setup_logger(__name__)

class ExcelExporter:
    """
    Professional Excel exporter met formatting.
    """
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.wb = Workbook()
        self.wb.remove(self.wb.active)  # Remove default sheet
    
    def add_sheet(self, 
                  df: pd.DataFrame, 
                  sheet_name: str,
                  apply_filters: bool = True,
                  freeze_header: bool = True,
                  auto_width: bool = True) -> None:
        """
        Voeg een sheet toe met DataFrame data.
        
        Args:
            df: DataFrame om te exporteren
            sheet_name: Naam van de sheet
            apply_filters: Zet autofilter aan
            freeze_header: Freeze eerste rij
            auto_width: Automatische kolombreedte
        """
        if df.empty:
            logger.warning(f"DataFrame voor {sheet_name} is leeg")
            return
        
        # Maak nieuwe sheet
        ws = self.wb.create_sheet(title=sheet_name)
        
        # Voeg data toe
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            ws.append(row)
        
        # Styling
        self._style_header(ws)
        
        if apply_filters and ws.max_row > 1:
            ws.auto_filter.ref = ws.dimensions
        
        if freeze_header:
            ws.freeze_panes = ws["A2"]
        
        if auto_width:
            self._auto_width_columns(ws)
        
        # Alternating row colors
        self._apply_alternating_rows(ws)
        
        logger.info(f"Sheet '{sheet_name}' toegevoegd: {len(df)} rijen")
    
    def _style_header(self, ws):
        """Style de header rij"""
        header_fill = PatternFill(
            start_color=EXCEL_STYLE['header_color'],
            end_color=EXCEL_STYLE['header_color'],
            fill_type="solid"
        )
        header_font = Font(
            color=EXCEL_STYLE['header_font_color'],
            bold=True
        )
        header_alignment = Alignment(
            horizontal="center",
            vertical="center"
        )
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
    
    def _apply_alternating_rows(self, ws):
        """Apply alternating row colors"""
        alt_fill = PatternFill(
            start_color=EXCEL_STYLE['alt_row_color'],
            end_color=EXCEL_STYLE['alt_row_color'],
            fill_type="solid"
        )
        
        for row_num in range(2, ws.max_row + 1, 2):
            for cell in ws[row_num]:
                cell.fill = alt_fill
    
    def _auto_width_columns(self, ws):
        """Set auto-width voor kolommen"""
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 3, 50)  # Max 50
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def save(self):
        """Sla workbook op"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(str(self.output_path))
        logger.info(f"Excel bestand opgeslagen: {self.output_path}")

# Convenience function
def export_to_excel(dataframes: Dict[str, pd.DataFrame], output_path: str):
    """
    Export multiple DataFrames naar één Excel bestand.
    
    Args:
        dataframes: Dict van {sheet_name: DataFrame}
        output_path: Pad waar Excel bestand komt
    
    Example:
        >>> export_to_excel({
        ...     'Master Table': master_df,
        ...     'ATA Summary': ata_df,
        ...     'Critical Parts': critical_df
        ... }, 'output/analysis.xlsx')
    """
    exporter = ExcelExporter(output_path)
    
    for sheet_name, df in dataframes.items():
        exporter.add_sheet(df, sheet_name)
    
    exporter.save()
```

**Waarom?**
- Professionele Excel outputs (filters, frozen headers, alternating rows)
- Herbruikbaar voor alle analyses
- Gemakkelijk uit te breiden (grafieken, conditional formatting, etc.)

**Tijd:** 4-5 uur

---

## 🤖 DEEL 4: VOORBEREIDING VOOR AI / RAG

### 4.1 Wat is RAG?

**RAG = Retrieval Augmented Generation**

**In simpele woorden:**
Je geeft een AI niet alleen een vraag, maar ook de relevante documentatie erbij.

**Voorbeeld:**
```
Vraag: "Wat is de IPC-referentie voor de GPS sensor in een Falcon 7X?"

Zonder RAG:
AI: "Ik weet het niet, want dit is specifieke technische info."

Met RAG:
1. Systeem zoekt in geïndexeerde IPC-documenten van Falcon 7X
2. Vindt relevante pagina's (bijv. pagina 234, sectie 34-11)
3. Geeft deze pagina's mee aan de AI
4. AI: "Volgens IPC pagina 234, sectie 34-11: de GPS sensor heeft 
        referentie 34-11-01 met part number ABC123."
```

### 4.2 Hoe ga je dit bouwen?

#### Fase 1: Document indexatie

**Wat je nodig hebt:**
1. **Alle documentatie verzamelen:**
   - IPC's per vliegtuigtype
   - AMM's per vliegtuigtype
   - Technische manuals
   - Interne analyses

2. **Metadata extractie:**
   ```python
   document = {
       'aircraft_type': 'Falcon 7X',
       'document_type': 'IPC',
       'section': '34-11',
       'page_number': 234,
       'content': "...",  # Text van deze pagina
       'part_numbers_mentioned': ['ABC123', 'XYZ789'],
       'ata_codes': ['34']
   }
   ```

3. **Vector database:**
   - Text wordt omgezet in "vectors" (getallen)
   - Vergelijkbare text heeft vergelijkbare vectors
   - Je kunt zoeken op "meaning" niet alleen keywords

**Tools die je nodig hebt:**
- **ChromaDB** of **Pinecone**: vector databases
- **OpenAI Embeddings** of **Sentence Transformers**: text → vectors
- **LangChain**: framework voor RAG

#### Fase 2: RAG pipeline

**Nieuwe directory structuur:**
```
src/
├── ai/
│   ├── __init__.py
│   ├── document_indexer.py    # Index PDF's
│   ├── vector_store.py        # Vector database wrapper
│   ├── retriever.py           # Zoek relevante docs
│   └── rag_pipeline.py        # AI + retrieval
```

**Voorbeeld code:**

**`src/ai/document_indexer.py`**
```python
import fitz
from pathlib import Path
from typing import List, Dict
import chromadb

class DocumentIndexer:
    """Index technische documentatie voor RAG"""
    
    def __init__(self, db_path: str = "data/vector_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="aircraft_docs"
        )
    
    def index_pdf(self, 
                  pdf_path: Path, 
                  aircraft_type: str,
                  document_type: str) -> None:
        """
        Index één PDF document.
        
        Args:
            pdf_path: Pad naar PDF
            aircraft_type: bijv. 'Falcon 7X'
            document_type: bijv. 'IPC', 'AMM'
        """
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            
            # Extract metadata
            metadata = {
                'aircraft_type': aircraft_type,
                'document_type': document_type,
                'filename': pdf_path.name,
                'page_number': page_num,
            }
            
            # Add to vector store
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[f"{pdf_path.stem}_p{page_num}"]
            )
        
        print(f"Indexed: {pdf_path.name} ({len(doc)} pages)")
    
    def index_directory(self, 
                       dir_path: Path,
                       aircraft_type: str,
                       document_type: str) -> None:
        """Index alle PDFs in een directory"""
        for pdf_file in dir_path.glob("*.pdf"):
            self.index_pdf(pdf_file, aircraft_type, document_type)
```

**`src/ai/retriever.py`**
```python
from typing import List, Dict

class DocumentRetriever:
    """Zoek relevante documenten op basis van een vraag"""
    
    def __init__(self, collection):
        self.collection = collection
    
    def search(self, 
               query: str,
               aircraft_type: str = None,
               top_k: int = 5) -> List[Dict]:
        """
        Zoek relevante document passages.
        
        Args:
            query: De vraag/zoekterm
            aircraft_type: Filter op vliegtuigtype
            top_k: Hoeveel resultaten
        
        Returns:
            List van resultaten met content + metadata
        """
        # Build filter
        where_filter = {}
        if aircraft_type:
            where_filter['aircraft_type'] = aircraft_type
        
        # Search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        # Format results
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'relevance_score': results['distances'][0][i]
            })
        
        return formatted
```

**`src/ai/rag_pipeline.py`**
```python
from openai import OpenAI

class RAGPipeline:
    """RAG pipeline: retrieve + generate"""
    
    def __init__(self, retriever, openai_api_key: str):
        self.retriever = retriever
        self.client = OpenAI(api_key=openai_api_key)
    
    def query(self, 
              question: str,
              aircraft_type: str = None) -> Dict:
        """
        Beantwoord een vraag met RAG.
        
        Args:
            question: De vraag
            aircraft_type: Filter op type
        
        Returns:
            Dict met answer en bronnen
        """
        # 1. Retrieve relevante documenten
        docs = self.retriever.search(
            query=question,
            aircraft_type=aircraft_type,
            top_k=3
        )
        
        # 2. Build context
        context = "\n\n---\n\n".join([
            f"[{d['metadata']['document_type']} - "
            f"Page {d['metadata']['page_number']}]\n{d['content']}"
            for d in docs
        ])
        
        # 3. Build prompt
        prompt = f"""Je bent een technisch assistent voor luchtvaart.
Beantwoord de vraag op basis van de gegeven documentatie.
Als het antwoord niet in de documentatie staat, zeg dan "Ik kan deze informatie niet vinden in de beschikbare documentatie."

DOCUMENTATIE:
{context}

VRAAG: {question}

ANTWOORD (met bronvermelding):"""
        
        # 4. Generate answer
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een technisch assistent."},
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # 5. Return met bronnen
        return {
            'answer': answer,
            'sources': [
                {
                    'document': d['metadata']['filename'],
                    'page': d['metadata']['page_number'],
                    'relevance': d['relevance_score']
                }
                for d in docs
            ]
        }
```

**Gebruik:**
```python
# Setup
indexer = DocumentIndexer()
indexer.index_directory(
    Path("data/manuals/falcon_7x/ipc"),
    aircraft_type="Falcon 7X",
    document_type="IPC"
)

# Query
rag = RAGPipeline(retriever, openai_api_key="...")
result = rag.query(
    "Wat is de part number van de GPS sensor?",
    aircraft_type="Falcon 7X"
)

print(result['answer'])
print(f"Bronnen: {result['sources']}")
```

### 4.3 Roadmap naar AI Copilot

**Maand 1-2: Fundament**
- ✅ Projectstructuur proper
- ✅ Config + logging
- ✅ Base parsers werkend
- ✅ Tests geschreven

**Maand 3: Document indexatie**
- Alle manuals verzamelen
- Indexatie pipeline bouwen
- Vector database opzetten
- Testen met sample queries

**Maand 4: RAG MVP**
- Simpele query interface
- RAG pipeline implementeren
- Evaluatie van antwoorden
- Fine-tuning van retrieval

**Maand 5: GUI integratie**
- AI copilot tab in GUI
- Chat-interface
- Bronvermelding weergeven
- Feedback systeem

**Maand 6+: Advanced features**
- Multi-modal (images uit PDFs)
- Automatische metadata extractie
- Conversational memory
- Export naar rapport

---

## 📝 DEEL 5: EDUCATIEVE UITLEG - HOE WERKT DIT ALLEMAAL?

### 5.1 Python Basics die je moet snappen

#### A. Wat zijn modules?

**Simpel gezegd:**
Een module is een Python-bestand met functies die je kunt hergebruiken.

**Voorbeeld:**
```python
# calculator.py (dit is een module)
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

# main.py (dit gebruikt de module)
from calculator import add, subtract

result = add(5, 3)  # 8
```

**Waarom is dit nuttig?**
- Je hoeft niet alles in één bestand te hebben
- Code is herbruikbaar
- Makkelijker te testen

#### B. Wat zijn packages?

**Simpel gezegd:**
Een package is een map met modules erin.

**Voorbeeld:**
```
math_tools/           # Dit is een package
├── __init__.py      # Maakt het een package (mag leeg zijn)
├── calculator.py    # Module 1
└── geometry.py      # Module 2

# Gebruik:
from math_tools.calculator import add
from math_tools.geometry import area_circle
```

**De `__init__.py` file:**
```python
# math_tools/__init__.py
from .calculator import add, subtract
from .geometry import area_circle

# Nu kan je dit doen:
from math_tools import add, area_circle
```

#### C. Wat zijn classes?

**Simpel gezegd:**
Een class is een "template" voor objecten.

**Voorbeeld zonder class (repetitief):**
```python
# Vliegtuig 1
plane1_type = "Falcon 7X"
plane1_tail = "N123AB"
plane1_hours = 5000

# Vliegtuig 2
plane2_type = "Global 6000"
plane2_tail = "N456CD"
plane2_hours = 3000

# Je moet overal plane1_, plane2_ etc. schrijven
```

**Voorbeeld met class (clean):**
```python
class Aircraft:
    def __init__(self, aircraft_type, tail, hours):
        self.aircraft_type = aircraft_type
        self.tail = tail
        self.hours = hours
    
    def info(self):
        return f"{self.aircraft_type} ({self.tail}): {self.hours} hrs"

# Gebruik:
plane1 = Aircraft("Falcon 7X", "N123AB", 5000)
plane2 = Aircraft("Global 6000", "N456CD", 3000)

print(plane1.info())  # "Falcon 7X (N123AB): 5000 hrs"
```

**Wat is `self`?**
- `self` verwijst naar het object zelf
- `self.tail` = de tail van DIT specifieke vliegtuig

#### D. Wat is inheritance (overerving)?

**Simpel gezegd:**
Een class kan eigenschappen "erven" van een andere class.

**Voorbeeld:**
```python
class Animal:  # Parent class
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "Some sound"

class Dog(Animal):  # Child class
    def speak(self):  # Override parent method
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

# Gebruik:
dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # "Woof!"
print(cat.speak())  # "Meow!"
print(dog.name)     # "Buddy" (inherited from Animal)
```

**Waarom is dit nuttig voor PartsCare?**
```python
class BaseAircraftParser:  # Parent
    def parse(self):
        # Algemene logica die ALLE parsers gebruiken
        pass

class JetWorksParser(BaseAircraftParser):  # Child
    def extract_components(self):
        # JetWorks-specific logic
        pass

class DassaultParser(BaseAircraftParser):  # Child
    def extract_components(self):
        # Dassault-specific logic
        pass
```

Alle parsers hebben nu dezelfde `.parse()` methode, maar hun eigen `.extract_components()`.

#### E. Wat zijn abstract classes?

**Simpel gezegd:**
Een template die MOET worden ingevuld.

**Voorbeeld:**
```python
from abc import ABC, abstractmethod

class Shape(ABC):  # Abstract class
    @abstractmethod
    def area(self):
        """Subclass MOET dit implementeren"""
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):  # Verplicht!
        return 3.14 * self.radius ** 2

class Square(Shape):
    def __init__(self, side):
        self.side = side
    
    def area(self):  # Verplicht!
        return self.side ** 2

# Dit werkt:
circle = Circle(5)
print(circle.area())  # 78.5

# Dit werkt NIET:
# shape = Shape()  # Error: Can't instantiate abstract class
```

**Waarom is dit nuttig?**
- Je dwingt af dat elke parser een `extract_components()` methode heeft
- Consistency: alle parsers werken hetzelfde
- Minder bugs: vergeten functies = compile error

---

### 5.2 Belangrijke concepten

#### A. Error handling (try/except)

**Waarom?**
Code kan falen om duizend redenen:
- File bestaat niet
- PDF is corrupt
- Geen internet
- etc.

**Zonder error handling:**
```python
file = open("data.txt")  # Crash als file niet bestaat!
```

**Met error handling:**
```python
try:
    file = open("data.txt")
    content = file.read()
except FileNotFoundError:
    print("File niet gevonden!")
    content = ""
except Exception as e:
    print(f"Onverwachte fout: {e}")
    content = ""
finally:
    file.close()  # Gebeurt altijd, zelfs bij error
```

**Best practices:**
1. **Specifieke errors eerst:**
```python
try:
    ...
except FileNotFoundError:  # Specifiek
    ...
except PermissionError:    # Specifiek
    ...
except Exception as e:     # Generiek (catch-all)
    ...
```

2. **Log de error:**
```python
except Exception as e:
    logger.exception("Fout bij PDF parsing:")  # Logt ook stack trace
```

3. **Re-raise als je het niet kunt fixen:**
```python
try:
    critical_operation()
except CriticalError as e:
    logger.error("Kritieke fout!")
    raise  # Gooi de error verder omhoog
```

#### B. Logging vs Print

**Print:**
```python
print("PDF gelezen")  # Gaat naar console
```

**Probleem:**
- Geen timestamp
- Geen log-level (is dit info? error?)
- Verdwijnt als je de terminal sluit
- Geen file output

**Logging:**
```python
logger.info("PDF gelezen")
# Output: 2024-12-22 14:30:15 | parsers.jetworks | INFO | PDF gelezen
```

**Voordelen:**
- Timestamp automatisch
- Log-levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Gaat naar file én console
- Configureerbaar per module

**Log-levels:**
```python
logger.debug("Detailed info voor debugging")     # Alleen in logfile
logger.info("Normale info over wat er gebeurt")  # Console + file
logger.warning("Iets is raar maar niet fataal")  # Console + file
logger.error("Er is iets fout gegaan")           # Console + file
logger.critical("Alles is kapot, stop!")         # Console + file
```

**Wanneer gebruik je wat?**
- DEBUG: Variabele waardes, loop iterations
- INFO: "PDF gelezen", "Analyse gestart"
- WARNING: "Geen date gevonden, skip deze rij"
- ERROR: "Kan PDF niet openen"
- CRITICAL: "Database is corrupt, kan niet verder"

#### C. Context Managers (with statement)

**Zonder context manager:**
```python
file = open("data.txt")
content = file.read()
file.close()  # Je MOET dit doen, anders blijft file open
```

**Probleem:**
Als er een error is tussen `open()` en `close()`, blijft de file open!

**Met context manager:**
```python
with open("data.txt") as file:
    content = file.read()
# File wordt automatisch gesloten, zelfs bij error!
```

**Voor databases:**
```python
with fitz.open(pdf_path) as doc:
    for page in doc:
        text = page.get_text()
# Document wordt automatisch gesloten
```

**Eigen context manager maken:**
```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    print(f"Start {name}")
    yield  # Hier gebeurt de code
    end = time.time()
    print(f"Klaar {name}: {end-start:.2f}s")

# Gebruik:
with timer("PDF parsing"):
    parse_pdf(path)
# Output:
# Start PDF parsing
# Klaar PDF parsing: 3.45s
```

---

## 🧪 DEEL 6: TESTING STRATEGIE

### 6.1 Waarom testen?

**Scenario zonder tests:**
```
Je past iets aan in JetWorks parser
↓
Je test handmatig met 1 PDF
↓
Lijkt te werken!
↓
Gebruiker probeert andere PDF
↓
CRASH! 💥
```

**Scenario met tests:**
```
Je past iets aan in JetWorks parser
↓
Je draait tests: pytest
↓
50 tests draaien automatisch
↓
1 test faalt: "test_extract_date_format_2"
↓
Je ziet meteen wat er fout is
↓
Je fixt het
↓
Alle tests groen ✅
↓
Deploy met vertrouwen
```

### 6.2 Soorten tests

#### A. Unit tests

**Wat:** Test één functie in isolatie.

**Voorbeeld:**
```python
# src/processors/data_cleaner.py
def parse_hours(hours_str: str) -> float:
    """Parse hours string naar float"""
    # ... implementation ...

# tests/test_data_cleaner.py
import pytest
from src.processors.data_cleaner import parse_hours

def test_parse_hours_colon_format():
    assert parse_hours("123:45") == 123.75

def test_parse_hours_decimal_format():
    assert parse_hours("1234.56") == 1234.56

def test_parse_hours_comma_format():
    assert parse_hours("1,234.56") == 1234.56

def test_parse_hours_invalid_input():
    assert parse_hours("invalid") == 0.0

def test_parse_hours_empty_string():
    assert parse_hours("") == 0.0

def test_parse_hours_none():
    assert parse_hours(None) == 0.0
```

**Run:**
```bash
pytest tests/test_data_cleaner.py -v

# Output:
# test_parse_hours_colon_format PASSED
# test_parse_hours_decimal_format PASSED
# test_parse_hours_comma_format PASSED
# test_parse_hours_invalid_input PASSED
# test_parse_hours_empty_string PASSED
# test_parse_hours_none PASSED
```

#### B. Integration tests

**Wat:** Test meerdere componenten samen.

**Voorbeeld:**
```python
# tests/test_jetworks_parser.py
from src.parsers.aircraft.jetworks import JetWorksParser

def test_full_parsing_workflow():
    """Test hele parsing pipeline"""
    parser = JetWorksParser("tests/fixtures/sample_jetworks.pdf")
    
    df = parser.parse()
    
    # Assertions
    assert not df.empty
    assert len(df) > 0
    assert 'ATA' in df.columns
    assert 'PN' in df.columns
    
    # Check specifieke data
    first_row = df.iloc[0]
    assert first_row['ATA'] == '23'
    assert first_row['PN'] == 'ABC123'
```

#### C. Fixtures (test data)

**Wat:** Herbruikbare test data.

**Voorbeeld:**
```python
# tests/conftest.py
import pytest
import pandas as pd

@pytest.fixture
def sample_component_data():
    """Sample component data voor tests"""
    return pd.DataFrame([
        {
            'ATA': '23',
            'PN': 'ABC123',
            'DESC': 'GPS SENSOR',
            'HRS': '1234.5',
            'DATE': '15-Jan-2024'
        },
        {
            'ATA': '34',
            'PN': 'XYZ789',
            'DESC': 'FUEL PUMP',
            'HRS': '2345.6',
            'DATE': '20-Feb-2024'
        }
    ])

# Gebruik in test:
def test_data_cleaning(sample_component_data):
    cleaned = clean_dataframe(sample_component_data)
    
    assert cleaned['HRS'].dtype == float
    assert cleaned['DATE'].str.match(r'\d{2}-[A-Z][a-z]{2}-\d{4}').all()
```

### 6.3 Test-driven development (TDD)

**Principe:** Schrijf de test VOOR je de code schrijft.

**Workflow:**
1. **Red**: Schrijf een test die faalt
2. **Green**: Schrijf minimale code om test te laten slagen
3. **Refactor**: Verbeter de code, tests blijven groen

**Voorbeeld:**
```python
# Stap 1: Schrijf test (faalt want functie bestaat niet)
def test_extract_part_number():
    text = "Part Number: ABC-123-XYZ"
    pn = extract_part_number(text)
    assert pn == "ABC-123-XYZ"

# Stap 2: Schrijf simpelste implementatie
def extract_part_number(text):
    return "ABC-123-XYZ"  # Hardcoded!

# Test slaagt ✅

# Stap 3: Schrijf meer tests
def test_extract_part_number_different_format():
    text = "PN: DEF-456"
    assert extract_part_number(text) == "DEF-456"

# Test faalt ❌

# Stap 4: Verbeter implementatie
def extract_part_number(text):
    import re
    m = re.search(r'(?:Part Number|PN):\s*([A-Z0-9\-]+)', text)
    return m.group(1) if m else ""

# Alle tests slagen ✅
```

---

## 📅 DEEL 7: IMPLEMENTATIE TIMELINE

### Week 1: Setup & Fundament
- ✅ Virtual environment
- ✅ Git repository + branching strategy
- ✅ Logging implementeren
- ✅ Config files maken
- ✅ .gitignore updaten
- ✅ README updaten

**Deliverable:** Schone basis om op verder te bouwen

### Week 2: Core refactoring
- ✅ BaseAircraftParser implementeren
- ✅ JetWorks parser migreren
- ✅ Data cleaner module
- ✅ Excel exporter verbeteren
- ✅ Error handling overal toevoegen

**Deliverable:** Modulaire, schaalbare code

### Week 3: Testing
- ✅ pytest setup
- ✅ Unit tests voor alle processors
- ✅ Integration tests voor parsers
- ✅ Test fixtures maken
- ✅ CI/CD setup (optioneel: GitHub Actions)

**Deliverable:** 80%+ test coverage

### Week 4: Remaining parsers
- ✅ Dassault parser compleet maken
- ✅ Bombardier parser compleet maken
- ✅ Gulfstream parser compleet maken
- ✅ Parser auto-detection (welk type is dit PDF?)

**Deliverable:** Alle vliegtuigtypes ondersteund

### Week 5: Advanced features
- ✅ Duplicate detection
- ✅ Data validation
- ✅ Excel advanced formatting
- ✅ Export templates
- ✅ Batch processing optimalisatie

**Deliverable:** Production-ready tool

### Week 6: Documentatie & deployment
- ✅ User guide schrijven
- ✅ Developer guide schrijven
- ✅ API reference
- ✅ PyInstaller build testen
- ✅ Deployment scripts

**Deliverable:** Klaar voor productie

### Week 7-8: AI Voorbereiding (optioneel)
- ✅ Document indexer bouwen
- ✅ Vector database opzetten
- ✅ Sample queries testen
- ✅ RAG pipeline prototype

**Deliverable:** AI foundation

---

## 🎯 DEEL 8: PRIORITEITEN & QUICK WINS

### High Priority (nu doen)

1. **✅ Logging implementeren** (3 uur)
   - Makkelijk, grote impact
   - Je kunt nu debuggen zonder user erbij

2. **✅ Config centraliseren** (4 uur)
   - Maakt aanpassingen veel simpeler
   - Goede voorbereiding voor testen

3. **✅ Error handling verbeteren** (3 uur)
   - Voorkomt crashes
   - Betere user experience

### Medium Priority (volgende sprint)

4. **✅ BaseAircraftParser** (1 dag)
   - Maakt nieuwe parsers simpeler
   - Consistency

5. **✅ Excel exporter upgrade** (4 uur)
   - Professionelere outputs
   - Herbruikbaar

6. **✅ Tests schrijven** (2 dagen)
   - Confidence bij refactoring
   - Voorkom regressies

### Low Priority (later)

7. **✅ Remaining parsers** (per parser 1 dag)
   - Niet kritiek als JetWorks werkt
   - Kunnen incrementeel

8. **✅ AI/RAG** (1-2 maanden)
   - Grote investering
   - Vereist solide basis eerst

---

## 🚨 DEEL 9: VEELVOORKOMENDE VALKUILEN

### Valkuil 1: Te veel tegelijk willen

**❌ Fout:**
"Ik ga alles refactoren + tests schrijven + AI toevoegen in 1 week!"

**✅ Goed:**
"Deze week: logging + config. Volgende week: base parser. Week daarna: tests."

**Tip:** Kleine stappen, frequent committen.

### Valkuil 2: Geen backups

**❌ Fout:**
Beginnen met refactoring zonder Git commit.

**✅ Goed:**
```bash
git add .
git commit -m "Working state before refactoring"
git branch refactor/logging
git checkout refactor/logging
# Nu kan je veilig experimenteren
```

### Valkuil 3: Testing overslaan

**❌ Fout:**
"Tests schrijven we later wel."

**✅ Goed:**
"Elke nieuwe functie krijgt meteen een test."

**Waarom:** Later = nooit. En zonder tests durf je niets te refactoren.

### Valkuil 4: Onduidelijke variabele namen

**❌ Fout:**
```python
def f(x, y):
    return x + y

a = f(b, c)
```

**✅ Goed:**
```python
def calculate_total_hours(flight_hours, ground_hours):
    return flight_hours + ground_hours

total_hours = calculate_total_hours(flight_hours, ground_hours)
```

### Valkuil 5: God objects / God functions

**❌ Fout:**
```python
def do_everything(pdf_path):
    # 500 regels code die alles doet
    ...
```

**✅ Goed:**
```python
def parse_pdf(pdf_path):
    doc = open_pdf(pdf_path)
    text = extract_text(doc)
    components = parse_components(text)
    df = clean_data(components)
    return df
```

Elke functie doet ÉÉN ding.

---

## 📖 DEEL 10: LEERRESOURCES

### Python fundamentals
- **Official Python Tutorial**: https://docs.python.org/3/tutorial/
- **Real Python**: https://realpython.com (gratis tutorials)
- **Python for Everybody**: https://www.py4e.com (gratis cursus)

### Testing
- **Pytest Documentation**: https://docs.pytest.org
- **Test-Driven Development with Python**: (boek)

### Software Architecture
- **Clean Code** (boek van Robert C. Martin)
- **Python Design Patterns**: https://refactoring.guru/design-patterns/python

### Luchtvaart specifiek
- **ATA Chapters**: Basis kennis over systemen
- **IPC/AMM structuur**: Hoe zijn deze docs opgebouwd?

---

## ✅ DEEL 11: CHECKLIST

### Voor je begint met refactoring:

- [ ] Backup van huidige werkende code (Git commit)
- [ ] Virtual environment aangemaakt
- [ ] Requirements.txt up-to-date
- [ ] .gitignore geconfigureerd (data/, logs/, __pycache__)
- [ ] Branch gemaakt voor refactoring

### Na elke refactoring-stap:

- [ ] Code werkt (manual test)
- [ ] Tests geschreven
- [ ] Tests draaien groen
- [ ] Code committed met duidelijke message
- [ ] Documentatie geüpdatet

### Voor productie:

- [ ] Alle tests groen
- [ ] Error handling overal
- [ ] Logging geïmplementeerd
- [ ] Config extern (niet hardcoded)
- [ ] User guide geschreven
- [ ] PyInstaller build getest

---

## 🎓 CONCLUSIE

Je hebt nu:

1. ✅ **Volledige audit** van huidige code
2. ✅ **Architectuur-voorstel** voor schaalbaar systeem
3. ✅ **Stap-voor-stap plan** om erheen te werken
4. ✅ **Educatieve uitleg** van alle concepten
5. ✅ **Roadmap naar AI** (RAG)
6. ✅ **Best practices** en valkuilen

### Volgende stappen:

1. **Lees dit document grondig**
2. **Stel vragen** waar dingen onduidelijk zijn
3. **Start met Week 1** (Setup & Fundament)
4. **Commit frequent** (kleine stappen)
5. **Test alles** wat je maakt

### Als je vast komt te zitten:

1. Check de logs (als je logging hebt geïmplementeerd)
2. Schrijf een simpele test die het probleem demonstreert
3. Debug stap-voor-stap (print statements / breakpoints)
4. Vraag om hulp met specifieke error messages

---

**Succes met het project! 🚀**

Dit is een solide basis geworden. Nu is het aan jou om het stap-voor-stap te implementeren. Begin klein, test vaak, en bouw gestaag verder.

Remember: **Rome werd ook niet in 1 dag gebouwd.** Een goed gestructureerd project is de moeite waard, ook al kost het tijd.
