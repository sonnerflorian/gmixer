
## gmixer/Rezepte/Rezept_Apfelsaftschorle.py

import time
import sys
import os

# Füge das übergeordnete Verzeichnis zum Systempfad hinzu, 
# damit fill_function gefunden werden kann
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fill_function as fill

def main():
    # Wir vertrauen der Position aus Homing (2400)
    
    # 1. Apfelsaft (Target Pos: 0)
    fill.move_to_drink("Apfelsaft")
    fill.pour_with_servo(fill.SERVO_PINS["Apfelsaft"], dwell=0.7)
    time.sleep(0.5)

    # 2. Wasser (Target Pos: 800)
    fill.move_to_drink("Wasser")
    fill.pour_with_servo(fill.SERVO_PINS["Wasser"], dwell=0.7)
    time.sleep(0.5)

    # 3. Zurück zur Warteposition (2400 Schritte)
    fill.move_to_position(2400) 

if __name__ == "__main__":
    main()