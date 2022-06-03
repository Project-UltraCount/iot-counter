#!/usr/bin/python
import threading

import RPi.GPIO as GPIO
import time

# set these ports as input and output
GPIO.setmode(GPIO.BOARD)

TRIG_1 = 29
ECHO_1 = 31
TRIG_2 = 24
ECHO_2 = 40
calibration_offset = 0

GPIO.setup(TRIG_1, GPIO.OUT)  # set the Trigger pin low
GPIO.setup(ECHO_1, GPIO.IN)
GPIO.setup(TRIG_2, GPIO.OUT)  # set the Trigger pin low
GPIO.setup(ECHO_2, GPIO.IN)

GPIO.output(TRIG_1, GPIO.LOW)
GPIO.output(TRIG_2, GPIO.LOW)

print("Waiting for sensor to settle")

time.sleep(2)
# To create our trigger pulse, we set out trigger pin high for 10 microseconds then set it low again
print("Calculating distance")


def range_1():
    GPIO.output(TRIG_1, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(TRIG_1, GPIO.LOW)
    # time.time() function measures the latest timestamp of high/low condition
    # e.g. pin from low -> high -- measure the latest time at which pin is low(transition point)
    # hence, by measuring two transition points, the time difference = time travelled
    pulse_start_time = 0
    pulse_end_time = 0
    while GPIO.input(ECHO_1) == 0:
        pulse_start_time = time.time()
    while GPIO.input(ECHO_1) == 1:
        pulse_end_time = time.time()
    # calculate the distance travelled -> speed in cm: 34300 =distance/(time/2) -> distance = time * 17150
    # round to two decimal places
    pulse_duration = pulse_end_time - pulse_start_time - calibration_offset
    distance = round(pulse_duration * 17150, 2)
    print("Distance for sensor 1: " + str(distance) + "cm")
    time.sleep(0.1)

def range_2():
    GPIO.output(TRIG_2, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_2, GPIO.LOW)
    pulse_start_time = 0
    pulse_end_time = 0
    while GPIO.input(ECHO_2) == 0:
        pulse_start_time = time.time()
    while GPIO.input(ECHO_2) == 1:
        pulse_end_time = time.time()
    pulse_duration = pulse_end_time - pulse_start_time - calibration_offset
    distance = round(pulse_duration * 17150, 2)
    print("Distance for sensor 2: " + str(distance) + "cm")
    time.sleep(0.1)

try:
    t1 = threading.Thread(target=range_1, )
    t2 = threading.Thread(target=range_2, )
    t1.start()
    t2.start()

except KeyboardInterrupt:
    print("Keyboard interrupt")

finally:
    print("clean up")
