
# gmixer/Rezepte/Rezept_Apfelsaftschorle.py
import time

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))          # .../gmixer/Rezepte
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))    # .../gmixer

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)



import hardware_config as hw
from gpiozero import OutputDevice, Servo

# Optional: ruhigeres Servo-PWM mit pigpio
try:
    from gpiozero.pins.pigpio import PiGPIOFactory
    _PIGPIO_FACTORY = PiGPIOFactory()
except Exception:
    _PIGPIO_FACTORY = None


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def _make_output(pin: int) -> OutputDevice:
    return OutputDevice(pin, initial_value=False)


def _make_servo(pin: int) -> Servo:
    if _PIGPIO_FACTORY is not None:
        return Servo(pin, pin_factory=_PIGPIO_FACTORY)
    return Servo(pin)


def set_servo_angle(servo: Servo, angle: float) -> None:
    """
    Mapping:
    0°   -> -1
    90°  ->  0
    180° ->  1
    """
    servo.value = (angle / 90.0) - 1.0


def pour_with_servo(
    servo_pin: int,
    dwell: float = 0.7,
    open_angle: float = 90.0,
    close_angle: float = 0.0,
):
    servo = _make_servo(servo_pin)
    try:
        set_servo_angle(servo, open_angle)
        time.sleep(float(dwell))
        set_servo_angle(servo, close_angle)
        time.sleep(0.4)
    finally:
        servo.close()


# ------------------------------------------------------------
# Stepper (ohne Homing!)
# ------------------------------------------------------------
class Stepper:
    def __init__(self):
        self.dir = _make_output(hw.STEPPER_PINS["DIR"])
        self.step = _make_output(hw.STEPPER_PINS["STEP"])
        self.en = _make_output(hw.STEPPER_PINS["EN"])
        self.step_delay = float(hw.STEP_DELAY)

        # A4988 typisch: EN LOW = enabled
        self.en.on()  # deaktiviert
        self.position_steps = hw.DRINK_POSITIONS.get("start", 0)

    def enable(self):
        self.en.off()

    def disable(self):
        self.en.on()

    def do_steps(self, direction: bool, steps: int):
        if steps <= 0:
            return

        self.dir.value = not bool(direction)

        for _ in range(steps):
            self.step.on()
            time.sleep(self.step_delay)
            self.step.off()
            time.sleep(self.step_delay)

        if direction == hw.STEPPER_FORWARD:
            self.position_steps += steps
        else:
            self.position_steps -= steps

    def move_to(self, target_steps: int):
        delta = target_steps - self.position_steps
        if delta == 0:
            return

        direction = hw.STEPPER_FORWARD if delta > 0 else hw.STEPPER_BACKWARD
        self.do_steps(direction, abs(delta))


# ------------------------------------------------------------
# Rezept: Apfelsaftschorle
# ------------------------------------------------------------
def main():
    stepper = Stepper()
    stepper.enable()

    # 1) Apfelsaft
    stepper.move_to(hw.DRINK_POSITIONS["Apfelsaft"])
    pour_with_servo(hw.SERVO_PINS["Apfelsaft"], dwell=0.7)
    time.sleep(0.5)

    # 2) Wasser
    stepper.move_to(hw.DRINK_POSITIONS["Wasser"])
    pour_with_servo(hw.SERVO_PINS["Wasser"], dwell=0.7)
    time.sleep(0.5)

    # 3) Zurück zur Startposition
    stepper.move_to(hw.DRINK_POSITIONS["start"])

    stepper.disable()


if __name__ == "__main__":
    main()
