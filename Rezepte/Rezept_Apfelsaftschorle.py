
# gmixer/Rezepte/Rezept_Apfelsaftschorle.py

import time
import fill_function as fill

def main():
    # ENTFERNT: fill.set_current_position(0) - Wir vertrauen der Position aus Homing (2400)

    # 1. Apfelsaft (Target Pos: 0)
    # Motor bewegt sich von 2400 zu 0
    fill.move_to_drink("Apfelsaft")
    fill.pour_with_servo(fill.SERVO_PINS["Apfelsaft"], dwell=0.7)
    time.sleep(0.5)

    # 2. Wasser (Target Pos: 800)
    # Motor bewegt sich von 0 zu 800
    fill.move_to_drink("Wasser")
    fill.pour_with_servo(fill.SERVO_PINS["Wasser"], dwell=0.7)
    time.sleep(0.5)

    # 3. Zurück zur Warteposition (2400 Schritte)
    # Motor bewegt sich von 800 zu 2400
    fill.move_to_position(2400) 

    # Hinzugefügter Code im alten Script war falsch platziert, da gpio_cleanup bereits
    # im finally-Block von main.py aufgerufen wird.
    # fill._setup_driver() # Wird in move_to_position aufgerufen
    # try:
    #     fill.move_to_position(0)  # zurück zum Start
    # finally:
    #     fill._cleanup_driver() # Wird nicht mehr benötigt

if __name__ == "__main__":
    main()