import time
import RPi.GPIO as GPIO
import hardware_config as cfg
import fill_function as fill

BACKOFF_STEPS = 50          # kurz vom Schalter weg
RECIPE_START_STEPS = 500    # zum Rezept-Startpunkt
TIMEOUT_SEC = 15

def _pull():
    return GPIO.PUD_UP if cfg.SWITCH_PULL.upper() == "UP" else GPIO.PUD_DOWN

def _step_once(step_pin):
    GPIO.output(step_pin, GPIO.HIGH)
    time.sleep(cfg.STEP_DELAY)
    GPIO.output(step_pin, GPIO.LOW)
    time.sleep(cfg.STEP_DELAY)

def home_stepper():
    pins = cfg.STEPPER_PINS
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins["DIR"], GPIO.OUT)
    GPIO.setup(pins["STEP"], GPIO.OUT)
    GPIO.setup(pins["EN"], GPIO.OUT)
    GPIO.setup(cfg.SWITCH_PIN, GPIO.IN, pull_up_down=_pull())

    GPIO.output(pins["EN"], GPIO.LOW)
    GPIO.output(pins["DIR"], cfg.STEPPER_FORWARD)

    start = time.time()
    try:
        while time.time() - start < TIMEOUT_SEC:
            if GPIO.input(cfg.SWITCH_PIN) == cfg.SWITCH_ACTIVE_STATE:
                break
            _step_once(pins["STEP"])
        else:
            raise RuntimeError("Homing-Timeout: Schalter nicht erreicht")

        # kleiner Backoff
        GPIO.output(pins["DIR"], cfg.STEPPER_BACKWARD)
        for _ in range(BACKOFF_STEPS):
            _step_once(pins["STEP"])

        # zum Rezept-Startpunkt fahren
        for _ in range(RECIPE_START_STEPS):
            _step_once(pins["STEP"])

        # Startpunkt setzen
        fill.set_current_position(0)
        return True
    finally:
        GPIO.output(pins["EN"], GPIO.HIGH)
        GPIO.cleanup()

if __name__ == "__main__":
    if home_stepper():
        print("Homing + Startpunkt abgeschlossen.")
