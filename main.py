import threading
import tkinter as tk
from pathlib import Path
import subprocess
import sys
import initialisation_stepper
from Gui_style import (
    PRIMARY_RED,
    BACKGROUND,
    TEXT_COLOR,
    BUTTON_BG,
    BUTTON_FG,
    BUTTON_ACTIVE_BG,
    BUTTON_ACTIVE_FG,
    STATUS_FONT,
    BUTTON_FONT,
    BUTTON_RADIUS
)

# Pfad zu diesem Script
SCRIPT_DIR = Path(__file__).resolve().parent
# Pad zu den Rezepten
RECIPES_DIR = SCRIPT_DIR / "Rezepte"

# Homing des Steppers ausführen, bevor GUI startet
# try:
#     initialisation_stepper.home_stepper()
# except Exception as exc:
#     print(f"Homing fehlgeschlagen: {exc}")
#     sys.exit(1)

current_thread = None  # merkt laufendes Rezept oder Homing

def set_buttons_state(state: str):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state=state)

def do_homing_and_ready():
    """Homing ausführen und Buttons danach freigeben."""
    global current_thread
    status_label.config(text="Homing... bitte warten")
    try:
        initialisation_stepper.home_stepper()
    except Exception as exc:
        status_label.config(text=f"Homing fehlgeschlagen: {exc}")
        current_thread = None
        return
    status_label.config(text="Bereit. Bitte Rezept wählen.")
    set_buttons_state("normal")
    current_thread = None

def on_recipe_done(name: str):
    """Nach Rezeptende Homing starten (Blockade bleibt, bis Homing fertig)."""
    global current_thread
    status_label.config(text=f"{name} fertig. Homing wird ausgeführt...")
    # Homing im gleichen Thread ausführen, dann in GUI freigeben
    do_homing_and_ready()

# --- Funktion zum Starten des Rezeptprogramms ---
def start_recipe(file_path: Path):
    global current_thread
    if current_thread is not None:
        return  # schon ein Rezept/Homing aktiv

    name = file_path.stem.replace("Rezept_", "")

    # Text anzeigen
    status_label.config(text=f"{name} wird zubereitet...")
    set_buttons_state("disabled")

    print(f"Starte: {file_path}")

    # Rezeptprogramm vorbereiten
    if file_path.suffix == ".py":
        cmd = ["python3", str(file_path)]
    elif file_path.suffix == ".sh":
        cmd = ["bash", str(file_path)]
    else:
        cmd = ["xdg-open", str(file_path)]

    def runner():
        try:
            subprocess.run(cmd, check=False)
        finally:
            root.after(0, on_recipe_done, name)

    current_thread = threading.Thread(target=runner, daemon=True)
    current_thread.start()

root = tk.Tk()
root.title("Hello World")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
root.configure(bg=BACKGROUND)

frame = tk.Frame(root, bg=BACKGROUND)
frame.pack(expand=True, fill="both", padx=40, pady=40)

status_label = tk.Label(
    root,
    text="",
    font=STATUS_FONT,
    fg=TEXT_COLOR,
    bg=BACKGROUND
)
status_label.pack(pady=20)

if RECIPES_DIR.exists() and RECIPES_DIR.is_dir():
    files = sorted(f for f in RECIPES_DIR.iterdir() if f.is_file())
else:
    files = []

if not files:
    label = tk.Label(frame, text="Keine Rezeptdateien gefunden.", font=("Arial", 32))
    label.pack()
else:
    # Grid so einstellen, dass sich die Buttons schön verteilen
    columns = 3  # Anzahl Spalten anpassen, wenn du willst
    for i, file_path in enumerate(files):
        name = file_path.stem.replace("Rezept_", "")  # Dateiname ohne .txt / .py / etc.
        row = i // columns
        col = i % columns

        btn = tk.Button(
            frame,
            text=name,
            font=BUTTON_FONT,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=BUTTON_ACTIVE_FG,
            relief="solid",
            bd=2,
            highlightthickness=0,
            width=20,       # gleiche Breite für ALLE
            height=5,
            command=lambda p=file_path: start_recipe(p)
        )
        btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    # Spalten/Zeilen dehnbar machen
    max_rows = (len(files) - 1) // columns + 1
    for c in range(columns):
        frame.grid_columnconfigure(c, weight=1)
    for r in range(max_rows):
        frame.grid_rowconfigure(r, weight=1)

root.mainloop()