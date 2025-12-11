import threading
import os
import tkinter as tk
from pathlib import Path
import subprocess
import initialisation_stepper
from Gui_style import (
    BACKGROUND,
    TEXT_COLOR,
    BUTTON_BG,
    BUTTON_FG,
    BUTTON_ACTIVE_BG,
    BUTTON_ACTIVE_FG,
    STATUS_FONT,
    BUTTON_FONT,
)

SCRIPT_DIR = Path(__file__).resolve().parent
RECIPES_DIR = SCRIPT_DIR / "Rezepte"

current_thread = None
# SKIP_HOMING_AFTER wird entfernt.

def set_buttons_state(state: str):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state=state)

def _finalize_homing(msg: str):
    """Wird nach dem Homing aufgerufen, um den Zustand zu aktualisieren."""
    global current_thread
    status_label.config(text=msg)
    set_buttons_state("normal")
    current_thread = None

def _finalize_recipe(name: str):
    """Wird nach dem Rezept aufgerufen, um den Zustand zu aktualisieren."""
    global current_thread
    # Buttons werden freigegeben, es wird KEIN Homing gestartet
    _finalize_homing(f"{name} fertig. Bereit. Bitte Rezept wählen.")


def run_initial_homing():
    """Führt die Homing-Routine einmalig beim Start aus."""
    global current_thread
    
    set_buttons_state("disabled")
    status_label.config(text="Anwendung gestartet. Homing wird ausgeführt...")

    def homing_runner():
        try:
            # Führt Homing (Button-Druck) und das Fahren zur Warteposition aus
            initialisation_stepper.home_stepper() 
            msg = "Bereit. Bitte Rezept wählen."
        except Exception as exc:
            msg = f"Homing fehlgeschlagen: {exc}"
        finally:
            root.after(0, _finalize_homing, msg)

    current_thread = threading.Thread(target=homing_runner, daemon=True)
    current_thread.start()


def start_recipe(file_path: Path):
    global current_thread
    if current_thread is not None:
        return  # schon ein Rezept/Homing aktiv

    name = file_path.stem.replace("Rezept_", "")
    status_label.config(text=f"{name} wird zubereitet...")
    status_label.update_idletasks()  # sofort anzeigen
    set_buttons_state("disabled")

    if file_path.suffix == ".py":
        cmd = ["python3", str(file_path)]
    elif file_path.suffix == ".sh":
        cmd = ["bash", str(file_path)]
    else:
        cmd = ["xdg-open", str(file_path)]

    def runner():
        try:
            # Das Rezept wird als Subprozess gestartet, um die Pins zu steuern
            subprocess.run(cmd, check=False)
        finally:
            # Nach Ende des Rezepts wird nur aufgeräumt
            root.after(0, _finalize_recipe, name)

    current_thread = threading.Thread(target=runner, daemon=True)
    current_thread.start()

root = tk.Tk()
root.title("Getränkemixer")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
root.configure(bg=BACKGROUND)

frame = tk.Frame(root, bg=BACKGROUND)
frame.pack(expand=True, fill="both", padx=40, pady=40)

status_label = tk.Label(root, text="Bitte warten, Homing läuft...", font=STATUS_FONT, fg=TEXT_COLOR, bg=BACKGROUND)
status_label.pack(pady=20)

files = sorted(f for f in RECIPES_DIR.iterdir() if f.is_file()) if RECIPES_DIR.exists() else []
if not files:
    tk.Label(frame, text="Keine Rezeptdateien gefunden.", font=("Arial", 32)).pack()
else:
    columns = 3
    for i, file_path in enumerate(files):
        name = file_path.stem.replace("Rezept_", "")
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
            width=20,
            height=5,
            command=lambda p=file_path: start_recipe(p)
        )
        btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    max_rows = (len(files) - 1) // columns + 1
    for c in range(columns):
        frame.grid_columnconfigure(c, weight=1)
    for r in range(max_rows):
        frame.grid_rowconfigure(r, weight=1)


# --- Homing-Start beim Anwendungsstart ---
run_initial_homing()


# NEUER CODE FÜR SAUBERES CLEANUP:
try:
    # Startet die GUI
    root.mainloop()
except KeyboardInterrupt:
    print("\nProgramm gestoppt durch Benutzer (Strg+C).")
finally:
    # Sauberes Herunterfahren der GPIO-Ressourcen
    print("Starte GPIO-Cleanup...")
    try:
        # Ruft die neue, zentralisierte Cleanup-Funktion auf
        initialisation_stepper.gpio_cleanup()
        print("GPIO-Ressourcen erfolgreich freigegeben.")
    except Exception as e:
        print(f"Warnung beim Cleanup: {e}")