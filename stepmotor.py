import RPi.GPIO as GPIO, time

DIR, STEP, EN = 16, 20, 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)     # aktiv
GPIO.output(DIR, GPIO.HIGH)   # Richtung

delay = 0.002
steps = 200

print("Starte Motorbewegung...")


for _ in range(steps):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(delay)

GPIO.output(DIR, GPIO.LOW)
time.sleep(0.5)

for _ in range(steps):
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(delay)

# finally:
#     GPIO.output(EN, GPIO.HIGH)  # deaktivieren
#     GPIO.cleanup()
