import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


def button_1_callback():
    print("Button 1 was pushed!")


def button_2_callback():
    print("Button 2 was pushed")


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(36, GPIO.BOTH, bouncetime=200)
GPIO.add_event_detect(32, GPIO.BOTH, bouncetime=200)
if GPIO.event_detected(36):
    button_1_callback()
    GPIO.remove_event_deteced(32)
if GPIO.event_detected(32):
    button_1_callback()
    GPIO.remove_event_deteced(36)
