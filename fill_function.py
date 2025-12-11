import time
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory 
import sys

# Importiere die zentralen Module
import fill_function as fill 
import hardware_config as cfg

# --- 1. GLOBALE KONFIGURATION ---
STEP_PIN = cfg.STEPPER_PINS["STEP"]
DIR_PIN = cfg.STEPPER_PINS["DIR"]
ENABLE_PIN = cfg.STEPPER_PINS["EN"]
DELAY = cfg.STEP_DELAY 

# Definierte Warteposition in Schritten von Home (Button) entfernt
WAITING_STEPS = 2400 # 8 * 300 Schritte

# Globale Variable für den Taster und die Factory
_button = None
_factory = None

# -----------------------------------
# --- 2. GERÄTE-SETUP ---
# -----------------------------------

try:
    # Starte die pigpio Factory
    _factory = PiGPIOFactory()

    # Taster initialisieren (Wir verwenden den festen Pull-Up von GPIO 2)
    # Taster wird als gedrückt erkannt, wenn das Signal auf LOW (GND) gezogen wird.
    _button = Button(BUTTON_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory) 
    
    print("Initialisierung abgeschlossen. Start bereit.")

except Exception as e:
    print(f"Fehler bei der Initialisierung: {e}")
    sys.exit(1)


# -----------------------------------
# --- 3. HOMING-HELPER ---
# -----------------------------------

def move_stepper_until_button_pressed(direction=False):
    """
    Bewegt den Steppermotor mit Ramping, bis der Taster gedrückt wird.
    """
    
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
    
    # 0. Setup der Stepper-Pins über fill_function
    fill._setup_driver() 
    
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
    # KORREKTUR: Ruft die neue Cleanup-Funktion auf, damit fill._setup_driver() später wieder funktioniert.
    fill.gpio_cleanup()


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
            # Dies fängt den Fehler ab, den Sie zuvor hatten, falls das Closing nicht perfekt ist
            pass 

    # 2. Globales Cleanup für Stepper/Factory aufrufen (falls nötig)
    fill.gpio_cleanup()


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