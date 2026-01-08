# gmixer/hardware_config.py

# Die Pins (BCM) bleiben gleich
STEPPER_PINS = {"DIR": 20, "STEP": 16, "EN": 21}

# NEU: Boolesche Werte für die Richtung (True/False)
# True/False wird von gpiozero OutputDevice(pin).value = direction verwendet.
STEPPER_FORWARD = True      # Richtung zum Endschalter (muss zu Ihrer Verkabelung passen)
STEPPER_BACKWARD = False    # Richtung weg vom Endschalter
STEP_DELAY = 0.0005          # 1 ms

# Taster-Konfiguration (für gpiozero Button)
SWITCH_PIN = 2               
# NEU: Wir nutzen den festen Pull-Up von GPIO 2
SWITCH_PULL = True           
# LOW (False) = gedrückt, da der Taster mit GND verbunden ist
SWITCH_ACTIVE_STATE = False  
