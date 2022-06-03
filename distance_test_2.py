import time
import RPi.GPIO as GPIO

# set these ports as input and output
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
PIN_TRIGGER = 29
PIN_ECHO = 31
PIN_BUTTON_1 = 36
PIN_BUTTON_2 = 32
LED = 35

GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
calibration_offset = 0.00243

GPIO.output(PIN_TRIGGER, GPIO.LOW)
GPIO.output(LED, GPIO.HIGH)
print("Waiting for sensor to settle")

time.sleep(2)

GPIO.wait_for_edge(PIN_BUTTON_1, GPIO.RISING)
# To create our trigger pulse, we set out trigger pin high for 10 microseconds then set it low again
print("Calculating distance")

try:
    while True:
        t0 = time.time()

        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        # time.time() function measures the latest timestamp of high/low condition
        # e.g. pin from low -> high -- measure the latest time at which pin is low(transition point)
        # hence, by measuring two transition points, the time difference = time travelled
        pin = GPIO.wait_for_edge(PIN_ECHO, GPIO.FALLING, timeout=5000)
        if pin is None:
            print("echo timeout exceeded")
        # calculate the distance travelled -> speed in cm: 34300 =distance/(time/2) -> distance = time * 17150
        # round to two decimal places
        pulse_duration = time.time() - t0 - calibration_offset
        distance = round(pulse_duration * 17150, 2)
        print("Distance: " + str(distance) + "cm")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Keyboard interrupt")

finally:
    print("clean up")
    GPIO.cleanup()
