import RPi.GPIO as GPIO
import time

SERVO_PIN = 13  # GPIO13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 50 Hz Servo-PWM
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Diese Werte kannst du ggf. anpassen:
MIN_DUTY = 3.0   # ca. 0°   (falls zu weit links/rechts -> leicht ändern)
MAX_DUTY = 11.0  # ca. 180°

def angle_to_duty(angle):
    # Begrenzen, falls aus Versehen was Größeres reinkommt
    angle = max(0, min(180, angle))
    duty = MIN_DUTY + (angle / 180.0) * (MAX_DUTY - MIN_DUTY)
    return duty

def set_angle(angle):
    duty = angle_to_duty(angle)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.4)       # Zeit geben zum Fahren
    pwm.ChangeDutyCycle(0)  # PWM „loslassen“, reduziert Zappeln

try:
    print("Auf 0°")
    set_angle(0)

    print("Auf 10°")
    set_angle(10)

    time.sleep(1)

    print("Zurück auf 0°")
    set_angle(0)

finally:
    pwm.stop()
    GPIO.cleanup()

