import time
import sys
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory 

# Importiere die zentralen Module
import fill_function as fill 
import hardware_config as cfg

# --- Globale Konstanten ---
WAITING_STEPS = 2400 # 8 * 300 Schritte (Fixe Warteposition)

# Globale Variable für Button und Factory
_button = None
_factory = None

# -----------------------------------
# --- 1. SETUP / CLEANUP ---
# -----------------------------------

def _setup_homing_devices():
    """Initialisiert Button und Factory."""
    global _factory, _button
    
    if _button is not None:
        return # Bereits initialisiert

    try:
        # Start Factory und Stepper-Pins (über fill_function)
        _factory = PiGPIOFactory()

        # Taster initialisieren: Nutzt cfg-Werte direkt
        _button = Button(cfg.SWITCH_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory) 
        
        fill._setup_driver() # Initialisiert Stepper pins in fill_function
        fill._en_pin.on() # Stepper am Anfang deaktivieren

        print("Hardware-Setup für Homing erfolgreich.")
        return True

    except Exception as e:
        print(f"Fehler beim Setup der Homing-Geräte: {e}")
        gpio_cleanup() # Bei Fehler sofort aufräumen
        sys.exit(1)

def gpio_cleanup():
    """Schließt alle lokalen Ressourcen (Button) und ruft das globale Cleanup auf."""
    global _button, _factory

    # 1. Lokale Button-Ressourcen schließen
    if _button is not None:
        try:
            _button.close()
            print("-> Taster-Ressourcen erfolgreich freigegeben.")
        except Exception:
            pass 
        _button = None

    # 2. Ruft das globale Cleanup auf, das die Stepper-Pins schließt
    fill.gpio_cleanup()
    _factory = None 


# -----------------------------------
# --- 2. HOMING LOGIC (RAMPING) ---
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
        
        fill._raw_step(current_delay) # Nutzt die neue Roh-Schrittfunktion
        
        # Beschleunigung
        if current_delay > TARGET_DELAY:
            current_delay *= ACCEL_RATE 
            current_delay = max(current_delay, TARGET_DELAY) 

    # Ende
    print("\n\n*** HOME-POSITION ERREICHT (Position 0) ***")
    fill._en_pin.on()
    time.sleep(0.1)


# -----------------------------------
# --- 3. EXPORT FUNKTION ---
# -----------------------------------

def home_stepper():
    """Führt Homing durch (0) und fährt zur Warteposition (2400)."""
    
    _setup_homing_devices()
    
    try:
        # 1. Homing: Fährt in Richtung des Endschalters
        _ramp_move_until_pressed() 

        # 2. Zurückfahren auf die Warteposition (2400 Schritte)
        print(f"--- Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")
        
        fill.move_steps(WAITING_STEPS) 
        
        # 3. Aktuelle Position speichern
        fill.set_current_position(WAITING_STEPS)
        print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    except Exception as e:
        print(f"Fehler während der Homing-Routine: {e}")
        # Fehler an den Hauptprozess weitergeben
        raise 

    finally:
        gpio_cleanup()
        
        
# -----------------------------------
# --- 4. MANUELLER START (TEST) ---
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