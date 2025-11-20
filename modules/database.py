import json
import os
import sys

# =====================================================
#   PAD-OPLOSSING (werkt ook in .exe via PyInstaller)
# =====================================================
def resource_path(relative_path):
    """
    Geeft het juiste pad terug, ook als de app is gebundeld met PyInstaller (.exe).
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Pad naar database (werkt in .exe én tijdens ontwikkeling)
DB_PATH = resource_path("data/database.json")

# =====================================================
#   DATABASE INITIALISATIE
# =====================================================
def init_database():
    """Controleer of database bestaat, anders maak een nieuwe aan."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        data = {
            "users": [
                {"username": "ADA", "password": "Adam2024$"}
            ],
            "analyses": []
        }
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)
        print("[OK] Nieuwe database aangemaakt.")
    else:
        print("[OK] Database gevonden.")

# =====================================================
#   DATABASE LEZEN / SCHRIJVEN
# =====================================================
def load_database():
    """Laad data uit JSON-bestand."""
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_database(data):
    """Sla data op in JSON-bestand."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# =====================================================
#   LOGIN VALIDATIE
# =====================================================
def validate_login(username, password):
    """Controleer of de gebruikerscode en het wachtwoord kloppen."""
    data = load_database()
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return True
    return False
