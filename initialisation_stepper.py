import time
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory 
import sys

# Importiere die zentralen Module
import fill_function as fill 
import hardware_config as cfg

# --- 1. GLOBALE KONFIGURATION ---
BUTTON_PIN = cfg.SWITCH_PIN
DELAY = cfg.STEP_DELAY 

# Definierte Warteposition in Schritten von Home (Button) entfernt
WAITING_STEPS = 2400 # 8 * 300 Schritte

# Globale Variable für den Taster und die Factory
_button = None
_factory = None

# -----------------------------------
# --- 2. GERÄTE-SETUP (NUR TASTER) ---
# -----------------------------------

try:
    # Starte die pigpio Factory
    _factory = PiGPIOFactory()

    # Taster initialisieren (Wir verwenden den festen Pull-Up von GPIO 2)
    _button = Button(BUTTON_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory) 
    
    print("Initialisierung abgeschlossen. Start bereit.")

except Exception as e:
    print(f"Fehler bei der Initialisierung: {e}")
    sys.exit(1)


# -----------------------------------
# --- 3. HOMING-ROUTINE ---
# -----------------------------------

def home_stepper():
    """Führt Homing durch und fährt zur Warteposition."""
    
    # 0. Setup der Stepper-Pins über fill_function
    # Dies initialisiert die Stepper-Pins in fill_function's globalen Variablen.
    fill._setup_driver() 
    
    # 1. Homing: Fährt in Richtung des Endschalters (BACKWARD)
    print("--- 1. STARTE HOME-SUCHE ---")
    
    # Setze Richtung und aktiviere Stepper über fill_function's globale Objekte
    fill._en_pin.off()
    fill._dir_pin.value = cfg.STEPPER_BACKWARD 
    time.sleep(0.005)
    
    # Schleife läuft, solange der Taster NICHT gedrückt ist
    while not _button.is_pressed:
        fill._step_once()
        
    print("\n\n*** HOME-POSITION ERREICHT (Position 0) ***")
    fill._en_pin.on() # Deaktivieren

    # 2. Zurückfahren auf die Warteposition (2400 Schritte)
    print(f"--- 2. Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")
    
    # Nutze die zentrale move_steps Funktion (setzt Richtung auf FORWARD)
    fill.move_steps(WAITING_STEPS) 
    
    # 3. Aktuelle Position speichern
    fill.set_current_position(WAITING_STEPS)
    print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    # Bereinigung der Stepper-Pins, damit das Rezept-Skript sie neu initialisieren kann
    fill._cleanup_driver()


# -----------------------------------
# --- 4. CLEANUP-FUNKTION ---
# -----------------------------------

def gpio_cleanup():
    """Schließt alle lokalen Ressourcen (Button) und ruft das globale Cleanup auf."""
    global _button

    # 1. Lokale Button-Ressourcen schließen (WICHTIG für Thread-Beendigung)
    if _button is not None:
        try:
            _button.close()
            print("-> Taster-Ressourcen erfolgreich freigegeben.")
        except Exception as e:
            print(f"Warnung beim Schließen des Tasters: {e}")

    # 2. Globales Cleanup für Stepper/Factory aufrufen (falls nötig)
    fill.gpio_cleanup()


# -----------------------------------
# --- 5. HAUPTPROGRAMM (Test-Code) ---
# -----------------------------------
# ... (Wird von main.py ignoriert und ist nur zum Testen gedacht)
# ...

if __name__ == "__main__":
    print("Starte manuelle Home-Suche...")
    
    # Stellen Sie sicher, dass alle globalen Ressourcen bereinigt werden,
    # egal ob die Routine normal oder durch Strg+C beendet wird.
    try:
        home_stepper()
    except KeyboardInterrupt:
        print("\nRoutine gestoppt durch Benutzer (Strg+C).")
    finally:
        gpio_cleanup()
        print("Manuelle Initialisierung beendet.")