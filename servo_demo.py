import pigpio
import time

SERVO_PIN = 13

pi = pigpio.pi()      # Verbindung zum pigpiod-Daemon
if not pi.connected:
    exit()

def set_angle(angle):
    # Winkel -> Pulsweite (µs)
    pulse = 500 + (angle / 180.0) * 2000   # 500–2500 µs
    pi.set_servo_pulsewidth(SERVO_PIN, pulse)

try:
    print("0°")
    set_angle(0)
    time.sleep(1)

    print("10°")
    set_angle(10)
    time.sleep(1)

    print("Zurück 0°")
    set_angle(0)
    time.sleep(1)

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Servo aus
    pi.stop()