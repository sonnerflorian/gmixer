from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

factory = PiGPIOFactory()
# Gib hier den Pin des Servos ein, den du gerade kalibrieren willst
PIN = 19 

# Wir starten mit den Standard-Pulsweiten
servo = Servo(PIN, min_pulse_width=0.0001, max_pulse_width=0.0025, pin_factory=factory)

print(f"Kalibrierung für Pin {PIN}")
print("Steuerung: 'a' = +0.05, 's' = -0.05 | 'd' = +0.01, 'f' = -0.01")
print("Drücke 'q' zum Beenden und Anzeigen des finalen Werts.")

current_val = 0.0
servo.value = current_pos = 0.0

try:
    while True:
        key = input(f"Aktueller Wert: {current_val:.2f} -> Kommando: ")
        if key == 'a': current_val += 0.05
        elif key == 's': current_val -= 0.05
        elif key == 'd': current_val += 0.01
        elif key == 'f': current_val -= 0.01
        elif key == 'q': break
        
        # Begrenzung auf gültigen Bereich
        current_val = max(-1.0, min(1.0, current_val))
        servo.value = current_val

except KeyboardInterrupt:
    pass

print(f"\nFinaler Kalibrierungswert für diesen Punkt: {current_val:.2f}")
servo.detach()