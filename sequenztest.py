import RPi.GPIO as GPIO
import time

# --- 1. GLOBALE KONFIGURATION ---

# Steppermotor Pins (A4988-Treiber)
STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21
DELAY = 0.002 # Verzögerung für den Stepper (sollte Ruckeln minimieren)
STEPS_PER_REVOLUTION = 200 # Schritte für 1 volle Umdrehung

# Servo Pins (Liste der 8 GPIO-Pins)
SERVO_PINS = [26, 19, 13, 6, 5, 17, 27, 22]
FREQ = 50  # PWM-Frequenz für Servos (50 Hz)

# -----------------------------------
# --- 2. GPIO SETUP ---
# -----------------------------------

# Warnungen unterdrücken, um flüssigen Start zu gewährleisten
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

# Stepper Pins als Output
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)

# Alle Servo Pins als Output initialisieren
for pin in SERVO_PINS:
    GPIO.setup(pin, GPIO.OUT)

# PWM-Objekte für jeden Servo erstellen und starten (Duty Cycle 0)
pwm_servos = {}
for pin in SERVO_PINS:
    pwm = GPIO.PWM(pin, FREQ)
    pwm.start(0)
    pwm_servos[pin] = pwm
    
# Steppermotor am Anfang deaktivieren
GPIO.output(ENABLE_PIN, GPIO.HIGH)
print("Initialisierung abgeschlossen. Start bereit.")

# -----------------------------------
# --- 3. HELPER-FUNKTIONEN ---
# -----------------------------------

def set_servo_angle(pwm_object, angle):
    """Konvertiert den Winkel in den Duty Cycle und bewegt den Servo."""
    # Duty Cycle: DC = (Winkel / 18.0) + 2.5
    duty_cycle = (angle / 18.0) + 2.5
    
    # Bewege den Servo
    pwm_object.ChangeDutyCycle(duty_cycle)
    # Wartezeit für die Bewegung (je nach Servo)
    time.sleep(0.5) 
    
    # Signal auf 0 setzen, um Rauschen im Stillstand zu vermeiden (optional, aber empfohlen)
    pwm_object.ChangeDutyCycle(0) 

def move_stepper(steps, direction):
    """Bewegt den Stepper und deaktiviert ihn anschließend."""
    print(f"-> Stepper: Bewege {steps} Schritte.")
    
    # Motor aktivieren
    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, direction) 
    time.sleep(0.005) # Kurze Zeit, um den Treiber zu stabilisieren
    
    # Schritte ausführen
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY)
        
    # Motor deaktivieren, um Haltestrom und Geräusche zu eliminieren
    GPIO.output(ENABLE_PIN, GPIO.HIGH)
    time.sleep(0.1)
    print("-> Stepper: Deaktiviert.")


# -----------------------------------
# --- 4. HAUPTPROGRAMM / SEQUENZ ---
# -----------------------------------

try:
    # Die Sequenz soll so oft durchlaufen, wie Servos vorhanden sind (8 Durchläufe)
    # Wir iterieren direkt über die Pin-Nummern
    for i, pin in enumerate(SERVO_PINS):
        pwm_obj = pwm_servos[pin]
        
        print("\n" + "="*40)
        print(f"START DURCHLAUF {i+1} von {len(SERVO_PINS)}")
        
        # TEIL 1: Stepper-Bewegung
        move_stepper(STEPS_PER_REVOLUTION, True) # 200 Schritte vorwärts
        
        # TEIL 2: Servo-Bewegung (0 -> 90 -> 0)
        print(f"-> Servo: Steuere Pin {pin}")
        
        # 0 Grad anfahren
        set_servo_angle(pwm_obj, 0) 
        time.sleep(0.5) # Kurze Pause an 0 Grad
        
        # 90 Grad anfahren
        set_servo_angle(pwm_obj, 90)
        time.sleep(1.0) # Halten auf 90 Grad
        
        # Zurück zu 0 Grad
        set_servo_angle(pwm_obj, 0)
        time.sleep(0.5) # Kurze Pause an 0 Grad
        
    print("\n" + "="*40)
    print("SEQUENZ ABGESCHLOSSEN.")

except KeyboardInterrupt:
    print("\nProgramm gestoppt durch Benutzer (Strg+C).")

finally:
    print("Führe GPIO-Cleanup aus.")
    
    # 5. AUFRÄUMEN
    
    # Alle PWM-Signale für Servos stoppen
    for pwm in pwm_servos.values():
        pwm.stop()
        
    # Steppermotor-Treiber sicher deaktivieren (falls nicht schon geschehen)
    GPIO.output(ENABLE_PIN, GPIO.HIGH)
    
    # Alle Pins in den sicheren Zustand zurücksetzen
    #GPIO.cleanup()