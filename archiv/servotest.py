from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

# 1. Setup
factory = PiGPIOFactory()
SERVO_PIN = 26

# Wir nutzen weite Pulsweiten, um sicherzustellen, dass wir 
# den vollen Geschwindigkeitsbereich erreichen.
servo = Servo(SERVO_PIN, 
              min_pulse_width=0.0000, 
              max_pulse_width=0.0030, 
              pin_factory=factory)

try:
    print("360° Servo Test an Pin 26 startet...")

    # Vorwärts drehen
    print("Drehe vorwärts (langsam)...")
    servo.value = 0.2
    time.sleep(2)

    print("Drehe vorwärts (schnell)...")
    servo.value = 1.2
    time.sleep(2)


finally:
    servo.close()
    print("Test beendet.")