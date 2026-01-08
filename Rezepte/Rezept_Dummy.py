import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# --- KONFIG ---
SERVO_APFEL_PIN = 26
SERVO_WASSER_PIN = 19

OPEN_ANGLE = 90
CLOSE_ANGLE = 0

# "Ausschankzeit" = wie lange Ventil offen bleibt
APFEL_OPEN_TIME = 0.8
WASSER_OPEN_TIME = 0.8

# --- SETUP (wie in deinem sequenztest.py) ---
factory = PiGPIOFactory()

servo_apfel = Servo(SERVO_APFEL_PIN, pin_factory=factory)
servo_wasser = Servo(SERVO_WASSER_PIN, pin_factory=factory)

# sicherheitshalber direkt "freigeben"
servo_apfel.detach()
servo_wasser.detach()


def set_servo_angle(servo_obj: Servo, angle: float, settle: float = 0.4):
    """
    Bewegt den Servo zu einem Winkel und deaktiviert das Signal wieder (detach),
    genau wie in deinem sequenztest.py. :contentReference[oaicite:1]{index=1}
    """
    value = (angle / 90.0) - 1.0  # 0°->-1, 90°->0, 180°->1
    servo_obj.value = value
    time.sleep(settle)
    servo_obj.detach()


def pour(servo_obj: Servo, open_time: float):
    """Ventil auf -> offen halten -> zu (alles jeweils mit detach)"""
    set_servo_angle(servo_obj, CLOSE_ANGLE)
    time.sleep(0.2)

    set_servo_angle(servo_obj, OPEN_ANGLE)
    time.sleep(open_time)

    set_servo_angle(servo_obj, CLOSE_ANGLE)
    time.sleep(0.3)


def main():
    print("Starte Apfelsaftschorle (nur 2 Servos, sequentiell).")

    # 1) Apfelsaft
    print("-> Apfelsaft Servo")
    pour(servo_apfel, APFEL_OPEN_TIME)

    time.sleep(0.6)  # kleine Pause zwischen den Komponenten

    # 2) Wasser
    print("-> Wasser Servo")
    pour(servo_wasser, WASSER_OPEN_TIME)

    print("Fertig.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer.")
    finally:
        # sicherheitshalber freigeben
        servo_apfel.detach()
        servo_wasser.detach()
