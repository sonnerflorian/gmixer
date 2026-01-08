import time
from gpiozero import OutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# ============================================================
# 1) KONFIG (wie in deinem sequenztest.py aufgebaut)
# ============================================================

# Stepper Pins (A4988)
STEP_PIN = 16
DIR_PIN = 20
ENABLE_PIN = 21

DELAY = 0.0005  # Pulsdelay (sek) -> Geschwindigkeit (kleiner = schneller)
DIR_SETTLE = 0.005

# Servos (nur die zwei verwendeten)
SERVO_APFEL_PIN = 26
SERVO_WASSER_PIN = 19

# Winkel
CLOSE_ANGLE = 0
OPEN_ANGLE = 90

# "Ausschankzeit" (wie lange offen)
APFEL_OPEN_TIME = 0.8
WASSER_OPEN_TIME = 0.8

# Stepper-Positionen in SCHRITTEN (Beispielwerte!)
# start = 0; Apfel = +X; Wasser = +Y
POS_START = 0
POS_APFEL = 1200
POS_WASSER = 2400

# Richtungskonvention:
# Wenn der Stepper falsch herum läuft: FORWARD_DIR einfach umdrehen (True <-> False)
FORWARD_DIR = False
BACKWARD_DIR = not FORWARD_DIR


# ============================================================
# 2) SETUP (Factory + Geräte, wie in sequenztest.py)
# ============================================================

factory = PiGPIOFactory()  # nutzt pigpiod (localhost:8888)

dir_pin = OutputDevice(DIR_PIN, pin_factory=factory)
enable_pin = OutputDevice(ENABLE_PIN, pin_factory=factory)
step_pin = OutputDevice(STEP_PIN, pin_factory=factory)

servo_apfel = Servo(SERVO_APFEL_PIN, pin_factory=factory)
servo_wasser = Servo(SERVO_WASSER_PIN, pin_factory=factory)

# Servos direkt freigeben (wie bei dir)
servo_apfel.detach()
servo_wasser.detach()

# Stepper deaktivieren (A4988 typisch: HIGH = aus)
enable_pin.on()

print("Initialisierung abgeschlossen. Geräte bereit.")


# ============================================================
# 3) HELPER (Servo exakt wie in deinem Script)
# ============================================================

def set_servo_angle(servo_obj: Servo, angle: float, settle: float = 0.5) -> None:
    """Bewegt Servo zu Winkel und deaktiviert Signal wieder (detach)."""
    value = (angle / 90.0) - 1.0  # 0°->-1, 90°->0, 180°->1
    servo_obj.value = value
    time.sleep(settle)
    servo_obj.detach()


def pour(servo_obj: Servo, open_time: float) -> None:
    """0 -> 90 -> 0, mit detach nach jedem Schritt (wie sequenztest)."""
    set_servo_angle(servo_obj, CLOSE_ANGLE)
    time.sleep(0.2)

    set_servo_angle(servo_obj, OPEN_ANGLE)
    time.sleep(open_time)

    set_servo_angle(servo_obj, CLOSE_ANGLE)
    time.sleep(0.3)


def move_stepper(steps: int, direction: bool) -> None:
    """Bewegt Stepper per manueller HIGH/LOW Schleife und deaktiviert ihn."""
    if steps <= 0:
        return

    print(f"-> Stepper: {steps} Schritte, dir={direction}")

    # aktivieren (LOW = an)
    enable_pin.off()

    # Richtung setzen
    dir_pin.value = direction
    time.sleep(DIR_SETTLE)

    # Schritte pulsen
    for _ in range(steps):
        step_pin.on()
        time.sleep(DELAY)
        step_pin.off()
        time.sleep(DELAY)

    # deaktivieren (HIGH = aus)
    enable_pin.on()
    time.sleep(0.1)


# ============================================================
# 4) REZEPTLOGIK (mit Positionen)
# ============================================================

current_pos = POS_START  # wichtig: ohne Homing muss Startlage stimmen!


def move_to(target_pos: int) -> None:
    global current_pos
    delta = target_pos - current_pos
    if delta == 0:
        return

    direction = FORWARD_DIR if delta > 0 else BACKWARD_DIR
    move_stepper(abs(delta), direction)
    current_pos = target_pos


def main():
    print("Starte Rezept: Apfelsaftschorle (Stepper + Servo-detach Sequenz)")

    # Sicherheitszustand: Ventile zu
    set_servo_angle(servo_apfel, CLOSE_ANGLE)
    set_servo_angle(servo_wasser, CLOSE_ANGLE)

    # 1) zu Apfel fahren + ausschenken
    move_to(POS_APFEL)
    print("-> Apfelsaft")
    pour(servo_apfel, APFEL_OPEN_TIME)

    time.sleep(0.6)

    # 2) zu Wasser fahren + ausschenken
    move_to(POS_WASSER)
    print("-> Wasser")
    pour(servo_wasser, WASSER_OPEN_TIME)

    # 3) zurück zu Start
    move_to(POS_START)
    print("Fertig.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer (Strg+C).")
    finally:
        # Safe-Off
        enable_pin.on()
        servo_apfel.detach()
        servo_wasser.detach()
        print("Cleanup: Stepper deaktiviert, Servos detached.")
