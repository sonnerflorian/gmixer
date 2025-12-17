import time
import sys
import os
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# Pfad für fill_function (Stepper)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fill_function as fill
import hardware_config as cfg

# --- 1. SETUP WIE IM TEST-SKRIPT ---
factory = PiGPIOFactory()

# Wir erstellen ein Dictionary mit allen Servos, genau wie in deinem Test
servos = {}
for name, pin in cfg.SERVO_PINS.items():
    servos[name] = Servo(pin, pin_factory=factory)
    servos[name].detach()

def set_servo_stable(servo_obj, angle):
    """Deine funktionierende Logik aus dem Test-Skript"""
    value = (angle / 90.0) - 1.0
    servo_obj.value = value
    time.sleep(0.5) 
    servo_obj.detach() 

def main():
    try:
        # 1. Johannisbeere
        fill.move_to_drink("Johannisbeere")
        print("Gieße Johannisbeere...")
        
        # Nutze das bereits existierende Objekt
        set_servo_stable(servos["Johannisbeere"], 130) # Auf
        time.sleep(0.7) # dwell
        set_servo_stable(servos["Johannisbeere"], 90)  # Zu
        
        time.sleep(0.5)

        # 2. Wasser
        fill.move_to_drink("Wasser")
        print("Gieße Wasser...")
        
        set_servo_stable(servos["Wasser"], 130) # Auf
        time.sleep(0.7) # dwell
        set_servo_stable(servos["Wasser"], 0)  # Zu

        # 3. Zurück
        fill.move_to_drink("start")

    except KeyboardInterrupt:
        print("Abbruch")
    finally:
        # Sauber schließen am Ende des Rezepts
        for s in servos.values():
            s.close()
        fill.gpio_cleanup()

if __name__ == "__main__":
    main()