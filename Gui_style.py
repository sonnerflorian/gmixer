# gui_style.py

# Primärfarbe aus deinem Logo
PRIMARY_RED = "#c62729"

# Grundfarben
BACKGROUND = "white"        # kompletter Hintergrund
TEXT_COLOR = PRIMARY_RED    # Standard-Textfarbe

# Button-Design
BUTTON_BG = "white"         # Button-Hintergrund
BUTTON_FG = PRIMARY_RED     # Button-Schrift
BUTTON_ACTIVE_BG = "#f7d4d6"  # leichtes Rosa beim Drücken/Hover
BUTTON_ACTIVE_FG = PRIMARY_RED

# Schriftarten
STATUS_FONT = ("Arial", 32, "bold")
BUTTON_FONT = ("Arial", 24, "bold")

def on_enter(e):
    """Hover-Effekt für Buttons."""
    e.widget["bg"] = BUTTON_ACTIVE_BG

def on_leave(e):
    """Hover-Effekt beenden."""
    e.widget["bg"] = BUTTON_BG
