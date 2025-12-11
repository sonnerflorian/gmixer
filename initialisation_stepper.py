import time
from gpiozero import OutputDevice, Button
from gpiozero.pins.pigpio import PiGPIOFactory 
import sys

# --- 1. GLOBALE KONFIGURATION ---

# Steppermotor Pins (A4988-Treiber)
STEP_PIN = 16 
DIR_PIN = 20
ENABLE_PIN = 21
DELAY = 0.005 # Geschwindigkeit des Steppers während der Initialisierung
STEPS = 1 # Wir bewegen den Stepper Schritt für Schritt

# Taster-Pin (Endschalter)
BUTTON_PIN = 2 

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

    # Taster initialisieren (mit Pull-Down-Widerstand)
    # Wenn der Schalter 3.3V mit GPIO 2 verbindet, nutzen wir pull_up=False
    button = Button(BUTTON_PIN, pull_up=False, pin_factory=factory) 
    
    # Stepper am Anfang deaktivieren
    enable_pin.on() 
    print("Initialisierung abgeschlossen. Start bereit.")

except Exception as e:
    print(f"Fehler bei der Initialisierung: {e}")
    print("Stellen Sie sicher, dass der pigpiod Daemon läuft!")
    sys.exit(1)


# -----------------------------------
# --- 3. INITIALISIERUNGS-ROUTINE ---
# -----------------------------------

def find_home_position():
    """Bewegt den Stepper langsam in Richtung False, bis der Taster gedrückt wird."""
    
    # 1. Prüfe, ob der Taster bereits gedrückt ist
    if button.is_pressed:
        print("Taster ist bereits geschlossen. Home-Position gefunden.")
        return
        
    print("\n--- STARTE HOME-SUCHE (Richtung: FALSE) ---")
    
    # 2. Motor aktivieren und Richtung setzen
    enable_pin.off()
    dir_pin.off() # Setze Richtung auf FALSE
    
    # Endlosschleife, die bei jedem Schritt den Zustand des Tasters prüft
    while not button.is_pressed:
        
        # Sende einen Schritt
        step_pin.on() 
        time.sleep(DELAY) # Wichtig für die Geschwindigkeit
        step_pin.off()
        time.sleep(DELAY)
        
        # Optional: Statusmeldung, um zu sehen, dass das Skript läuft
        # if int(time.time() * 10) % 10 == 0:
        #    print(".", end="", flush=True) # Zeigt Aktivität
        
    # 3. Wenn die Schleife beendet wird, wurde der Taster gedrückt
    print("\n\n*** HOME-POSITION ERREICHT! ***")

# -----------------------------------
# --- 4. HAUPTPROGRAMM ---
# -----------------------------------

try:
    find_home_position()

except KeyboardInterrupt:
    print("\nRoutine gestoppt durch Benutzer (Strg+C).")

finally:
    # 5. AUFRÄUMEN
    print("Führe Cleanup aus.")
    # Stepper deaktivieren (wichtig, sonst hält er die Position)
    enable_pin.on()
    # gpiozero schließt die Geräte automatisch