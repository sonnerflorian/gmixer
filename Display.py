import tkinter as tk
from pathlib import Path
import subprocess 
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

#Pad zu den Rezepten
RECIPES_DIR = SCRIPT_DIR / "Rezepte"


# --- Funktion zum Starten des Rezeptprogramms ---
def start_recipe(file_path: Path):
    # Rezeptname herausfiltern
    name = file_path.stem.replace("Rezept_", "")

    # Text anzeigen
    status_label.config(text=f"{name} wird zubereitet...")

    # Alle Buttons ausblenden
    frame.pack_forget()

    print(f"Starte: {file_path}")

    # Rezeptprogramm ausführen
    if file_path.suffix == ".py":
        subprocess.Popen(["python3", str(file_path)])
    elif file_path.suffix == ".sh":
        subprocess.Popen(["bash", str(file_path)])
    else:
        subprocess.Popen(["xdg-open", str(file_path)])





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
