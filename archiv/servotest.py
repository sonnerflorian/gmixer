#!/usr/bin/env python3
"""
360° Servo (continuous rotation) control with pigpio.

Wiring (typical):
- Servo V+  -> 5V extern (NICHT vom Pi speisen bei Last)
- Servo GND -> GND extern UND GND vom Pi verbinden (gemeinsame Masse!)
- Servo SIG -> GPIO (z.B. GPIO18)

Controls:
- speed: -1.0 .. +1.0   (negativ = links, positiv = rechts)
- stop at 0.0
"""

import time
import pigpio

GPIO_SERVO = 26          # Signal-Pin (BCM Nummer)
CENTER_US  = 1500        # Stop (ggf. kalibrieren: 1470-1530)
RANGE_US   = 400         # Maximaler Ausschlag (z.B. 300-500)

def set_speed(pi: pigpio.pi, gpio: int, speed: float,
              center_us: int = CENTER_US, range_us: int = RANGE_US) -> int:
    """Set continuous servo speed in [-1, +1]. Returns used pulsewidth (µs)."""
    speed = max(-1.0, min(1.0, float(speed)))
    pulse = int(center_us + speed * range_us)
    pi.set_servo_pulsewidth(gpio, pulse)
    return pulse

def stop(pi: pigpio.pi, gpio: int):
    pi.set_servo_pulsewidth(gpio, CENTER_US)

def main():
    pi = pigpio.pi()
    if not pi.connected:
        raise SystemExit("pigpio daemon läuft nicht. Starte ihn mit: sudo systemctl start pigpiod")

    try:
        print("360° Servo Test: links -> stop -> rechts -> stop")
        print("Hinweis: CENTER_US ggf. anpassen, bis der Servo bei speed=0 wirklich steht.\n")

        # langsam links
        pw = set_speed(pi, GPIO_SERVO, -0.3)
        print(f"links  (speed=-0.3)  pulse={pw}µs")
        time.sleep(2)

        # stop
        stop(pi, GPIO_SERVO)
        print(f"stop               pulse={CENTER_US}µs")
        time.sleep(2)

        # schneller rechts
        pw = set_speed(pi, GPIO_SERVO, +0.7)
        print(f"rechts (speed=+0.7) pulse={pw}µs")
        time.sleep(2)

        # stop
        stop(pi, GPIO_SERVO)
        print(f"stop               pulse={CENTER_US}µs")
        time.sleep(1)

        print("\nFertig.")
    finally:
        # Servo auf Stop und pigpio sauber schließen
        stop(pi, GPIO_SERVO)
        time.sleep(0.2)
        pi.stop()

if __name__ == "__main__":
    main()
