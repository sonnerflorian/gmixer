import RPi.GPIO as GPIO
import time

servoPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)


def set_angle(pwm, angle, settle=0.4):
  # 0° ≈ 2%, 180° ≈ 12% (Faustregel)
  duty = max(2, min(12, 2 + angle / 18))
  pwm.ChangeDutyCycle(duty)
  time.sleep(settle)
  pwm.ChangeDutyCycle(0)


p = GPIO.PWM(servoPIN, 50) # GPIO 17 als PWM mit 50Hz
p.start(0) # Initialisierung

set_angle(p, 0)
time.sleep(0.5)
# set_angle(p, 10)
# time.sleep(0.5)

GPIO.cleanup()

