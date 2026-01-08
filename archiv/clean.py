import RPi.GPIO as GPIO
import time
import sys

# --- 1. GLOBALE KONFIGURATION ---

# Pins, die in deinem Stepper- und Servo-Projekt verwendet werden
# Es ist wichtig, den ENABLE_PIN explizit zu deaktivieren, bevor alles bereinigt wird.
ENABLE_PIN = 21  # Steppermotor ENABLE Pin
# Alle anderen verwendeten Pins (Optional, aber gut zur Dokumentation)
# Alle Pins werden durch GPIO.cleanup() bereinigt, aber hier sind die Wichtigsten:
# STEP_PIN = 16 
# DIR_PIN = 20
# SERVO_PINS = [26, 19, 13, 6, 5, 11, 9, 10]


# --- 2. CLEANUP LOGIK ---

print("Starte GPIO Cleanup und Sicherheitsmodus.")

try:
    # 1. Warnungen deaktivieren
    GPIO.setwarnings(False) 
    
    # 2. Modus setzen: Dies ist notwendig, um Pins zu adressieren
    # Wir verwenden den BCM-Modus, da dieser in deinen Skripten verwendet wurde.
    GPIO.setmode(GPIO.BCM) 

    # 3. Sicherheits-Shutdown für den Stepper:
    # Setze den ENABLE-Pin auf OUTPUT und dann auf HIGH, um den Treiber zu deaktivieren.
    # Dies ist wichtig, da der Motor ansonsten im Haltestrom-Modus verbleiben könnte.
    GPIO.setup(ENABLE_PIN, GPIO.OUT)
    GPIO.output(ENABLE_PIN, GPIO.HIGH) 
    print(f"-> Steppermotor-Treiber an GPIO {ENABLE_PIN} (ENABLE) wurde deaktiviert (HIGH).")

    # Optional: Alle Servo-Pins kurz als OUTPUT setzen und das PWM-Signal stoppen
    # (Obwohl cleanup dies meistens regelt, ist es sicherer)
    for pin in [16, 20] + [26, 19, 13, 6, 5, 11, 9, 10]:
       GPIO.setup(pin, GPIO.OUT)


except Exception as e:
    # Sollte der Modus nicht gesetzt werden können, trotzdem versuchen, aufzuräumen
    print(f"Ein Fehler während der Sicherheitsinitialisierung: {e}")
    
finally:
    # 4. Abschließendes Cleanup: Setzt alle verwendeten Pins in den sicheren INPUT-Modus
    GPIO.cleanup()
    print("-> Alle verwendeten GPIO-Pins wurden erfolgreich in den sicheren INPUT-Modus zurückgesetzt.")
    print("Cleanup abgeschlossen.")
    sys.exit(0)
    