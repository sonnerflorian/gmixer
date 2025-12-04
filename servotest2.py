from gpiozero import AngularServo
import time

servo = AngularServo(13, min_pulse_width=0.0006, max_pulse_width=0.0023)

while True:
    print("Stelle Servo auf -1 (0°)")
    servo.angle = 90
    time.sleep(2)

    print("Stelle Servo auf 1 (180°)")
    servo.angle = 0
    time.sleep(2)

    print("Stelle Servo auf -1 (0°)")
    servo.angke = -90
    time.sleep(2)