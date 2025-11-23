import time
import RPi.GPIO as GPIO
import hardware_config as cfg

PINS = cfg.STEPPER_PINS
DRINK_POSITIONS = cfg.DRINK_POSITIONS
SERVO_PINS = cfg.SERVO_PINS
STEP_DELAY = cfg.STEP_DELAY
current_position = 0  # 0 = Startpunkt nach Homing

def set_current_position(position_steps: int = 0):
    global current_position
    current_position = position_steps

def _setup_driver():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINS["DIR"], GPIO.OUT)
    GPIO.setup(PINS["STEP"], GPIO.OUT)
    GPIO.setup(PINS["EN"], GPIO.OUT)
    GPIO.output(PINS["EN"], GPIO.LOW)

def _cleanup_driver():
    GPIO.output(PINS["EN"], GPIO.HIGH)
    GPIO.cleanup()

def _step_once():
    GPIO.output(PINS["STEP"], GPIO.HIGH)
    time.sleep(STEP_DELAY)
    GPIO.output(PINS["STEP"], GPIO.LOW)
    time.sleep(STEP_DELAY)

def move_steps(delta_steps: int):
    global current_position
    if delta_steps == 0:
        return
    direction = cfg.STEPPER_BACKWARD if delta_steps > 0 else cfg.STEPPER_FORWARD
    GPIO.output(PINS["DIR"], direction)
    for _ in range(abs(delta_steps)):
        _step_once()
    current_position += delta_steps

def move_to_position(target_steps: int):
    move_steps(target_steps - current_position)

def move_to_drink(drink_name: str):
    if drink_name not in DRINK_POSITIONS:
        raise KeyError(f"Unbekanntes Getränk: {drink_name}")
    _setup_driver()
    try:
        move_to_position(DRINK_POSITIONS[drink_name])
    finally:
        _cleanup_driver()

def _servo_duty(angle: float) -> float:
    return 2 + (angle / 18.0)

def pour_with_servo(servo_pin: int, forward_angle: float = 180, dwell: float = 0.5):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)
    try:
        pwm.ChangeDutyCycle(_servo_duty(forward_angle))
        time.sleep(0.3)
        time.sleep(dwell)
        pwm.ChangeDutyCycle(_servo_duty(0))
        time.sleep(0.3)
        pwm.ChangeDutyCycle(0)
    finally:
        pwm.stop()
        GPIO.cleanup(servo_pin)
