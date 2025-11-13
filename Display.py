import tkinter as tk
from pathlib import Path

# Pfad zu diesem Script
SCRIPT_DIR = Path(__file__).resolve().parent

#Pad zu den Rezepten
RECIPES_DIR = SCRIPT_DIR / "Rezepte"

root = tk.Tk()
root.title("Hello World")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

frame = tk.Frame(root)
frame.pack(expand=True, fill="both", padx=40, pady=40)

status_label = tk.Label(root, text="", font=("Arial", 32))
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

        btn = tk.Button(
            frame,
            text=name,
            font=("Arial", 24),
            width=15,
            height=3,
            # Hier kannst du später eine Funktion einbauen,
            # z.B. Rezept laden, Motor starten etc.
            command=lambda p=file_path: start_recipe(p)
        )

        row = i // columns
        col = i % columns
        btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    # Spalten/Zeilen dehnbar machen
    max_rows = (len(files) - 1) // columns + 1
    for c in range(columns):
        frame.grid_columnconfigure(c, weight=1)
    for r in range(max_rows):
        frame.grid_rowconfigure(r, weight=1)

# --- Funktion zum Starten des Rezeptprogramms ---
def start_recipe(file_path: Path):

    name = file_path.stem.replace("Rezept_", "")
    status_label.config(text=f"{name} wird zubereitet...")
    print(f"Starte: {file_path}")

    # Python-Rezept starten
    if file_path.suffix == ".py":
        subprocess.Popen(["python3", str(file_path)])

    # Shell-Skript starten
    elif file_path.suffix == ".sh":
        subprocess.Popen(["bash", str(file_path)])

    # Andere Dateien → öffnen
    else:
        subprocess.Popen(["xdg-open", str(file_path)])



root.mainloop()
