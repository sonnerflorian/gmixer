# Farben
BUTTON_BG = "#e8e8e8"
BUTTON_FG = "#333333"
BUTTON_ACTIVE = "#d0d0d0"

BACKGROUND = "white"
TEXT_COLOR = "red"

# Font
BUTTON_FONT = ("Arial", 24, "bold")
STATUS_FONT = ("Arial", 32)

# Hover-Effekte
def on_enter(e):
    e.widget['bg'] = BUTTON_ACTIVE

def on_leave(e):
    e.widget['bg'] = BUTTON_BG
