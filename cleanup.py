import time
import pigpio

# -------------------------------------------------
# ALLE SERVO GPIO PINS (anpassen!)
# -------------------------------------------------
SERVO_PINS = [ 5, 17, 13, 26, 18, 22, 27, 19 
]

# OPTIONAL: Stepper Enable Pin (A4988)
ENABLE_PIN = 21  # oder None, wenn nicht vorhanden


def main():
    print("🧹 Starte Servo / GPIO Cleanup")

    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon nicht erreichbar")

    try:
        # Alle Servos freigeben (PWM = 0)
        for pin in SERVO_PINS:
            pi.set_servo_pulsewidth(pin, 0)
            print(f"Servo GPIO {pin}: detached")

        # Stepper deaktivieren (falls vorhanden)
        if ENABLE_PIN is not None:
            pi.write(ENABLE_PIN, 1)  # HIGH = disable (A4988 typisch)
            print(f"Stepper ENABLE GPIO {ENABLE_PIN}: deaktiviert")

        time.sleep(0.2)

    finally:
        pi.stop()
        print("✅ Cleanup abgeschlossen. Alle Signale aus.")


if __name__ == "__main__":
    main()
