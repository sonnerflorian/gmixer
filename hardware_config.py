# gmixer/hardware_config.py

# Die Pins (BCM) bleiben gleich
STEPPER_PINS = {"DIR": 16, "STEP": 20, "EN": 21}

# NEU: Boolesche Werte für die Richtung (True/False)
# True/False wird von gpiozero OutputDevice(pin).value = direction verwendet.
STEPPER_FORWARD = True      # Richtung zum Endschalter (muss zu Ihrer Verkabelung passen)
STEPPER_BACKWARD = False    # Richtung weg vom Endschalter
STEP_DELAY = 0.001          # 1 ms

# Taster-Konfiguration (für gpiozero Button)
SWITCH_PIN = 2               
# NEU: Wir nutzen den festen Pull-Up von GPIO 2
SWITCH_PULL = True           
# LOW (False) = gedrückt, da der Taster mit GND verbunden ist
SWITCH_ACTIVE_STATE = False  

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