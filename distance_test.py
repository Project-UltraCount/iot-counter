#!/usr/bin/python
import RPi.GPIO as GPIO
import time

# set these ports as input and output
GPIO.setmode(GPIO.BOARD)

PIN_TRIGGER = 16
PIN_ECHO = 18
calibration_offset = 0

GPIO.setup(PIN_TRIGGER, GPIO.OUT)  # set the Trigger pin low
GPIO.setup(PIN_ECHO, GPIO.IN)

GPIO.output(PIN_TRIGGER, GPIO.LOW)

print("Waiting for sensor to settle")

time.sleep(2)
# To create our trigger pulse, we set out trigger pin high for 10 microseconds then set it low again
print("Calculating distance")

try:
    while True:
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        # time.time() function measures the latest timestamp of high/low condition
        # e.g. pin from low -> high -- measure the latest time at which pin is low(transition point)
        # hence, by measuring two transition points, the time difference = time travelled
        pulse_start_time = 0
        pulse_end_time = 0
        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time = time.time()
        # calculate the distance travelled -> speed in cm: 34300 =distance/(time/2) -> distance = time * 17150
        # round to two decimal places
        pulse_duration = pulse_end_time - pulse_start_time - calibration_offset
        distance = round(pulse_duration * 17150, 2)
        print("Distance: " + str(distance) + "cm")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Keyboard interrupt")

finally:
    print("clean up")
    GPIO.cleanup()
