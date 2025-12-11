import time
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory 
import sys

# Importiere die zentralen Module
import fill_function as fill 
import hardware_config as cfg

# --- 1. GLOBALE KONFIGURATION ---

# Stepper-Konstanten und Warteposition
DELAY = cfg.STEP_DELAY 
WAITING_STEPS = 2400 # 8 * 300 Schritte

# Globale Variable für den Taster und die Factory (NEU: Werden erst bei Bedarf gesetzt)
_button = None
_factory = None


def _initialize_button():
    """Initialisiert Button und Factory, falls noch nicht geschehen."""
    global _factory, _button
    
    if _button is not None:
        return # Bereits initialisiert

    try:
        _factory = PiGPIOFactory()
        
        # NEU: Pin-Initialisierung in einer Funktion, um NameError zu vermeiden
        _button = Button(cfg.SWITCH_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory) 
        
        print("Taster-Initialisierung erfolgreich.")

    except Exception as e:
        print(f"Fehler bei der Taster-Initialisierung: {e}")
        sys.exit(1)


# -----------------------------------
# --- 3. HOMING-HELPER ---
# -----------------------------------

def move_stepper_until_button_pressed(direction=False):
    """
    Bewegt den Steppermotor mit Ramping, bis der Taster gedrückt wird.
    """
    
    # Sicherstellen, dass der Taster initialisiert ist
    _initialize_button() 
    
    # 1. Prüfe, ob der Taster bereits gedrückt ist
    if _button.is_pressed:
        print("Taster ist bereits geschlossen. Home-Position gefunden.")
        return
        
    print(f"\n--- STARTE HOME-SUCHE (Richtung: {'Vorwärts' if direction else 'Rückwärts'}) ---")
    
    # Ramping-Konstanten
    START_DELAY = 0.005    # Sehr langsamer Start
    TARGET_DELAY = cfg.STEP_DELAY # 0.001s (Ihr gewünschtes End-Tempo)
    ACCEL_RATE = 0.999     # Beschleunigungsfaktor
    
    current_delay = START_DELAY
    
    # Motor aktivieren und Richtung setzen
    fill._setup_driver() # Stellt sicher, dass die Stepper-Pins bereit sind
    fill._en_pin.off()
    fill._dir_pin.value = direction 
    time.sleep(0.005) 
    
    # Endlosschleife mit Beschleunigung
    while not _button.is_pressed:
        
        # Sende einen Schritt
        fill._step_pin.on() 
        time.sleep(current_delay)
        
        fill._step_pin.off()
        time.sleep(current_delay)
        
        # Beschleunigungs-Logik: Reduziere den Delay schrittweise
        if current_delay > TARGET_DELAY:
            current_delay *= ACCEL_RATE 
            current_delay = max(current_delay, TARGET_DELAY) 

    # Wenn die Schleife beendet wird, wurde der Taster gedrückt
    print("\n\n*** HOME-POSITION ERREICHT UND MOTOR GESTOPPT! ***")
    
    # Motor deaktivieren
    fill._en_pin.on()
    time.sleep(0.1)


def home_stepper():
    """Führt Homing durch und fährt zur Warteposition."""
    
    # 1. Homing: Fährt in Richtung des Endschalters (BACKWARD)
    move_stepper_until_button_pressed(direction=cfg.STEPPER_BACKWARD) 

    # 2. Zurückfahren auf die Warteposition (2400 Schritte)
    print(f"--- 2. Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")
    
    # Nutze die zentrale move_steps Funktion 
    fill.move_steps(WAITING_STEPS) 
    
    # 3. Aktuelle Position speichern
    fill.set_current_position(WAITING_STEPS)
    print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    # 4. Bereinigung der Stepper-Pins
    fill.gpio_cleanup()


# -----------------------------------
# --- 4. CLEANUP-FUNKTION ---
# -----------------------------------

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
        _button = None # Setze zurück

    # 2. Globales Cleanup für Stepper/Factory aufrufen (falls nötig)
    fill.gpio_cleanup()
    _factory = None # Setze Factory zurück


# -----------------------------------
# --- 5. HAUPTPROGRAMM (Manueller Start) ---
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