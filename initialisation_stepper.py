#!/usr/bin/env python3
import time
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory
import sys
import pigpio

# Importiere die zentralen Module
import fill_function as fill
import hardware_config as cfg

# --- Globale Konstanten ---
WAITING_STEPS = 2500  # 8 * 300 Schritte

# --- FEST DEFINIERTE SERVO-PINS (unabhängig von hardware_config) ---
SERVO_PINS = [17, 5, 22, 26, 27, 18, 13, 19]

# Globale Variable für Button und Factory
_button = None
_factory = None

# -----------------------------------
# --- 1. SERVO CLEANUP ---
# -----------------------------------

def clean_servos():
    """
    Setzt alle Servo-Pins hart zurück (PWM aus).
    Kein Anfahren, kein Zucken – nur detach.
    """
    pi = pigpio.pi()
    if not pi.connected:
        print("-> pigpio nicht erreichbar, Servo-Cleanup übersprungen.")
        return

    try:
        for pin in SERVO_PINS:
            pi.set_servo_pulsewidth(pin, 0)  # detach
        print(f"-> Servos detached: {SERVO_PINS}")
    finally:
        pi.stop()


# -----------------------------------
# --- 2. SETUP / CLEANUP ---
# -----------------------------------

def _setup_homing_devices():
    """Initialisiert Button und Factory."""
    global _factory, _button

    if _button is not None:
        return  # Bereits initialisiert

    try:
        # 1. Stepper-Pins initialisieren (dies startet auch die Factory)
        fill._setup_driver()
        _factory = fill._factory  # Verwende die Factory von fill_function

        # 2. Taster initialisieren
        _button = Button(cfg.SWITCH_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory)

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

    # 0. Servos immer freigeben (detach)
    try:
        clean_servos()
    except Exception:
        pass

    # 1. Lokale Button-Ressourcen schließen
    if _button is not None:
        try:
            _button.close()
            print("-> Taster-Ressourcen erfolgreich freigegeben.")
        except Exception:
            pass
        _button = None

    # 2. Ruft das globale Cleanup auf
    # fill.gpio_cleanup()
    # _factory = None


# -----------------------------------
# --- 3. HOMING LOGIC (RAMPING) ---
# -----------------------------------

def _ramp_move_until_pressed():
    """Bewegt den Stepper mit Ramping, bis der Taster gedrückt wird."""

    # Ramping-Konstanten
    START_DELAY = 0.005
    TARGET_DELAY = cfg.STEP_DELAY
    ACCEL_RATE = 0.999
    current_delay = START_DELAY

    if _button.is_pressed:
        print("Taster ist bereits geschlossen.")
        return

    print(f"\n--- STARTE HOME-SUCHE (Richtung: Rückwärts) ---")

    # Motor aktivieren und Richtung setzen
    fill._en_pin.off()
    fill._dir_pin.value = cfg.STEPPER_BACKWARD
    time.sleep(0.005)

    # Endlosschleife
    while not _button.is_pressed:
        fill._raw_step(current_delay)

        # Beschleunigung
        if current_delay > TARGET_DELAY:
            current_delay *= ACCEL_RATE
            current_delay = max(current_delay, TARGET_DELAY)

    # Ende der Homing-Fahrt
    print("\n\n*** HOME-POSITION ERREICHT (Position 0) ***")

    # Backlash-Kompensation (5 Schritte in die Gegenrichtung)
    print("-> Führe Backlash-Kompensation aus.")

    fill._dir_pin.value = cfg.STEPPER_FORWARD  # Richtung WEG vom Endschalter setzen
    # Langsame Schritte, um sicherzustellen, dass sich der Motor bewegt
    for _ in range(5):
        fill._raw_step(0.005)

    fill._en_pin.on()  # Deaktiviert den Motor nach Backlash!
    time.sleep(0.1)


# -----------------------------------
# --- 4. EXPORT FUNKTION ---
# -----------------------------------

def home_stepper():
    """Führt Homing durch (0) und fährt zur Warteposition (2400)."""

    _setup_homing_devices()

    try:
        # 1. Homing: Fährt in Richtung des Endschalters
        _ramp_move_until_pressed()

        # NEUE AKTIVIERUNG: Muss den Motor re-aktivieren, nachdem _ramp_move_until_pressed ihn deaktiviert hat
        fill._en_pin.off()
        time.sleep(0.05)

        # 2. Zurückfahren auf die Warteposition (2400 Schritte)
        print(f"--- Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")

        fill.move_steps(WAITING_STEPS)

        # 3. Aktuelle Position speichern
        fill.set_current_position(WAITING_STEPS)
        print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    except Exception as e:
        print(f"Fehler während der Homing-Routine: {e}")
        raise

    finally:
        gpio_cleanup()


# -----------------------------------
# --- 5. MANUELLER START (TEST) ---
# -----------------------------------

if __name__ == "__main__":
    print("Starte manuelle Home-Suche...")

    try:
        home_stepper()
    except KeyboardInterrupt:
        print("\nRoutine gestoppt durch Benutzer (Strg+C).")
    finally:
        gpio_cleanup()
        print("Manuelle Initialisierung beendet.")
