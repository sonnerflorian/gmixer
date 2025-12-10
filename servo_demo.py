import RPi.GPIO as GPIO
import time

# 1. Konfiguration
servo_pin = 16 # Wähle den GPIO-Pin, an den das orange/gelbe Kabel angeschlossen ist
GPIO.setmode(GPIO.BCM) # Verwende die BCM-Nummerierung (nicht die Pin-Nummer)
GPIO.setup(servo_pin, GPIO.OUT)

# 2. PWM-Einrichtung
# Servos benötigen eine Frequenz von typischerweise 50 Hz (50 Zyklen pro Sekunde)
pwm = GPIO.PWM(servo_pin, 50) 
pwm.start(0) # Starte PWM mit einem Tastverhältnis (Duty Cycle) von 0%

# 3. Funktion zur Winkelsteuerung
def set_angle(angle):
    # Die Position des Servos wird durch den "Duty Cycle" (Tastverhältnis) bestimmt.
    # Ein typischer Servo benötigt:
    # 0 Grad: Duty Cycle von ca. 2.5 % (Pulsweite von 0.5 ms)
    # 90 Grad: Duty Cycle von ca. 7.5 % (Pulsweite von 1.5 ms)
    # 180 Grad: Duty Cycle von ca. 12.5 % (Pulsweite von 2.5 ms)
    
    # Berechne den Duty Cycle: DC = (angle / 18) + 2.5
    duty_cycle = (angle / 18.0) + 2.5
    
    # Ändere den Duty Cycle des PWM-Signals
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5) # Warte, bis der Servo die Position erreicht hat
    pwm.ChangeDutyCycle(0) # Setze den Duty Cycle zurück, um Rauschen zu vermeiden

counter = 0
# 4. Hauptprogramm
try:
    while counter <= 1:   
        print("Setze Winkel auf 0 Grad")
        set_angle(0)
        time.sleep(1)
        
        print("Setze Winkel auf 90 Grad")
        set_angle(90)
        time.sleep(1)
        counter += 1
        
    print("Programm beendet.")
    pwm.stop()      # Stoppe PWM
    GPIO.cleanup()  # Setze die GPIO-Pins zurück


# Beende das Programm sauber bei Tastendruck (Ctrl+C)
except KeyboardInterrupt:
    print("Programm beendet.")
    pwm.stop()      # Stoppe PWM
    GPIO.cleanup()  # Setze die GPIO-Pins zurück