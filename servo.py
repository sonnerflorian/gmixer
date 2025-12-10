import RPi.GPIO as GPIO
import time

SERVO_PIN = 16   # BCM-Nummer
FREQ = 50        # Hz, typisch für Servos

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, FREQ)
pwm.start(0)

def set_angle(angle: float, settle: float = 0.4):
    # Duty-Cycle grob: 0° ≈ 2%, 180° ≈ 12%
    duty = max(2, min(12, 2 + angle / 18))
    pwm.ChangeDutyCycle(duty)
    time.sleep(settle)
    pwm.ChangeDutyCycle(0)

try:
    current = 5
    print("Starte bei 5°")
    set_angle(current)
    while True:
        current = 10 if current == 5 else 5
        print(f"Stelle Servo auf {current}°")
        set_angle(current)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nBeende Programm …")
finally:
    pwm.stop()
    GPIO.cleanup()
