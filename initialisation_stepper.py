#!/usr/bin/env python3
import time
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory
import sys
import pigpio
import fill_function as fill

STEPS_TO_START = 2500

SERVO_PINS = [17, 5, 22, 26, 27, 18, 13, 19]
SWITCH_PIN = 2               
SWITCH_PULL = True  

STEPPER_FORWARD = True
STEPPER_BACKWARD = False
STEP_DELAY = 0.0005  

_button = None
_factory = None


def clean_servos():
    pi = pigpio.pi()
    try:
        for pin in SERVO_PINS:
            pi.set_servo_pulsewidth(pin, 0)
        print(f"-> Servos detached: {SERVO_PINS}")
    finally:
        pi.stop()


def _setup_init_devices():
    """Initialisiert Button und Factory."""
    global _factory, _button

    if _button is not None:
        return  # Bereits initialisiert

    try:
        # 1. Stepper-Pins initialisieren (dies startet auch die Factory)
        fill._setup_driver()
        _factory = fill._factory  # Verwende die Factory von fill_function

        # 2. Taster initialisieren
        _button = Button(SWITCH_PIN, pull_up=SWITCH_PULL, pin_factory=_factory)

        fill._en_pin.on()  # Stepper am Anfang deaktivieren

        print("Hardware-Setup für Homing erfolgreich.")
        return True

    except Exception as e:
        print(f"Fehler beim Setup der Homing-Geräte: {e}")
        gpio_cleanup()  # Bei Fehler sofort aufräumen
        sys.exit(1)


def gpio_cleanup():
    """Schließt alle lokalen Ressourcen (Button) und ruft das globale Cleanup auf."""
    global _button, _factory

    try:
        clean_servos()
    except Exception:
        pass

    if _button is not None:
        try:
            _button.close()
            print("-> Taster-Ressourcen erfolgreich freigegeben.")
        except Exception:
            pass
        _button = None


def move_until_pressed():
    """Bewegt den Stepper mit konstanter Geschwindigkeit, bis der Taster gedrückt wird."""

    STEP_DELAY = STEP_DELAY

    if _button.is_pressed:
        print("Taster ist bereits geschlossen.")
        return

    print(f"\n--- STARTE HOME-SUCHE (Richtung: Rückwärts) ---")

    # Motor aktivieren und Richtung setzen
    fill._en_pin.off()
    fill._dir_pin.value = STEPPER_BACKWARD
    time.sleep(0.005)


    while not _button.is_pressed:
        fill._raw_step(STEP_DELAY)

    fill._dir_pin.value = STEPPER_FORWARD  
    for _ in range(5):
        fill._raw_step(STEP_DELAY)

    fill._en_pin.on()
    time.sleep(0.1)


def init_stepper():

    _setup_init_devices()

    try:
        move_until_pressed()

        fill._en_pin.off()
        time.sleep(0.05)

        fill.move_steps(STEPS_TO_START)

        fill.set_current_position(STEPS_TO_START)
        print(f"*** WARTEPOSITION BEI {STEPS_TO_START} SCHRITTEN ERREICHT. ***")

    except Exception as e:
        print(f"Fehler während der Initialisierung: {e}")
        raise

    finally:
        gpio_cleanup()


if __name__ == "__main__":
    print("Starte Initailisierung...")

    try:
        init_stepper()
    except KeyboardInterrupt:
        print("\nInitialisierung gestoppt")
    finally:
        gpio_cleanup()
        print("Initialisierung beendet.")
