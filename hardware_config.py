import RPi.GPIO as GPIO

STEPPER_PINS = {"DIR": 16, "STEP": 20, "EN": 21}
STEPPER_FORWARD = GPIO.HIGH      # Richtung zum Endschalter
STEPPER_BACKWARD = GPIO.LOW      # Richtung weg vom Endschalter
STEP_DELAY = 0.001               # 1 ms

SWITCH_PIN = 17
SWITCH_PULL = "UP"               # "UP" oder "DOWN"
SWITCH_ACTIVE_STATE = GPIO.LOW   # LOW = gedrückt

# Servo-Pins je Getränk (BCM)
SERVO_PINS = {
    "Apfelsaft": 18,
    "Wasser": 23,
    "Johannisbeere": 27,
    # "Getränk4": 23,
    # "Getränk5": 18,
    # "Getränk6": 22,
    # "Getränk7": 27,
    # "Getränk8": 23,
}

DRINK_POSITIONS = {
    "Apfelsaft": 0,
    "Wasser": 800,
    "Johannisbeere": 1600,
    # "Getränk4": 1200,
    # "Getränk5": 2000,
    # "Getränk6": 2400,
    # "Getränk7": 2800,
    # "Getränk8": 3200,
}
