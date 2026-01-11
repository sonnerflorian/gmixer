import time
from gpiozero import OutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory 

PINS = {"DIR": 20, "STEP": 16, "EN": 21}
STEP_DELAY = 0.0005   
current_position = 0
STEPPER_FORWARD = True
STEPPER_BACKWARD = False


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
        
        _dir_pin = OutputDevice(PINS["DIR"], pin_factory=_factory)
        _step_pin = OutputDevice(PINS["STEP"], pin_factory=_factory)
        _en_pin = OutputDevice(PINS["EN"], pin_factory=_factory)
        
        _gpio_devices.extend([_dir_pin, _step_pin, _en_pin])

        _en_pin.off() 
        print("Driver setup successful.")
    except Exception as e:
        print(f"Fehler im Setup von fill_function: {e}")
        gpio_cleanup()
        raise


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
    _raw_step(STEP_DELAY)
    

def move_steps(delta_steps: int):
    """
    Bewegt den Stepper um eine bestimmte Anzahl von Schritten (delta_steps).
    Aktiviert den Treiber vor der Bewegung und deaktiviert ihn danach.
    """
    global current_position, _en_pin
    
    if delta_steps == 0:
        return
        
    _setup_driver() 
    
    try:
        if _en_pin is not None:
            _en_pin.off() # Stepper aktivieren (LOW)
            time.sleep(0.005) # Kurze Pause zur Stabilisierung
            
        direction = STEPPER_FORWARD if delta_steps > 0 else STEPPER_BACKWARD
        _dir_pin.value = direction 
        
        for _ in range(abs(delta_steps)):
            _step_once()
            
        current_position += delta_steps
        
    finally:
        if _en_pin is not None:
            _en_pin.on()