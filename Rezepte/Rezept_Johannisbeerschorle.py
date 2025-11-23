import time
import fill_function as fill

def main():
    fill.set_current_position(0)  # Startpunkt
    
    #Getränk befüllen

    fill.move_to_drink("Johannisbeersaft")
    fill.pour_with_servo(fill.SERVO_PINS["Johannisbeersaft"], dwell=0.7)
    time.sleep(0.5)

    fill.move_to_drink("Wasser")
    fill.pour_with_servo(fill.SERVO_PINS["Wasser"], dwell=0.7)
    time.sleep(0.5)


    fill._setup_driver()
    try:
        fill.move_to_position(0)  # zurück zum Start
    finally:
        fill._cleanup_driver()

if __name__ == "__main__":
    main()