
# gmixer/Rezepte/Rezept_Apfelsaftschorle.py

import time
import fill_function as fill

def main():
    fill.set_current_position(0)  # Startpunkt

    # 1. Apfelsaft
    fill.move_to_drink("Apfelsaft")
    fill.pour_with_servo(fill.SERVO_PINS["Apfelsaft"], dwell=0.7)
    time.sleep(0.5)

    # 2. Wasser
    fill.move_to_drink("Wasser")
    fill.pour_with_servo(fill.SERVO_PINS["Wasser"], dwell=0.7)
    time.sleep(0.5)

    # 3. Zurück zur Home-Position (die der Subprozess steuert)
    # Entferne _setup_driver und _cleanup_driver
    fill.move_to_position(0)  # zurück zum Start


if __name__ == "__main__":
    main()