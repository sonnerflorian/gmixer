import time
from gpiozero import OutputDevice, Button
from gpiozero.pins.pigpio import PiGPIOFactory 
import sys

# --- 1. GLOBALE KONFIGURATION ---

# Steppermotor Pins (A4988-Treiber)
STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21
DELAY = 0.0005 # Geschwindigkeit des Steppers (anpassen für schnellere/langsamere Suche)

# Taster-Pin (Endschalter)
BUTTON_PIN = 2 # GPIO 2 hat festen Pull-Up und muss mit GND verbunden werden

# -----------------------------------
# --- 2. GERÄTE-SETUP ---
# -----------------------------------

try:
    # Starte die pigpio Factory (Voraussetzung: pigpiod läuft)
    factory = PiGPIOFactory()

    # Stepper-Geräte initialisieren
    dir_pin = OutputDevice(DIR_PIN, pin_factory=factory)
    enable_pin = OutputDevice(ENABLE_PIN, pin_factory=factory)
    step_pin = OutputDevice(STEP_PIN, pin_factory=factory) 

    # Taster initialisieren (Wir verwenden den festen Pull-Up von GPIO 2)
    # Taster wird als gedrückt erkannt, wenn das Signal auf LOW (GND) gezogen wird.
    button = Button(BUTTON_PIN, pull_up=True, pin_factory=factory) 
    
    # Stepper am Anfang deaktivieren
    enable_pin.on() 
    print("Initialisierung abgeschlossen. Start bereit.")

except Exception as e:
    print(f"Fehler bei der Initialisierung: {e}")
    print("Sicherstellen, dass der pigpiod Daemon läuft und GPIO 2 mit GND verbunden ist!")
    sys.exit(1)


# -----------------------------------
# --- 3. INITIALISIERUNGS-ROUTINE ---
# -----------------------------------

def move_stepper_until_button_pressed(direction=False):
    """
    Bewegt den Steppermotor Schritt für Schritt in die angegebene Richtung (False/Rückwärts), 
    bis der Taster (Button) geschlossen wird (LOW).
    """
    
    # 1. Prüfe, ob der Taster bereits gedrückt ist
    if button.is_pressed:
        print("Taster ist bereits geschlossen. Home-Position gefunden.")
        return
        
    print(f"\n--- STARTE HOME-SUCHE (Richtung: {'Vorwärts' if direction else 'Rückwärts'}) ---")
    
    # 2. Motor aktivieren und Richtung setzen
    enable_pin.off()
    dir_pin.value = direction 
    time.sleep(0.005) # Kurze Zeit, um den Treiber zu stabilisieren
    
    # 3. Endlosschleife, die bei jedem Schritt den Zustand des Tasters prüft
    # Die Schleife läuft, solange der Taster NICHT gedrückt ist
    while not button.is_pressed:
        
        # Sende einen Schritt
        step_pin.on() 
        time.sleep(DELAY)
        
        step_pin.off()
        time.sleep(DELAY)
        
    # 4. Wenn die Schleife beendet wird, wurde der Taster gedrückt
    print("\n\n*** HOME-POSITION ERREICHT UND MOTOR GESTOPPT! ***")
    
    # Motor deaktivieren, um Haltestrom und Geräusche zu eliminieren
    enable_pin.on()
    time.sleep(0.1)


# -----------------------------------
# --- 4. HAUPTPROGRAMM ---
# -----------------------------------

try:
    # Starte die Home-Suche. Der Motor läuft, bis der Button GPIO 2 auf GND zieht.
    # Wir setzen direction=False (die Richtung, in der der Endschalter liegt)
    move_stepper_until_button_pressed(direction=False) 

except KeyboardInterrupt:
    print("\nRoutine gestoppt durch Benutzer (Strg+C).")

finally:
    # 5. AUFRÄUMEN
    print("Führe Cleanup aus.")
    enable_pin.on()
    # gpiozero schließt die Geräte automatisch