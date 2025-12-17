import time
import sys
from gpiozero import OutputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# --- 1. KONFIGURATION (Hardcoded für Standalone) ---
STEP_PIN = 16 
DIR_PIN = 20
EN_PIN = 21

# Richtungen (Anpassen, falls er falsch herum fährt)
FORWARD = True  # Weg vom Button
BACKWARD = False # Zum Button

# Positionen in Schritten
POSITIONS = {
    "Johannisbeere": 0,    # Beispielwert
    "Wasser": 800,         # Beispielwert
    "start": 2400          # Warteposition
}

# Servo Pins
SERVO_PINS = {
    "Johannisbeere": 19, # Dein funktionierender Pin
    "Wasser": 23
}

STEP_DELAY = 0.001 
current_pos = 2400 # Startwert nach dem Homing

# --- 2. HARDWARE SETUP ---
factory = PiGPIOFactory()

# Stepper initialisieren
step_dev = OutputDevice(STEP_PIN, pin_factory=factory)
dir_dev = OutputDevice(DIR_PIN, pin_factory=factory)
en_dev = OutputDevice(EN_PIN, pin_factory=factory)

# Treiber standardmäßig deaktivieren
en_dev.on()

# --- 3. FUNKTIONEN ---

def move_to(target_steps):
    global current_pos
    delta = target_steps - current_pos
    if delta == 0:
        return

    print(f"Fahre zu {target_steps} (Delta: {delta})")
    
    # Treiber aktivieren
    en_dev.off()
    time.sleep(0.005)
    
    # Richtung setzen
    dir_dev.value = FORWARD if delta > 0 else BACKWARD
    
    # Schritte ausführen
    for _ in range(abs(delta)):
        step_dev.on()
        time.sleep(STEP_DELAY)
        step_dev.off()
        time.sleep(STEP_DELAY)
    
    # Treiber wieder deaktivieren (schont Motoren & reduziert Rauschen für Servos)
    en_dev.on()
    current_pos = target_steps
    time.sleep(0.1)

def pour(pin, dwell=0.7):
    print(f"Öffne Servo an Pin {pin}...")
    # Servo nur für den Gießvorgang initialisieren (verhindert Zappeln anderer Servos)
    servo = Servo(pin, pin_factory=factory)
    
    try:
        servo.max() # Öffnen
        time.sleep(dwell)
        servo.min() # Schließen
        time.sleep(0.3)
    finally:
        servo.detach()
        servo.close() # Pin komplett freigeben

# --- 4. ABLAUF ---

def main():
    try:
        # 1. Johannisbeere
        move_to(POSITIONS["Johannisbeere"])
        pour(SERVO_PINS["Johannisbeere"])
        time.sleep(0.5)

        # 2. Wasser
        move_to(POSITIONS["Wasser"])
        pour(SERVO_PINS["Wasser"])
        time.sleep(0.5)

        # 3. Zurück zur Warteposition
        move_to(POSITIONS["start"])
        print("Rezept fertig!")

    except KeyboardInterrupt:
        print("Abbruch durch Nutzer")
    finally:
        # Endgültiges Aufräumen
        en_dev.on()
        step_dev.close()
        dir_dev.close()
        en_dev.close()

if __name__ == "__main__":
    main()