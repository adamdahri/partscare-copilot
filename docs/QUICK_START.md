# 🚀 QUICK START GUIDE - EERSTE STAPPEN

Dit document helpt je om **vandaag nog** te beginnen met de refactoring.

---

## STAP 1: Backup maken (5 minuten)

### A. Check of Git geïnitialiseerd is
```bash
cd partscare-copilot
git status
```

**Als je een error krijgt ("not a git repository"):**
```bash
git init
git add .
git commit -m "Initial commit - working state"
```

**Als Git al werkt:**
```bash
git status  # Bekijk wat er uncommitted is
git add .
git commit -m "Backup before refactoring - $(date +%Y-%m-%d)"
```

### B. Maak een nieuwe branch
```bash
git checkout -b refactor/week1
```

Nu werk je in een aparte branch. Als iets fout gaat, kan je terug:
```bash
git checkout main  # Terug naar originele code
```

---

## STAP 2: Virtual Environment (10 minuten)

### Windows:
```bash
# Maak venv
python -m venv venv

# Activeer
venv\Scripts\activate

# Je ziet nu (venv) voor je prompt
```

### macOS/Linux:
```bash
# Maak venv
python3 -m venv venv

# Activeer
source venv/bin/activate

# Je ziet nu (venv) voor je prompt
```

### Installeer dependencies
```bash
pip install -r requirements.txt
```

### Test of het werkt
```bash
python gui_main.py
```

Als de GUI opent → success! ✅

---

## STAP 3: .gitignore maken (5 minuten)

Maak een bestand `.gitignore` in je project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data (belangrijk!)
data/input/
data/output/
data/logs/
*.pdf
*.xlsx
*.xls

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log

# Database (zet wachtwoorden NOOIT in Git!)
data/database.json

# PyInstaller
build/
dist/
*.spec
```

**Commit dit:**
```bash
git add .gitignore
git commit -m "Add .gitignore"
```

---

## STAP 4: Logging implementeren (30 minuten)

### A. Maak de logger utility

**Nieuwe file: `src/utils/logger.py`**

(Zie het volledige audit rapport voor de code)

### B. Test de logger

**Nieuwe file: `test_logger.py`** (tijdelijk, voor testen)
```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

logger.debug("Dit is een debug bericht")
logger.info("Dit is een info bericht")
logger.warning("Dit is een waarschuwing")
logger.error("Dit is een error")

print("\n✅ Check data/logs/ voor het logbestand!")
```

**Run:**
```bash
python test_logger.py
```

**Verwacht resultaat:**
- Console: zie je INFO, WARNING, ERROR (maar geen DEBUG)
- File: `data/logs/partscare_2024-12-22.log` → bevat ALLES inclusief DEBUG

**Als het werkt:**
```bash
rm test_logger.py  # Verwijder test file
git add src/utils/logger.py
git commit -m "Add logging utility"
```

---

## STAP 5: Update één module met logging (30 minuten)

### A. Kies een module om te updaten

Start met `modules/parts68.py` (je belangrijkste module).

### B. Voeg logging toe

**Bovenaan het bestand:**
```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
```

**Vervang alle prints:**
```python
# VOOR:
print(f"[OK] PDF succesvol gelezen: {file_path}")

# NA:
logger.info(f"PDF succesvol gelezen: {file_path}")
```

```python
# VOOR:
print(f"[FOUT] Kon PDF niet lezen: {e}")

# NA:
logger.error(f"Kon PDF niet lezen: {e}", exc_info=True)
```

### C. Test het

```bash
python gui_main.py
```

Upload een PDF, bekijk de logs in `data/logs/`.

**Commit:**
```bash
git add modules/parts68.py
git commit -m "Add logging to parts68 module"
```

---

## STAP 6: Config file maken (30 minuten)

### A. Maak de config directory

```bash
mkdir -p config
touch config/__init__.py
```

### B. Maak settings.py

**File: `config/settings.py`**
```python
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = DATA_DIR / "logs"

# ATA configuration
ATA_RANGE = (21, 79)

# Excel configuration
EXCEL_STYLE = {
    'header_color': '1F4E78',
    'header_font_color': 'FFFFFF',
    'alt_row_color': 'F2F2F2'
}

# Parsing thresholds
MIN_HOURS = 0.0
```

### C. Update parts68.py om config te gebruiken

**Bovenaan:**
```python
from config.settings import ATA_RANGE, MIN_HOURS
```

**In de code:**
```python
# VOOR:
ATA_MIN, ATA_MAX = 21, 79
if not (ata >= ATA_MIN and ata <= ATA_MAX):

# NA:
if not (ATA_RANGE[0] <= ata <= ATA_RANGE[1]):
```

### D. Test

```bash
python gui_main.py
```

Upload een PDF, check of het nog werkt.

**Commit:**
```bash
git add config/
git add modules/parts68.py
git commit -m "Add config system"
```

---

## EINDE VAN DAG 1 🎉

Je hebt nu:
- ✅ Git backup
- ✅ Virtual environment
- ✅ .gitignore
- ✅ Logging system
- ✅ Config system
- ✅ Eerste module geüpdatet

### Volgende keer:
- Meer modules updaten met logging
- Base parser maken
- Tests schrijven

---

## TROUBLESHOOTING

### "Module not found" error

**Probleem:** Python vindt je modules niet.

**Oplossing:** Voeg een `__init__.py` toe in elke map:
```bash
touch src/__init__.py
touch src/utils/__init__.py
touch config/__init__.py
```

### "Permission denied" bij venv activeren (Windows)

**Probleem:** PowerShell execution policy.

**Oplossing:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Git merge conflicts

**Probleem:** Je hebt changes op main EN op je branch.

**Oplossing:**
```bash
git checkout refactor/week1
git merge main  # Merge main into je branch
# Los conflicts op in je editor
git add .
git commit -m "Merge main into refactor/week1"
```

### Imports werken niet

**Probleem:** Relative imports falen.

**Oplossing 1 - Voeg project root toe aan Python path:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Oplossing 2 - Run als module:**
```bash
python -m src.main  # In plaats van python src/main.py
```

---

## HANDIGE COMMANDO'S

### Git
```bash
git status                    # Wat is er veranderd?
git diff                      # Laat changes zien
git add <file>               # Stage een bestand
git add .                     # Stage alles
git commit -m "message"       # Commit met message
git log --oneline             # Bekijk history
git checkout <branch>         # Switch naar branch
git checkout -b <new-branch>  # Maak en switch naar nieuwe branch
```

### Python
```bash
python --version              # Check Python versie
pip list                      # Geïnstalleerde packages
pip freeze > requirements.txt # Update requirements
python -m pytest              # Run tests (later)
python -m pdb script.py       # Run met debugger
```

### Virtual Environment
```bash
# Activeren
venv\Scripts\activate         # Windows
source venv/bin/activate      # Mac/Linux

# Deactiveren
deactivate
```

---

## CHECKLIST VOOR VANDAAG

- [ ] Git backup gemaakt
- [ ] Branch aangemaakt: `refactor/week1`
- [ ] Virtual environment gemaakt en geactiveerd
- [ ] .gitignore aangemaakt
- [ ] Logging utility gemaakt (`src/utils/logger.py`)
- [ ] Logging getest (test_logger.py)
- [ ] Config system gemaakt (`config/settings.py`)
- [ ] Één module geüpdatet met logging
- [ ] Alles gecommit naar Git
- [ ] Code werkt nog (GUI test)

Als je alle checkboxes hebt: **GEFELICITEERD!** 🎉

Je hebt een solide basis voor verdere refactoring.

---

## VOLGENDE SESSIE

Wanneer je verder gaat:

1. Update meer modules met logging
2. Maak `config/regex_patterns.py`
3. Update parsers om config te gebruiken
4. Test alles grondig
5. Commit frequent

**Vergeet niet:**
- Kleine stappen
- Frequent testen
- Frequent committen
- Als iets breekt: `git checkout` terug

Succes! 💪
