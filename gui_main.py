# ==============================================================
# PARTSCARE COPILOT v4.0 (macOS Stable Edition - Button Fix)
# Intelligent Aircraft Data Assistant
# Author: ADA
# ==============================================================

import sys, os, importlib, subprocess, threading, traceback, time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage
from pathlib import Path

# ==============================================================
# SAFE MAIN THREAD EXECUTION (macOS FIX)
# ==============================================================
def run_on_main_thread(func):
    """Run Tkinter operations safely on macOS main thread."""
    if threading.current_thread() is threading.main_thread():
        func()
    else:
        import queue
        q = queue.Queue()
        def wrapper():
            try:
                func()
            finally:
                q.put(None)
        root = tk.Tk()
        root.withdraw()
        root.after(0, wrapper)
        root.mainloop()
        q.get()

# ==============================================================
# SPLASHSCREEN (thread-safe)
# ==============================================================
def show_splash():
    def inner():
        splash = tk.Tk()
        splash.overrideredirect(True)
        splash.geometry("420x260+550+350")
        splash.configure(bg="#0C1A34")

        tk.Label(
            splash, text="✈️ PARTSCARE COPILOT",
            fg="white", bg="#0C1A34",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(70, 10))
        ttk.Label(
            splash, text="Starting Intelligent Assistant...",
            background="#0C1A34", foreground="#B7C9FF"
        ).pack()
        bar = ttk.Progressbar(splash, mode="indeterminate")
        bar.pack(fill="x", padx=60, pady=20)
        bar.start(12)

        splash.after(1800, splash.destroy)
        splash.mainloop()

    run_on_main_thread(inner)

# ==============================================================
# AUTO-INSTALLER (with thread-safe close)
# ==============================================================
def ensure_modules():
    required = [
        "pandas", "numpy", "openpyxl", "PyMuPDF", "pillow", "matplotlib"
    ]
    missing = []
    for m in required:
        try:
            importlib.import_module(m)
        except ImportError:
            missing.append(m)

    if missing:
        def installer():
            root = tk.Tk()
            root.title("Installatie van modules…")
            root.geometry("420x150")
            root.configure(bg="#101828")
            root.resizable(False, False)

            ttk.Label(root, text="Modules worden automatisch geïnstalleerd…",
                      background="#101828", foreground="#E0E6F0",
                      font=("Segoe UI", 10)).pack(pady=(25, 10))
            bar = ttk.Progressbar(root, mode="indeterminate")
            bar.pack(fill="x", padx=40)
            bar.start(10)
            lbl = ttk.Label(root, text="", background="#101828", foreground="#9AA5B1")
            lbl.pack(pady=(5, 5))

            def install_all():
                for module in missing:
                    lbl.config(text=f"📦 Installeert: {module}")
                    root.update()
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                    except Exception as e:
                        messagebox.showerror("Installatiefout", f"Kon {module} niet installeren:\n{e}")
                bar.stop()
                root.after(0, root.destroy)

            threading.Thread(target=install_all, daemon=True).start()
            root.mainloop()

        run_on_main_thread(installer)

# ==============================================================
# STARTUP SEQUENCE
# ==============================================================
show_splash()
ensure_modules()

# ==============================================================
# IMPORTS NA INSTALLATIE
# ==============================================================
from modules.parts68 import run_batch as run_parts68_batch
from modules.fleet_analyse import write_fleet_sheet
from modules.database import validate_login, init_database

# ==============================================================
# INITIALISATIE DATABASE
# ==============================================================
init_database()

# ==============================================================
# INTERFACE CONSTANTEN
# ==============================================================
BG_GRADIENT = ("#0A1428", "#132B54")
PRIMARY_COLOR = "#004A99"
TEXT_COLOR = "#E8F0FE"

# ==============================================================
# GRADIENT FUNCTIE
# ==============================================================
def create_gradient(canvas, width, height, color1, color2):
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    for i in range(height):
        ratio = i / height
        nr = int(r1 + (r2 - r1) * ratio)
        ng = int(g1 + (g2 - g1) * ratio)
        nb = int(b1 + (b2 - b1) * ratio)
        color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
        canvas.create_line(0, i, width, i, fill=color)

# ==============================================================
# LOGINVENSTER
# ==============================================================
def show_login_window():
    def inner():
        root = tk.Tk()
        root.title("PartsCare Copilot - Login")
        root.geometry("520x400")
        root.resizable(False, False)

        canvas = tk.Canvas(root, width=520, height=400, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        create_gradient(canvas, 520, 400, BG_GRADIENT[0], BG_GRADIENT[1])

        logo_path = "data/partscare_logo.png"
        if os.path.exists(logo_path):
            logo_img = PhotoImage(file=logo_path)
            canvas.create_image(260, 80, image=logo_img)
            canvas.logo_img = logo_img
        else:
            canvas.create_text(260, 80, text="✈️ PARTSCARE COPILOT", fill=TEXT_COLOR,
                               font=("Segoe UI", 18, "bold"))

        canvas.create_text(260, 110, text="Intelligent Aircraft Data Assistant",
                           fill="#AFCBFF", font=("Segoe UI", 10, "italic"))

        frame = tk.Frame(root, bg="#162A4A")
        frame.place(relx=0.5, rely=0.57, anchor="center")

        def field(label, row, show=None):
            tk.Label(frame, text=label, bg="#162A4A", fg=TEXT_COLOR,
                     font=("Segoe UI", 10)).grid(row=row, column=0, pady=(8, 4))
            e = tk.Entry(frame, show=show, font=("Segoe UI", 11),
                         width=26, relief="flat", justify="center")
            e.grid(row=row+1, column=0, padx=10, pady=5)
            return e

        username = field("Gebruikerscode", 0)
        password = field("Wachtwoord", 2, show="*")

        def login():
            u = username.get().strip().upper()
            p = password.get().strip()
            if validate_login(u, p):
                messagebox.showinfo("Welkom", f"Welkom terug, {u}!")
                root.destroy()
                show_dashboard(u)
            else:
                messagebox.showerror("Fout", "Ongeldige gebruikerscode of wachtwoord.")

        login_btn = tk.Button(
            root, text="Inloggen", command=login,
            bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 11, "bold"),
            activebackground="#0066CC", activeforeground="white",
            relief="raised", bd=3, highlightthickness=0,
            width=15, cursor="hand2"
        )
        login_btn.place(relx=0.5, rely=0.8, anchor="center")

        canvas.create_text(260, 380, text="© PartsCare Copilot v4.0 | Developed by ADA",
                           fill="#8FB4FF", font=("Segoe UI", 8))

        root.mainloop()

    run_on_main_thread(inner)

# ==============================================================
# PROGRESSVENSTER
# ==============================================================
class ProgressWindow:
    def __init__(self, parent, text):
        self.top = tk.Toplevel(parent)
        self.top.title("Bezig…")
        self.top.geometry("380x120")
        self.top.configure(bg="#0E1F3A")
        self.top.transient(parent)
        self.top.grab_set()
        ttk.Label(self.top, text=text, font=("Segoe UI", 10)).pack(pady=(20, 10))
        self.bar = ttk.Progressbar(self.top, mode="indeterminate")
        self.bar.pack(fill="x", padx=25, pady=(0, 12))
        self.bar.start(10)
    def close(self):
        self.bar.stop()
        self.top.after(0, self.top.destroy)

# ==============================================================
# DASHBOARD
# ==============================================================
def show_dashboard(username):
    app = tk.Tk()
    app.title("PartsCare Copilot - Dashboard")
    app.geometry("960x620")
    app.configure(bg="#0B152B")
    app.resizable(False, False)

    logo_path = "data/partscare_logo.png"
    if os.path.exists(logo_path):
        logo_img = PhotoImage(file=logo_path)
        tk.Label(app, image=logo_img, bg="#0B152B").pack(pady=(25, 10))
        app.logo_img = logo_img
    else:
        tk.Label(app, text="✈️ PARTSCARE COPILOT",
                 bg="#0B152B", fg="white", font=("Segoe UI", 22, "bold")).pack()

    tk.Label(app, text="Intelligent Aircraft Data Assistant",
             bg="#0B152B", fg="#AFCBFF", font=("Segoe UI", 11, "italic")).pack()
    tk.Label(app, text=f"Welkom, {username} 👋",
             bg="#0B152B", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=(10, 20))

    output = tk.Text(app, width=110, height=13, bg="#101F3D", fg="#EAF2FF", font=("Consolas", 9))
    output.pack(padx=25, pady=(10, 20))
    output.insert("end", "🔹 PartsCare Copilot v4.0 is klaar voor gebruik.\n")
    output.configure(state="disabled")

    def log(msg):
        output.configure(state="normal")
        output.insert("end", msg + "\n")
        output.configure(state="disabled")
        output.see("end")

    def run_fleet():
        path = filedialog.askopenfilename(title="Selecteer Excelbestand", filetypes=[("Excel-bestanden", "*.xlsx *.xls")])
        if not path: return
        progress = ProgressWindow(app, "FleetAnalyse uitvoeren…")

        def work():
            try:
                result = write_fleet_sheet(Path(path))
                app.after(0, lambda: (
                    progress.close(),
                    messagebox.showinfo("Klaar", f"✅ FleetAnalyse voltooid:\n{result}"),
                    log(f"✅ FleetAnalyse voltooid: {result}")
                ))
            except Exception as e:
                app.after(0, lambda: (
                    progress.close(),
                    messagebox.showerror("Fout", str(e)),
                    log(traceback.format_exc())
                ))

        threading.Thread(target=work, daemon=True).start()

    def run_parts():
        in_dir = filedialog.askdirectory(title="Kies inputmap (PDF's)")
        if not in_dir: return
        out_dir = filedialog.askdirectory(title="Kies outputmap (Excel-bestanden)")
        if not out_dir: return
        progress = ProgressWindow(app, "Parts Analyse v6.8 uitvoeren…")

        def work():
            try:
                stats = run_parts68_batch(in_dir, out_dir, log=log)
                app.after(0, lambda: (
                    progress.close(),
                    messagebox.showinfo("Klaar", f"✅ PartsAnalyse voltooid\nVerwerkt: {stats['processed']} |  Geëxporteerd: {stats['exported']}"),
                    log("✅ PartsAnalyse succesvol voltooid.")
                ))
            except Exception as e:
                app.after(0, lambda: (
                    progress.close(),
                    messagebox.showerror("Fout", str(e)),
                    log(traceback.format_exc())
                ))

        threading.Thread(target=work, daemon=True).start()

    # ---- Buttons (visible fix macOS) ----
    def button(text, cmd, color):
        return tk.Button(
            app,
            text=text,
            command=cmd,
            bg=color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="raised",
            bd=3,
            highlightthickness=0,
            activebackground="#0066CC",
            activeforeground="white",
            width=26,
            height=2,
            cursor="hand2"
        )

    button(" Fleet Analyse uitvoeren", run_fleet, "#004A99").pack(pady=5)
    button(" Parts Analyse v6.8 (PDF → Excel)", run_parts, "#007040").pack(pady=5)
    button(" Afsluiten", app.destroy, "#A80000").pack(pady=15)

    tk.Label(app, text="© PartsCare Copilot v4.0 | Developed by ADA",
             bg="#0B152B", fg="#7FAAFF", font=("Segoe UI", 9)).pack(side="bottom", pady=10)

    app.mainloop()

# ==============================================================
# START APP
# ==============================================================
if __name__ == "__main__":
    show_login_window()
