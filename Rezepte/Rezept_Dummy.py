import time
import pigpio

# ----------------------------
# GPIO Pins der Servos
# ----------------------------
SERVO_APFEL = 26
SERVO_WASSER = 19

# Pulsweiten (ggf. feinjustieren!)
PULSE_CLOSED = 1000   # 0°
PULSE_OPEN   = 1500   # 90°

# Ausschankzeiten (Sekunden)
TIME_APFEL  = 0.8
TIME_WASSER = 0.8


def pour(pi, pin, duration):
    """Öffnet Servo, wartet, schließt wieder"""
    pi.set_servo_pulsewidth(pin, PULSE_OPEN)
    time.sleep(duration)
    pi.set_servo_pulsewidth(pin, PULSE_CLOSED)
    time.sleep(0.4)


def main():
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("❌ pigpio daemon läuft nicht (sudo systemctl start pigpiod)")

    try:
        # Start: beide Ventile sicher zu
        pi.set_servo_pulsewidth(SERVO_APFEL, PULSE_CLOSED)
        pi.set_servo_pulsewidth(SERVO_WASSER, PULSE_CLOSED)
        time.sleep(0.5)

        # 1️⃣ Apfelsaft
        pour(pi, SERVO_APFEL, TIME_APFEL)

        # kleine Pause
        time.sleep(0.5)

        # 2️⃣ Wasser
        pour(pi, SERVO_WASSER, TIME_WASSER)

    finally:
        # Servos freigeben (kein Summen)
        pi.set_servo_pulsewidth(SERVO_APFEL, 0)
        pi.set_servo_pulsewidth(SERVO_WASSER, 0)
        pi.stop()


if __name__ == "__main__":
    main()
