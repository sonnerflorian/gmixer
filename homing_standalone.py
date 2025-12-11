import time
import sys
from gpiozero import OutputDevice, Button
from gpiozero.pins.pigpio import PiGPIOFactory 

# --- 1. HARCODED KONFIGURATION (ersetzt hardware_config.py) ---

# Steppermotor Pins (BCM)
DIR_PIN = 20
STEP_PIN = 16
ENABLE_PIN = 21

# Taster-Pin (Endschalter)
BUTTON_PIN = 2 # GPIO 2 hat festen Pull-Up

# Bewegungs-Konstanten
STEPPER_FORWARD = True      # Richtung weg von Home/zum Endschalter
STEPPER_BACKWARD = False    # Richtung zu Home/vom Endschalter
STEP_DELAY = 0.001          # Ziel-Geschwindigkeit (1 ms)
WAITING_STEPS = 2500        # Schritte von Home entfernt

# --- 2. GLOBALE GERÄTE VARIABLEN ---
_factory = None
_button = None
_dir_pin = None
_step_pin = None
_en_pin = None

# -----------------------------------
# --- 3. SETUP / CLEANUP FUNKTIONEN ---
# -----------------------------------

def _setup_devices():
    """Initialisiert alle GPIO-Geräte (Stepper und Button)."""
    global _factory, _button, _dir_pin, _step_pin, _en_pin
    
    if _factory is not None:
        return True

    try:
        _factory = PiGPIOFactory()
        
        # Stepper Pins
        _dir_pin = OutputDevice(DIR_PIN, pin_factory=_factory)
        _step_pin = OutputDevice(STEP_PIN, pin_factory=_factory)
        _en_pin = OutputDevice(ENABLE_PIN, pin_factory=_factory)
        
        # Taster (Pull-Up, LOW = gedrückt)
        _button = Button(BUTTON_PIN, pull_up=True, pin_factory=_factory) 
        
        _en_pin.on() # Stepper deaktivieren (HIGH = AUS)

        print("Hardware-Setup erfolgreich.")
        return True

    except Exception as e:
        print(f"Fehler beim Setup der Geräte: {e}")
        gpio_cleanup()
        sys.exit(1)

def gpio_cleanup():
    """Schließt alle GPIO-Ressourcen."""
    global _factory, _button, _dir_pin, _step_pin, _en_pin

    if _en_pin is not None:
        _en_pin.on()
        
    for device in [_button, _dir_pin, _step_pin, _en_pin]:
        if device is not None:
            try:
                device.close()
            except Exception:
                pass 
                
    _factory = None
    print("Cleanup abgeschlossen.")


# -----------------------------------
# --- 4. MOVEMENT FUNKTIONEN ---
# -----------------------------------

def _raw_step(delay):
    """Erzeugt einen einzelnen Schrittpuls mit variablem Delay (für Ramping)."""
    _step_pin.on()
    time.sleep(delay)
    _step_pin.off()
    time.sleep(delay)

def _ramp_move_until_pressed():
    """Bewegt den Stepper mit Ramping, bis der Taster gedrückt wird."""
    
    START_DELAY = 0.005    
    TARGET_DELAY = STEP_DELAY 
    ACCEL_RATE = 0.999     
    current_delay = START_DELAY
    
    if _button.is_pressed:
        print("Taster ist bereits geschlossen.")
        return

    print(f"\n--- STARTE HOME-SUCHE (Richtung: Rückwärts) ---")
    
    _en_pin.off()
    _dir_pin.value = STEPPER_BACKWARD 
    time.sleep(0.005) 
    
    while not _button.is_pressed:
        
        _raw_step(current_delay)
        
        if current_delay > TARGET_DELAY:
            current_delay *= ACCEL_RATE 
            current_delay = max(current_delay, TARGET_DELAY) 

    print("\n\n*** HOME-POSITION ERREICHT (Position 0) ***")
    _en_pin.on()
    time.sleep(0.1)

def move_steps(steps: int, direction: bool):
    """Bewegt den Stepper um eine feste Anzahl Schritte."""
    if steps == 0:
        return

    print(f"-> Stepper: Bewege {steps} Schritte.")
    
    _en_pin.off()
    _dir_pin.value = direction 
    time.sleep(0.005)
    
    for _ in range(abs(steps)):
        _raw_step(STEP_DELAY) # Nutze das fixe Target-Delay

    _en_pin.on()
    time.sleep(0.1)


# -----------------------------------
# --- 5. HAUPT-HOMING FUNKTION ---
# -----------------------------------

def home_stepper():
    """Führt Homing durch (0) und fährt zur Warteposition (2400)."""
    
    if _setup_devices() is None:
        return 

    try:
        # 1. Homing: Fährt in Richtung des Endschalters
        _ramp_move_until_pressed() 

        # 2. Zurückfahren auf die Warteposition (2400 Schritte)
        print(f"--- Fahren zur Warteposition ({WAITING_STEPS} Schritte) ---")
        
        # Fährt zur Warteposition (Richtung FORWARD)
        move_steps(WAITING_STEPS, STEPPER_FORWARD) 
        
        print(f"*** WARTEPOSITION BEI {WAITING_STEPS} SCHRITTEN ERREICHT. ***")

    except Exception as e:
        print(f"Fehler während der Homing-Routine: {e}")
        # Wir überlassen das Cleanup dem finally Block
        raise 
    finally:
        # Cleanup wird im __main__ Block aufgerufen, um alles sauber zu beenden
        pass
        

# -----------------------------------
# --- 6. MANUELLER START (TEST) ---
# -----------------------------------

if __name__ == "__main__":
    print("Starte manuelle Home-Suche (Standalone)...")
    
    try:
        home_stepper()
    except KeyboardInterrupt:
        print("\nRoutine gestoppt durch Benutzer (Strg+C).")
    finally:
        # Führt das Cleanup für alle internen Geräte aus
        gpio_cleanup()
        print("Manuelle Initialisierung beendet.")