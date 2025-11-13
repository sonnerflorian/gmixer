#!/usr/bin/env python3
"""
Rezept: Apfelschorle
"""

import time

RECIPE_NAME = "Apfelschorle"

# Schritte des Rezepts
STEPS = [
    {"beschreibung": "Apfelsaft einfüllen", "dauer": 3},
    {"beschreibung": "Wasser hinzufügen", "dauer": 2},
]

def run_step(step):
    """Einen Schritt ausführen."""
    beschreibung = step["beschreibung"]
    dauer = step["dauer"]

    print(f"➡️  Schritt: {beschreibung} | {dauer} Sekunden")
    time.sleep(dauer)
    print(f"   ✔️ Fertig: {beschreibung}\n")

def main():
    print(f"\n🥤 Starte Rezept: {RECIPE_NAME}\n")
    for step in STEPS:
        run_step(step)
    print(f"🎉 Rezept '{RECIPE_NAME}' abgeschlossen!\n")

if __name__ == "__main__":
    main()
