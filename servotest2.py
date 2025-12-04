from gpiozero import Servo
import time

servo = Servo(13, min_pulse_width=0.0005, max_pulse_width=0.0025)

while True:
    print("Stelle Servo auf -1 (0°)")
    servo.value = -1
    time.sleep(2)

    print("Stelle Servo auf 1 (180°)")
    servo.value = 0
    time.sleep(2)

    print("Stelle Servo auf -1 (0°)")
    servo.value = 1
    time.sleep(2)