#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# --------- Konfiguration ---------
DRINKS = [
    "Cola", "Fanta", "Sprite",
    "Wasser", "Apfelschorle", "Eistee",
    "Kaffee", "Latte", "Mate"
]

WINDOW_TITLE = "Getränkeauswahl"
WINDOW_SIZE = "800x480"     # z.B. "1024x600" oder "" für automatisch
PRIMARY = "#0ea5e9"         # Akzentfarbe (helles Blau)
BG_DARK = "#0f172a"         # Hintergrund
CARD_BG = "#111827"         # Karten-Hintergrund
CARD_FG = "#e5e7eb"         # Karten-Text
MUTED = "#94a3b8"           # Sekundärtext
OK_GREEN = "#22c55e"
WARN = "#fdba74"
# ---------------------------------

class DrinkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        if WINDOW_SIZE:
            self.geometry(WINDOW_SIZE)
        self.configure(bg=BG_DARK)

        self.selected = []  # aktuelle Auswahl (1 oder 3, je nach Use-Case)

        self._build_styles()
        self._build_header()
        self._build_grid()
        self._build_footer()

    def _build_styles(self):
        self.style = ttk.Style(self)
        # Auf Linux/PI ist "clam" i. d. R. verfügbar
        try:
            self.style.theme_use("clam")
        except:
            pass

        self.style.configure("App.TFrame", background=BG_DARK)
        self.style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        self.style.configure("Card.TLabel", background=CARD_BG, foreground=CARD_FG, font=("Arial", 18, "bold"))
        self.style.configure("Small.TLabel", background=BG_DARK, foreground=MUTED, font=("Arial", 12))
        self.style.configure("Title.TLabel", background=BG_DARK, foreground="white", font=("Arial", 24, "bold"))

        self.style.configure("Primary.TButton",
                             font=("Arial", 16, "bold"),
                             padding=10)
        self.style.map("Primary.TButton",
                       background=[("!disabled", PRIMARY)],
                       foreground=[("!disabled", "white")])

        self.style.configure("Ghost.TButton",
                             font=("Arial", 14),
                             padding=8)
        self.style.map("Ghost.TButton",
                       foreground=[("!disabled", CARD_FG)],
                       background=[("!disabled", CARD_BG)])

        self.style.configure("Confirm.TButton",
                             font=("Arial", 16, "bold"),
                             padding=10)
        self.style.map("Confirm.TButton",
                       background=[("!disabled", OK_GREEN)],
                       foreground=[("!disabled", "white")])

    def _build_header(self):
        header = ttk.Frame(self, style="App.TFrame")
        header.pack(side="top", fill="x", padx=16, pady=(16, 8))

        title = ttk.Label(header, text="Wähle ein Getränk", style="Title.TLabel")
        title.pack(side="left")

        custom_btn = ttk.Button(header, text="Eigene 3 wählen", style="Primary.TButton",
                                command=self.open_custom_dialog)
        custom_btn.pack(side="right")

    def _build_grid(self):
        grid = ttk.Frame(self, style="App.TFrame")
        grid.pack(expand=True, fill="both", padx=16, pady=8)

        grid.columnconfigure((0,1,2), weight=1, uniform="cols")
        grid.rowconfigure((0,1,2), weight=1, uniform="rows")

        # Karten für 9 Getränke
        for idx, name in enumerate(DRINKS):
            r, c = divmod(idx, 3)
            card = ttk.Frame(grid, style="Card.TFrame")
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            # „Hover“-Effekt (leicht)
            def on_enter(e, w=card):
                w.configure(style="Card.TFrame")
                w.configure(cursor="hand2")
            def on_leave(e, w=card):
                w.configure(style="Card.TFrame")
                w.configure(cursor="")

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            label = ttk.Label(card, text=name, style="Card.TLabel")
            label.pack(padx=16, pady=(24, 8))

            # Auswählen-Button (ein Getränk)
            btn = ttk.Button(card, text="Auswählen", style="Ghost.TButton",
                             command=lambda n=name: self.select_single(n))
            btn.pack(padx=16, pady=(0, 16))

    def _build_footer(self):
        footer = ttk.Frame(self, style="App.TFrame")
        footer.pack(side="bottom", fill="x", padx=16, pady=(8, 16))

        self.status_var = tk.StringVar(value="Bereit.")
        status = ttk.Label(footer, textvariable=self.status_var, style="Small.TLabel", anchor="w")
        status.pack(side="left")

        confirm = ttk.Button(footer, text="Bestätigen", style="Confirm.TButton",
                             command=self.confirm_selection)
        confirm.pack(side="right")

    # --- Aktionen ---
    def select_single(self, drink):
        self.selected = [drink]
        self._update_status()

    def open_custom_dialog(self):
        CustomDialog(self, DRINKS, preselected=self.selected[:3], on_done=self._set_custom)

    def _set_custom(self, chosen_list):
        self.selected = chosen_list
        self._update_status()

    def _update_status(self):
        if not self.selected:
            self.status_var.set("Keine Auswahl.")
        elif len(self.selected) == 1:
            self.status_var.set(f"Ausgewählt: {self.selected[0]}")
        else:
            self.status_var.set(f"Ausgewählt (3): {', '.join(self.selected)}")

    def confirm_selection(self):
        if not self.selected:
            messagebox.showwarning("Hinweis", "Bitte wähle mindestens ein Getränk.")
            return
        if len(self.selected) == 1:
            messagebox.showinfo("Bestätigt", f"Du hast gewählt: {self.selected[0]}")
        else:
            messagebox.showinfo("Bestätigt", f"Du hast gewählt: {', '.join(self.selected)}")


class CustomDialog(tk.Toplevel):
    def __init__(self, parent, drinks, preselected=None, on_done=None):
        super().__init__(parent)
        self.title("Eigene 3 wählen")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()

        self.drinks = drinks
        self.on_done = on_done
        self.vars = {}
        self.max_select = 3

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(expand=True, fill="both", padx=16, pady=16)

        ttk.Label(container, text="Wähle bis zu 3 Getränke", style="Title.TLabel").pack(anchor="w", pady=(0,10))

        self.count_var = tk.StringVar(value="0 / 3 gewählt")
        ttk.Label(container, textvariable=self.count_var, style="Small.TLabel").pack(anchor="w", pady=(0,10))

        grid = ttk.Frame(container, style="App.TFrame")
        grid.pack(expand=True, fill="both")
        grid.columnconfigure((0,1,2), weight=1, uniform="cols")

        # Checkbuttons in 3×3
        for i, name in enumerate(self.drinks):
            r, c = divmod(i, 3)
            frame = ttk.Frame(grid, style="Card.TFrame")
            frame.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            var = tk.BooleanVar(value=False)
            if preselected and name in preselected:
                var.set(True)
            self.vars[name] = var

            lbl = ttk.Label(frame, text=name, style="Card.TLabel")
            lbl.pack(padx=12, pady=(16,6))

            cb = ttk.Checkbutton(frame, text="auswählen", variable=var,
                                 command=self._on_toggle, style="Ghost.TButton")
            # Stiltrick: Checkbutton wie Button aussehen lassen
            cb.pack(padx=12, pady=(0,12))

        # Buttons
        btns = ttk.Frame(container, style="App.TFrame")
        btns.pack(fill="x", pady=(12,0))
        ttk.Button(btns, text="Abbrechen", style="Ghost.TButton", command=self._cancel).pack(side="left")
        ttk.Button(btns, text="Übernehmen", style="Confirm.TButton", command=self._apply).pack(side="right")

        # Nach Vorbelegung Limit durchsetzen
        self._enforce_limit()

    def _selected_list(self):
        return [n for n, v in self.vars.items() if v.get()]

    def _on_toggle(self):
        self._enforce_limit()

    def _enforce_limit(self):
        chosen = self._selected_list()
        cnt = len(chosen)
        self.count_var.set(f"{cnt} / {self.max_select} gewählt")

        # Wenn Limit erreicht, alle noch nicht ausgewählten Checkbuttons „sperren“
        disable_more = cnt >= self.max_select
        for name, var in self.vars.items():
            cb = self._get_associated_checkbutton(name)
            if not cb:
                continue
            if disable_more and not var.get():
                cb.state(["disabled"])
            else:
                cb.state(["!disabled"])

    def _get_associated_checkbutton(self, name):
        # Sucht das Checkbutton-Widget innerhalb der Karte (letztes Kind mit class TCheckbutton)
        # (einfacher Ansatz: gehe durch alle Kinder in diesem Dialog)
        for w in self.winfo_children():
            for sub in w.winfo_children():
                for subsub in sub.winfo_children():
                    if isinstance(subsub, ttk.Checkbutton):
                        # Text vergleichen
                        if subsub.cget("text") == "auswählen":
                            # Leider gibt ttk.Checkbutton keine direkte Variable preis – wir nutzen den Zustand:
                            # Wir mappen über die Label-Nachbarn:
                            pass
        # Vereinfachung: wir traversieren die Struktur erneut präziser:
        for frame in self.children.values():
            for g in frame.children.values():
                # Grid frame mit Karten:
                for card in g.children.values():
                    kids = list(card.children.values())
                    if len(kids) == 2 and isinstance(kids[0], ttk.Label) and isinstance(kids[1], ttk.Checkbutton):
                        if kids[0].cget("text") == name:
                            return kids[1]
        return None

    def _apply(self):
        chosen = self._selected_list()
        if len(chosen) == 0:
            messagebox.showwarning("Hinweis", "Bitte wähle mindestens ein Getränk.")
            return
        if len(chosen) > self.max_select:
            messagebox.showwarning("Hinweis", "Maximal 3 Getränke erlaubt.")
            return
        if self.on_done:
            self.on_done(chosen)
        self.destroy()

    def _cancel(self):
        self.destroy()


if __name__ == "__main__":
    app = DrinkApp()
    # Optional: Vollbild (Kiosk)
    # app.attributes("-fullscreen", True)
