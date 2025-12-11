import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory 

# --- KONFIGURATION ---
SERVO_PIN = 26       # BCM-Pin-Nummer (Ihr funktionierender Pin)
TEST_CYCLES = 3      # Wie oft soll der Servo fahren

# Aggressive Pulsweiten für maximale Reichweite (0.45ms bis 2.55ms)
MIN_PULSE = 0.00045  
MAX_PULSE = 0.00255  

# -----------------------------------
# --- HAUPTPROGRAMM ---
# -----------------------------------

def test_servo():
    print(f"Starte Servo-Test auf GPIO {SERVO_PIN}...")
    
    # Sicherstellen, dass der pigpiod Daemon läuft!
    try:
        factory = PiGPIOFactory()
    except Exception as e:
        print("FEHLER: PiGPIOFactory konnte nicht gestartet werden.")
        print("Stellen Sie sicher, dass der 'pigpiod' Daemon läuft. (sudo systemctl start pigpiod)")
        return

    servo = None
    try:
        # Initialisiere den Servo mit der Factory und den aggressiven Pulsweiten
        servo = Servo(SERVO_PIN, 
                      min_pulse_width=MIN_PULSE, 
                      max_pulse_width=MAX_PULSE, 
                      pin_factory=factory) 
        
        print(f"Servo initialisiert. Starte {TEST_CYCLES} Zyklen.")

        for i in range(TEST_CYCLES):
            print(f"--- Durchlauf {i+1} ---")
            
            # 1. Maximale Öffnung (+1.0 entspricht 180 Grad)
            print("Setze auf MAX (180 Grad / +1.0)")
            servo.max() 
            time.sleep(1.5)
            
            # 2. Minimale Öffnung (-1.0 entspricht 0 Grad)
            print("Setze auf MIN (0 Grad / -1.0)")
            servo.min() 
            time.sleep(1.5)

        print("\nTest beendet.")

    except Exception as e:
        print(f"\nEIN FEHLER IST AUFGETRETEN: {e}")
        
    finally:
        # Sauberes Aufräumen
        if servo is not None:
            servo.detach() # Stoppt das PWM-Signal
            servo.close()
        
        # Da wir die Factory nur für diesen Test gestartet haben, 
        # muss sie nicht global geschlossen werden.


if __name__ == "__main__":
    test_servo()