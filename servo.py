import RPi.GPIO as GPIO
import time

servo_pin = 18  # <-- dein Anschluss

GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Hardware-PWM auf GPIO18: 50 Hz (typisch für Servos)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        for angle in [0, 90, 180, 90]:
            print(f"Stelle Servo auf {angle}°")
            set_angle(angle)
            time.sleep(1)
except KeyboardInterrupt:
    print("\nBeende Programm …")
    pwm.stop()
    GPIO.cleanup()
