import RPi.GPIO as GPIO
import time

DIR, STEP, EN = 16, 20, 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.LOW)     # Treiber aktiv
GPIO.output(DIR, GPIO.HIGH)   # Richtung vorwärts

delay = 0.005   # 5 ms -> 100 Schritte pro Sekunde
steps = 4000

print("Starte Motorbewegung...")

try:
    # Vorwärts
    for _ in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

    # kurze Pause
    time.sleep(0.5)

    # Rückwärts
    GPIO.output(DIR, GPIO.LOW)

    for _ in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

finally:
    GPIO.output(EN, GPIO.HIGH)  # Treiber deaktivieren
    GPIO.cleanup()