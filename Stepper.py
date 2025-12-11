import RPi.GPIO as GPIO
import time

# 1. GPIO-Pin-Definitionen (BCM-Nummerierung)
STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21

# Schrittfrequenz: Wartezeit zwischen Pulsen in Sekunden.
# Kleinere Zahl = höhere Geschwindigkeit. 0.001s ist ein guter Start.
DELAY = 0.0001 

# Anzahl der Schritte für eine volle Umdrehung (meistens 200 bei Vollschritt-Modus)
STEPS_PER_REVOLUTION = 3200

# 2. GPIO-Einrichtung
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)

# Den Motor initialisieren (ENABLE auf LOW, um den Treiber zu aktivieren!)
# Der A4988 ist aktiv, wenn ENABLE LOW ist.
GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Zuerst deaktivieren
print(f"Treiber aktiviert (ENABLE: LOW an GPIO {ENABLE_PIN})")

# 3. Funktion zur Motorsteuerung
def move_stepper(steps, direction):
    """
    Bewegt den Schrittmotor um die angegebene Anzahl Schritte in eine Richtung.
    direction: True (vorwärts) oder False (rückwärts).
    """
    # 1. Richtung setzen
    # True für eine Richtung, False für die andere (je nach Verdrahtung)
    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, direction) 
    print(f"Setze Richtung: {'Vorwärts' if direction else 'Rückwärts'}")
    
    # 2. Schritte ausführen
    for _ in range(steps):
        # Schrittpuls HIGH (AN)
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY)
        
        # Schrittpuls LOW (AUS) - Muss kurz genug sein, um den Puls zu registrieren
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY)

    GPIO.output(ENABLE_PIN, GPIO.HIGH)
# 4. Hauptprogramm
try:
    print("-" * 30)
    # 200 Schritte vorwärts (1 Umdrehung)
    move_stepper(STEPS_PER_REVOLUTION, True)
    print("Bewegung 1 abgeschlossen. Warte 2 Sekunden...")
    time.sleep(5)
    
    # 200 Schritte rückwärts (1 Umdrehung)
    move_stepper(STEPS_PER_REVOLUTION, False)
    print("Bewegung 2 abgeschlossen.")
    print("-" * 30)

except KeyboardInterrupt:
    print("\nProgramm beendet durch Benutzer.")

finally:
    # 5. Aufräumarbeiten
    # Deaktiviere den Motor, um Energie zu sparen und das Halten aufzuheben
    GPIO.output(ENABLE_PIN, GPIO.HIGH) 
    print(f"Treiber deaktiviert (ENABLE: HIGH an GPIO {ENABLE_PIN})")
    delay(10)
    GPIO.cleanup()