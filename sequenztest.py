import time
# Importiere gpiozero Klassen
from gpiozero import OutputDevice, Servo
# Der Stepper wird hier als einfacher Pulsgeber und Richtungsausgabe behandelt
from gpiozero.tools import digital_thread

# --- 1. GLOBALE KONFIGURATION ---

# Steppermotor Pins (A4988-Treiber)
STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21
DELAY = 0.002 # Verzögerung zwischen Pulsen (in Sekunden)
STEPS_PER_REVOLUTION = 200 # Schritte für 1 volle Umdrehung

# Servo Pins (Liste der 8 GPIO-Pins)
SERVO_PINS = [26, 19, 13, 6, 5, 17, 27, 22]

# -----------------------------------
# --- 2. GERÄTE-SETUP (ersetzt GPIO.setup) ---
# -----------------------------------

# Stepper-Geräte initialisieren
# OutputDevice ist perfekt für DIR und ENABLE
dir_pin = OutputDevice(DIR_PIN)
enable_pin = OutputDevice(ENABLE_PIN)
step_pin = OutputDevice(STEP_PIN) # Wird später für die Puls-Funktion verwendet

# Servo-Geräte initialisieren
# Die Servo-Klasse kümmert sich um PWM (50Hz) und die Duty-Cycle-Berechnung
# Das Dictionary speichert die Servo-Objekte
servos = {}
for pin in SERVO_PINS:
    # Die gpiozero Servo Klasse nimmt standardmäßig 50Hz und konvertiert Winkel/Werte automatisch
    servos[pin] = Servo(pin) 
    # Setze Servo initial in den 'deaktivierten' Zustand (keine PWM-Pulse, kein Zittern)
    servos[pin].detach() 
    
# Steppermotor am Anfang deaktivieren (ENABLE ist hier eine boolesche Invertierung des OutputDevice)
# Bei A4988 ist LOW = AN, HIGH = AUS. OutputDevice(active_high=False) macht es einfacher.
enable_pin.on() # .on() setzt den Pin auf HIGH (Deaktiviert den Treiber)
print("Initialisierung abgeschlossen. Geräte bereit.")

# -----------------------------------
# --- 3. HELPER-FUNKTIONEN ---
# -----------------------------------

def set_servo_angle(servo_obj, angle):
    """Bewegt den Servo zu einem Winkel und deaktiviert das Signal wieder."""
    
    # 1. Servo aktivieren und Winkel setzen
    # gpiozero verwendet einen Wert von -1 (entspricht 0 Grad) bis +1 (entspricht 180 Grad)
    # Winkel 0 Grad -> Wert -1
    # Winkel 90 Grad -> Wert 0
    # Berechne den gpiozero-Wert: value = (angle / 90.0) - 1.0
    value = (angle / 90.0) - 1.0
    
    servo_obj.value = value
    time.sleep(0.5) # Wartezeit für die Bewegung
    
    # 2. Signal trennen (Deaktivieren) um Zittern zu vermeiden
    servo_obj.detach() 

def move_stepper(steps, direction):
    """Bewegt den Stepper und deaktiviert ihn anschließend."""
    print(f"-> Stepper: Bewege {steps} Schritte.")
    
    # 1. Motor aktivieren (enable_pin.off() setzt auf LOW)
    enable_pin.off()
    
    # 2. Richtung setzen (True/False wird automatisch auf HIGH/LOW abgebildet)
    dir_pin.value = direction 
    time.sleep(0.005) 
    
    # 3. Schritte ausführen: Nutzt die pulse-Methode von OutputDevice
    # Wir senden die halbe Anzahl der Pulse, da 'pulse' HIGH und LOW automatisch regelt.
    step_pin.pulse(
        n=steps, 
        duration=DELAY * 2, # Gesamtdauer eines HIGH-LOW-Zyklus
        background=False    # Blockiert, bis alle Pulse gesendet sind
    )

    # 4. Motor deaktivieren (enable_pin.on() setzt auf HIGH)
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
        
        # 0 Grad anfahren
        set_servo_angle(servo_obj, 0) 
        time.sleep(0.5) 
        
        # 90 Grad anfahren
        set_servo_angle(servo_obj, 90)
        time.sleep(1.0) 
        
        # Zurück zu 0 Grad
        set_servo_angle(servo_obj, 0)
        time.sleep(0.5) 
        
    print("\n" + "="*40)
    print("SEQUENZ ABGESCHLOSSEN.")

except KeyboardInterrupt:
    print("\nProgramm gestoppt durch Benutzer (Strg+C).")

finally:
    print("Führe GPIO-Cleanup aus.")
    
    # 5. AUFRÄUMEN (Mit gpiozero entfällt GPIO.cleanup())
    
    # Alle Geräte werden automatisch beendet/freigegeben, wenn das Skript endet.
    # Wir stellen nur sicher, dass der Stepper deaktiviert ist:
    enable_pin.on()
    
    # Die Geräte-Objekte werden beim Beenden des Skripts automatisch freigegeben (close()).