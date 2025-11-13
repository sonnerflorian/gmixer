import tkinter as tk

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
        name = file_path.stem  # Dateiname ohne .txt / .py / etc.

        btn = tk.Button(
            frame,
            text=name,
            font=("Arial", 24),
            width=15,
            height=3,
            # Hier kannst du später eine Funktion einbauen,
            # z.B. Rezept laden, Motor starten etc.
            command=lambda p=file_path: print(f"Ausgewählt: {p}")
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




root.mainloop()
