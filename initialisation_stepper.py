import time
import sys
from gpiozero import OutputDevice, Button
from gpiozero.pins.pigpio import PiGPIOFactory 

# Importiere die zentralen Module
import fill_function as fill 
import hardware_config as cfg

# --- Globale Konstanten ---
WAITING_STEPS = 2400 # 8 * 300 Schritte

# Globale Variable für den Taster und die Factory (Initialisierung wird verzögert)
_button = None
_factory = None

# -----------------------------------
# --- 1. SETUP FUNKTION ---
# -----------------------------------

def _setup_local_devices():
    """Initialisiert Button und Factory, falls noch nicht geschehen."""
    global _factory, _button
    
    if _button is not None:
        return # Bereits initialisiert

    try:
        # Starte Factory
        _factory = PiGPIOFactory()

        # Taster initialisieren: Verwende cfg-Werte direkt, um NameError zu umgehen
        _button = Button(cfg.SWITCH_PIN, pull_up=cfg.SWITCH_PULL, pin_factory=_factory) 
        
        # Stellt sicher, dass die Stepper-Pins in fill_function initialisiert sind
        fill._setup_driver() 
        fill._en_pin.on() # Stepper am Anfang deaktivieren

        print("Taster- und Stepper-Initialisierung erfolgreich.")
        return True

    except Exception as e:
        print(f"Fehler bei der Hardware-Initialisierung: {e}")
        # Ruft fill_function cleanup auf, falls Stepper-Pins initialisiert wurden
        fill.gpio_cleanup() 
        sys.exit(1)


# -----------------------------------
# --- 2. MOVEMENT LOGIC (RAMPING) ---
# -----------------------------------

def _ramp_move_until_pressed():
    """Bewegt den Stepper mit Ramping, bis der Taster gedrückt wird."""
    
    # Ramping-Konstanten
    START_DELAY = 0.005    
    TARGET_DELAY = cfg.STEP_DELAY # Ziel-Delay aus hardware_config
    ACCEL_RATE = 0.999     
    current_delay = START_DELAY
    
    # 1. Startprüfung
    if _button.is_pressed:
        print("Taster ist bereits geschlossen. Home-Position gefunden.")
        return

    print(f"\n--- STARTE HOME-SUCHE (Richtung: {'Rückwärts'}) ---")
    
    # 2. Motor aktivieren und Richtung setzen
    fill._en_pin.off()
    fill._dir_pin.value = cfg.STEPPER_BACKWARD 
    time.sleep(0.005) 
    
    # 3. Endlosschleife mit Beschleunigung
    while not _button.is_pressed:
        
        fill._step_pin.on() 
        time.sleep(current_delay)
        
        fill._step_pin.off()
        time.sleep(current_delay)
        
        # Beschleunigung
        if current_delay > TARGET_DELAY:
            current_delay *= ACCEL_RATE 
            current_delay = max(current_delay, TARGET_DELAY) 

    # 4. Ende
    print("\n\n*** HOME-POSITION ERREICHT UND MOTOR GESTOPPT! ***")
    fill._en_pin.on()
    time.sleep(0.1)


# -----------------------------------
# --- 3. HAUPT-HOMING FUNKTION ---
# -----------------------------------

def home_stepper():
    """Führt Homing durch und fährt zur Warteposition."""
    
    # Setup muss zuerst erfolgen
    if _setup_local_devices() is None:
        return # Initialisierung fehlgeschlagen

    # 1. Homing: Fährt in Richtung des Endschalters (BACKWARD)
    _ramp_move_until_pressed() 

    # 2. Zurückfahren auf die Warteposition (2400 Schritte)
    print(f"--- 2. Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")
    
    # Nutze die zentrale move_steps Funktion 
    fill.move_steps(WAITING_STEPS) 
    
    # 3. Aktuelle Position speichern
    fill.set_current_position(WAITING_STEPS)
    print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    # 4. Bereinigung (Steuerung wird an main.py zurückgegeben)
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
        _button = None

    # 2. Globales Cleanup für Stepper/Factory aufrufen
    fill.gpio_cleanup()
    _factory = None 


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