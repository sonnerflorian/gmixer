import time
import sys
from gpiozero import OutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory 
import hardware_config as cfg

# Konfiguration aus hardware_config
PINS = cfg.STEPPER_PINS
DRINK_POSITIONS = cfg.DRINK_POSITIONS
SERVO_PINS = cfg.SERVO_PINS
STEP_DELAY = cfg.STEP_DELAY
current_position = 0

# Globale Variablen für gpiozero Objekte (Stepper-Pins und Factory)
_factory = None
_dir_pin = None
_step_pin = None
_en_pin = None
_gpio_devices = [] 

def set_current_position(position_steps: int = 0):
    global current_position
    current_position = position_steps

def _setup_driver():
    """Initialisiert die GPIO-Geräte mit PiGPIOFactory, falls noch nicht geschehen."""
    global _factory, _dir_pin, _step_pin, _en_pin, _gpio_devices
    
    if _factory is not None:
        return 

    try:
        _factory = PiGPIOFactory()
        
        # Stepper Pins
        _dir_pin = OutputDevice(PINS["DIR"], pin_factory=_factory)
        _step_pin = OutputDevice(PINS["STEP"], pin_factory=_factory)
        _en_pin = OutputDevice(PINS["EN"], pin_factory=_factory)
        
        # Liste für späteres Schließen füllen
        _gpio_devices.extend([_dir_pin, _step_pin, _en_pin])

        # Aktivieren des Treibers (EN=LOW in A4988)
        _en_pin.off() 
        print("Driver setup successful.")
    except Exception as e:
        print(f"Fehler im Setup von fill_function: {e}")
        # Wenn der Fehler auftritt, sofort aufräumen
        gpio_cleanup()
        raise


def gpio_cleanup():
    """
    Führt ein sauberes Herunterfahren aller Stepper/Factory-Ressourcen durch.
    Wird von initialisation_stepper und main.py aufgerufen.
    """
    global _gpio_devices, _factory, _en_pin, _dir_pin, _step_pin
    
    if _factory is None:
        return 

    print("Führe fill_function GPIO Cleanup aus...")
    
    if _en_pin is not None:
        _en_pin.on() # Treiber deaktivieren (Sicherheit)
    
    # Alle Geräte explizit schließen
    for device in _gpio_devices:
        if device is not None:
            try:
                device.close()
            except Exception:
                pass
                
    # Globale Zustände zurücksetzen
    _gpio_devices = []
    _factory = None
    _dir_pin = _step_pin = _en_pin = None
    print("Cleanup abgeschlossen.")


def _raw_step(delay):
    """Erzeugt einen einzelnen Schrittpuls mit variablem Delay (für Ramping)."""
    if _step_pin is None:
        raise Exception("Stepper-Pins nicht initialisiert. SetupDriver() fehlt.")
        
    _step_pin.on()
    time.sleep(delay)
    _step_pin.off()
    time.sleep(delay)


def _step_once():
    """Erzeugt einen einzelnen Schrittpuls mit fixem Delay."""
    # Ruft _raw_step mit dem konfigurierten Delay auf
    _raw_step(STEP_DELAY)

def move_steps(delta_steps: int):
    """Bewegt den Stepper um delta_steps (negativ = Backward)."""
    global current_position
    if delta_steps == 0:
        return
        
    _setup_driver() # Muss immer vor Bewegung initialisiert werden
        
    # Richtung setzen
    direction = cfg.STEPPER_FORWARD if delta_steps > 0 else cfg.STEPPER_BACKWARD
    _dir_pin.value = direction 
    
    # Schritte ausführen
    for _ in range(abs(delta_steps)):
        _step_once()
        
    current_position += delta_steps

# ... (move_to_position und move_to_drink bleiben gleich) ...

def move_to_position(target_steps: int):
    move_steps(target_steps - current_position)

def move_to_drink(drink_name: str):
    if drink_name not in DRINK_POSITIONS:
        raise KeyError(f"Unbekanntes Getränk: {drink_name}")
    
    _setup_driver() 
    try:
        move_to_position(-DRINK_POSITIONS[drink_name])
    finally:
        pass 

def pour_with_servo(servo_pin: int, forward_angle: float = 180, dwell: float = 0.5):
    """Steuert das Servo-Ventil für eine bestimmte Dauer."""
    
    _setup_driver() # Stellt sicher, dass die Factory läuft
    servo = None
    
    try:
        # Initialisiere das Servo mit der Factory
        servo = Servo(servo_pin, pin_factory=_factory)
        
        # Servo öffnen (Angle-to-Value Konvertierung)
        servo_value = (forward_angle / 90.0) - 1.0 
        
        servo.value = servo_value
        time.sleep(0.3)
        time.sleep(dwell)
        
        # Servo schließen
        servo.min() 
        time.sleep(0.3)
        
    finally:
        if servo is not None:
            servo.detach() 
            servo.close()