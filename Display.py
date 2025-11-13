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
)




# Pfad zu diesem Script
SCRIPT_DIR = Path(__file__).resolve().parent

#Pad zu den Rezepten
RECIPES_DIR = SCRIPT_DIR / "Rezepte"

# --- Funktion zum Erstellen eines runden Buttons ---
def create_rounded_button(parent, text, command):

    # Canvas für runden Button
    canvas = tk.Canvas(
        parent,
        width=350, height=120,
        bg=parent["bg"],
        highlightthickness=0,
        bd=0
    )

    # Koordinaten
    x1, y1, x2, y2 = 10, 10, 340, 110
    r = BUTTON_RADIUS

    # Abgerundetes Rechteck zeichnen
    canvas.create_round_rect = lambda *args, **kwargs: canvas.create_polygon(
        [
            x1+r, y1,
            x2-r, y1,
            x2, y1+r,
            x2, y2-r,
            x2-r, y2,
            x1+r, y2,
            x1, y2-r,
            x1, y1+r,
        ],
        smooth=True,
        **kwargs
    )

    rect = canvas.create_round_rect(
        fill="white",
        outline=PRIMARY_RED,
        width=3
    )

    # Text
    text_id = canvas.create_text(
        (175, 60),
        text=text,
        fill=PRIMARY_RED,
        font=BUTTON_FONT
    )

    # Klick-Effekt
    def on_click(event):
        command()

    canvas.bind("<Button-1>", on_click)

    # Hover-Effekte
    def on_enter(event):
        canvas.itemconfig(rect, fill="#f7d4d6")

    def on_leave(event):
        canvas.itemconfig(rect, fill="white")

    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)

    return canvas





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

        rounded = create_rounded_button(
            frame,
            text=name,
            command=lambda p=file_path: start_recipe(p)
        )
        rounded.grid(row=row, column=col, padx=20, pady=20)




        row = i // columns
        col = i % columns
        rounded.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    # Spalten/Zeilen dehnbar machen
    max_rows = (len(files) - 1) // columns + 1
    for c in range(columns):
        frame.grid_columnconfigure(c, weight=1)
    for r in range(max_rows):
        frame.grid_rowconfigure(r, weight=1)



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



root.mainloop()
