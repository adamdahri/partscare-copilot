# ============================================
#   PARTSCARE COPILOT v1.0
#   Auteur: Adam & GPT-5 Copilot
#   Functie: Login + Menustructuur (professionele console)
# ============================================

import os
import datetime
from colorama import Fore, Style, init
from modules.parts_analyse import run_parts_analyse
from modules.fleet_analyse import run_fleet_analyse
from modules.full_parts_analyse import run_full_parts_analyse
from modules.database import init_database, validate_login

# Colorama activeren
init(autoreset=True)

# ============================================
#   HULPFUNCTIES
# ============================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(Fore.CYAN + Style.BRIGHT + f"\n=== {title} ===")
    print(Fore.LIGHTBLACK_EX + f"Datum & tijd: {now}")
    print(Style.RESET_ALL)

def print_logo():
    clear_screen()
    print(Fore.BLUE + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
          PARTSCARE COPILOT – v1.0
      Intelligent Aircraft Data Assistant
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)

# ============================================
#   LOGIN SCHERM
# ============================================

def login_screen():
    print_logo()
    print(Fore.CYAN + "🔐 LOGIN VEREIST\n" + Style.RESET_ALL)

    username = input(Fore.YELLOW + "Gebruikerscode: " + Style.RESET_ALL).upper()
    password = input(Fore.YELLOW + "Wachtwoord: " + Style.RESET_ALL)

    if validate_login(username, password):
        print(Fore.GREEN + f"[✔] Ingelogd als {username}\n" + Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + "[✖] Onjuiste login of wachtwoord.\n" + Style.RESET_ALL)
        return False

# ============================================
#   ANALYSE MENU
# ============================================

def analyses_menu():
    while True:
        print_header("ANALYSES MENU")
        print(Fore.WHITE + "1. Parts Analyse")
        print("2. Fleet Analyse")
        print("3. Full Parts Analyse")
        print("4. Terug naar hoofdmenu" + Style.RESET_ALL)

        choice = input(Fore.YELLOW + "Maak uw keuze: " + Style.RESET_ALL)

        if choice == "1":
            run_parts_analyse()
        elif choice == "2":
            run_fleet_analyse()
        elif choice == "3":
            run_full_parts_analyse()
        elif choice == "4":
            break
        else:
            print(Fore.RED + "⚠ Ongeldige keuze, probeer opnieuw.\n")

# ============================================
#   MAINTENANCE MENU
# ============================================

def maintenance_menu():
    while True:
        print_header("MAINTENANCE MENU")
        print("1. (Nog te ontwikkelen)")
        print("2. Terug naar hoofdmenu")

        choice = input(Fore.YELLOW + "Maak uw keuze: " + Style.RESET_ALL)

        if choice == "2":
            break
        else:
            print(Fore.LIGHTBLUE_EX + "🛠️ Deze functie komt binnenkort beschikbaar.\n")

# ============================================
#   HOOFDMENU
# ============================================

def main_menu():
    while True:
        print_header("PARTSCARE PLATFORM")
        print("1. Analyses")
        print("2. Maintenance")
        print("3. Exit")

        choice = input(Fore.YELLOW + "Maak uw keuze: " + Style.RESET_ALL)

        if choice == "1":
            analyses_menu()
        elif choice == "2":
            maintenance_menu()
        elif choice == "3":
            print(Fore.MAGENTA + "🔒 Programma afgesloten. Tot ziens!\n")
            break
        else:
            print(Fore.RED + "⚠ Ongeldige keuze, probeer opnieuw.\n")

# ============================================
#   STARTPUNT
# ============================================

if __name__ == "__main__":
    print_logo()
    init_database()

    # Login vereist
    logged_in = False
    pogingen = 0

    while not logged_in and pogingen < 3:
        logged_in = login_screen()
        if not logged_in:
            pogingen += 1
            if pogingen < 3:
                print(Fore.YELLOW + f"⏳ Poging {pogingen}/3 mislukt. Probeer opnieuw.\n")
            else:
                print(Fore.RED + "❌ Te veel mislukte pogingen. Programma afgesloten.\n")
                exit()

    if logged_in:
        main_menu()
