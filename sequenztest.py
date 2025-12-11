import time
from gpiozero import OutputDevice, Servo 
# Importiere die empfohlene Factory für stabileres PWM und Timing
from gpiozero.pins.pigpio import PiGPIOFactory 

# --- 1. GLOBALE KONFIGURATION ---

STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21
DELAY = 0.002 # Verzögerung zwischen Pulsen (in Sekunden)
STEPS_PER_REVOLUTION = 200

SERVO_PINS = [26, 19, 13, 6, 5, 10, 27, 22]

# -----------------------------------
# --- 2. GERÄTE-SETUP ---
# -----------------------------------

# Instanz der PiGPIOFactory erstellen und als Standard setzen
factory = PiGPIOFactory()

# Stepper-Geräte initialisieren (Alle müssen die Factory verwenden)
dir_pin = OutputDevice(DIR_PIN, pin_factory=factory)
enable_pin = OutputDevice(ENABLE_PIN, pin_factory=factory)
step_pin = OutputDevice(STEP_PIN, pin_factory=factory) 

# Servo-Geräte initialisieren
servos = {}
for pin in SERVO_PINS:
    # Übergebe die Factory an jedes Servo-Objekt
    servos[pin] = Servo(pin, pin_factory=factory) 
    servos[pin].detach() 
    
enable_pin.on() # Stepper deaktivieren (HIGH = AUS)
print("Initialisierung abgeschlossen. Geräte bereit.")

# -----------------------------------
# --- 3. HELPER-FUNKTIONEN ---
# -----------------------------------

def set_servo_angle(servo_obj, angle):
    """Bewegt den Servo zu einem Winkel und deaktiviert das Signal wieder."""
    value = (angle / 90.0) - 1.0
    servo_obj.value = value
    time.sleep(0.5) 
    servo_obj.detach() 

def move_stepper(steps, direction):
    """Bewegt den Stepper mit manueller HIGH/LOW-Schleife und deaktiviert ihn."""
    print(f"-> Stepper: Bewege {steps} Schritte.")
    
    # 1. Motor aktivieren (enable_pin.off() setzt auf LOW)
    enable_pin.off()
    
    # 2. Richtung setzen 
    dir_pin.value = direction 
    time.sleep(0.005) 
    
    # 3. Schritte ausführen: MANUELLE HIGH/LOW-SCHLEIFE
    for _ in range(steps):
        # step_pin.on() entspricht GPIO.HIGH
        step_pin.on() 
        time.sleep(DELAY)
        
        # step_pin.off() entspricht GPIO.LOW
        step_pin.off()
        time.sleep(DELAY)
    
    # 4. Motor deaktivieren
    enable_pin.on()
    time.sleep(0.1)
    print("-> Stepper: Deaktiviert.")


# -----------------------------------
# --- 4. HAUPTPROGRAMM / SEQUENZ ---
# -----------------------------------

try:
    for i, pin in enumerate(SERVO_PINS):
        servo_obj = servos[pin]
        
        print("\n" + "="*40)
        print(f"START DURCHLAUF {i+1} von {len(SERVO_PINS)}")
        
        # TEIL 1: Stepper-Bewegung
        move_stepper(STEPS_PER_REVOLUTION, True) # 200 Schritte vorwärts
        
        # TEIL 2: Servo-Bewegung (0 -> 90 -> 0)
        print(f"-> Servo: Steuere Pin {pin}")
        
        set_servo_angle(servo_obj, 0) 
        time.sleep(0.5) 
        
        set_servo_angle(servo_obj, 90)
        time.sleep(1.0) 
        
        set_servo_angle(servo_obj, 0)
        time.sleep(0.5) 
        
    print("\n" + "="*40)
    print("SEQUENZ ABGESCHLOSSEN.")

except KeyboardInterrupt:
    print("\nProgramm gestoppt durch Benutzer (Strg+C).")

finally:
    print("Führe GPIO-Cleanup aus.")
    enable_pin.on()
    # gpiozero schließt alle Geräte automatisch