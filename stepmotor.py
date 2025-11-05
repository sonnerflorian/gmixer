import RPi.GPIO as GPIO
import time

# Pin-Definitionen
DIR = 16     # Drehrichtung
STEP = 20    # Schrittimpuls
EN = 21      # Enable

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

# Treiber aktivieren (LOW = an)
GPIO.output(EN, GPIO.LOW)

# Richtung einstellen (True oder False)
GPIO.output(DIR, GPIO.HIGH)  # HIGH = vorwärts, LOW = rückwärts

# Parameter
steps = 200          # Anzahl der Schritte (z. B. 200 = 1 Umdrehung bei 1,8°/Step)
delay = 0.001        # Schrittgeschwindigkeit (Sekunden zwischen Impulsen)

print("Starte Motorbewegung...")

try:
    for i in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

    # Richtung wechseln
    GPIO.output(DIR, GPIO.LOW)
    time.sleep(1)

    for i in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

except KeyboardInterrupt:
    print("\nBeende Programm...")

finally:
    # Treiber deaktivieren
    GPIO.output(EN, GPIO.HIGH)
    GPIO.cleanup()
