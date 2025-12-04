import RPi.GPIO as GPIO
import time

SERVO_PIN = 13   # GPIO13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM mit 50 Hz erzeugen
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    # Umrechnung: 0° = ca. 2.5% Duty, 180° = ca. 12.5%
    duty = 2.5 + (angle / 180.0) * 10
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # kurze Zeit, damit der Servo ankommt

try:
    print("Fahre auf 0° …")
    set_angle(0)

    print("Fahre auf 10° …")
    set_angle(10)

    time.sleep(1)

    print("Zurück auf 0° …")
    set_angle(0)

finally:
    pwm.stop()
    GPIO.cleanup()
