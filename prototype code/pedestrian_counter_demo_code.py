import RPi.GPIO as GPIO
import time
import _thread

timeout = 0.0180  # about 3 meters
waiting_time = 0.00003
detection_threshold = 5
calibration_samples = 100
max_range = 300  # 3 meters
min_range = 75  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 5  # no of times the range is back to normal
calibration_offset = 0.00243

# Rpi 3A USB-C supply
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND

GPIO.setmode(GPIO.BOARD)

# name input and output pins to refer to later in the code
TRIG_1 = 38
ECHO_1 = 40
TRIG_2 = 38
ECHO_2 = 40
print("Distance measurement in progress")

GPIO.setup(TRIG_1, GPIO.OUT)
GPIO.setup(ECHO_1, GPIO.IN)
GPIO.output(TRIG_1, False)  # set the Trigger pin low
GPIO.setup(TRIG_2, GPIO.OUT)
GPIO.setup(ECHO_2, GPIO.IN)
GPIO.output(TRIG_2, False)  # set the Trigger pin low
print("Sensors have been set up")


class Count:
    def __init__(self):
        self.__calibration_start_sensor_1()
        self.__calibration_start_sensor_2()
        self.count1 = 0
        self.reset_count1 = 0
        self.no_of_pedestrians1 = 0
        self.pedestrian_detected1 = False
        self.count2 = 0
        self.reset_count2 = 0
        self.no_of_pedestrians2 = 0
        self.pedestrian_detected2 = False

    def __calibration_start_sensor_1(self):
        GPIO.setup(ECHO_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Sensor 1 calibration starts...")
        sum_of_measurement = 0
        for i in range(calibration_samples):
            t0 = time.time()
            time.localtime()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=24)
            pulse_duration = time.time() - t0 - calibration_offset
            distance = round(pulse_duration * 17150, 2)
            print(str(distance))
            if max_range > distance > min_range:
                sum_of_measurement += distance
            else:
                sum_of_measurement += min_range
            i += 1
            time.sleep(0.01)
        print("Calibration ends...")
        self.average_dist_1 = round(sum_of_measurement / calibration_samples, 2)
        print("Average range without pedestrian for sensor 1: " + str(self.average_dist_1) + " cm")

    def __calibration_start_sensor_2(self):
        GPIO.setup(ECHO_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Sensor 2 calibration starts...")
        sum_of_measurement = 0
        for i in range(calibration_samples):
            t0 = time.time()
            GPIO.output(TRIG_2, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_2, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_2, GPIO.FALLING, timeout=24)
            duration = time.time() - t0 - calibration_offset
            distance = round(duration * 17150, 2)
            print(str(distance))
            if max_range > distance > min_range:
                sum_of_measurement += distance
            else:
                sum_of_measurement += min_range
            i += 1
            time.sleep(0.01)
        print("Calibration ends...")
        self.average_dist_2 = round(sum_of_measurement / calibration_samples, 2)
        print("Average range without pedestrian for sensor 2: " + str(self.average_dist_2) + " cm")

    # constants to be declared
    def counting1(self):
        pulse_end1 = 0
        pulse_start1 = 0
        while True:
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            time.sleep(0.00001)

            while GPIO.input(ECHO_1) == 0:
                pulse_start1 = float(time.time())
            while GPIO.input(ECHO_1) == 1:
                pulse_end1 = float(time.time())
            duration = pulse_end1 - pulse_start1
            distance = duration * 17150

            if distance < self.average_dist_1 - min_human_width:
                self.count1 += 1
                self.reset_count1 = 0
            elif self.pedestrian_detected1:
                self.reset_count1 += 1
                if self.reset_count1 >= reset_threshold:
                    self.count1 = 0  # reset counter
                    self.reset_count1 = 0
                    self.pedestrian_detected1 = False
            else:
                self.count1 = 0
            if self.count1 >= detection_threshold and not self.pedestrian_detected1:
                self.no_of_pedestrians1 += 1
                self.pedestrian_detected1 = True
                print("Pedestrian count: " + str(self.no_of_pedestrians1))
            time.sleep(waiting_time)

    def counting2(self):
        pulse_end2 = 0
        pulse_start2 = 0
        while True:
            GPIO.output(TRIG_2, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_2, GPIO.LOW)
            time.sleep(0.00001)

            while GPIO.input(ECHO_2) == 0:
                pulse_start2 = float(time.time())
            while GPIO.input(ECHO_2) == 1:
                pulse_end2 = float(time.time())
            duration = pulse_end2 - pulse_start2
            distance = duration * 17150

            if distance < self.average_dist_2 - min_human_width:
                self.count2 += 1
                self.reset_count2 = 0
            elif self.pedestrian_detected2:
                self.reset_count2 += 1
                if self.reset_count2 >= reset_threshold:
                    self.count2 = 0  # reset counter
                    self.reset_count2 = 0
                    self.pedestrian_detected2 = False
            else:
                self.count2 = 0
            if self.count2 >= detection_threshold and not self.pedestrian_detected2:
                self.no_of_pedestrians2 += 1
                self.pedestrian_detected2 = True
                print("Pedestrian count: " + str(self.no_of_pedestrians2))
            time.sleep(waiting_time)


# instantiate the Count functions
trial_1 = Count()
try:
    _thread.start_new_thread(trial_1.counting1(),("Thread-1",))
    _thread.start_new_thread(trial_1.counting2(),("Thread-2",))
except KeyboardInterrupt:
    print("clean up")
    time.sleep(2)
    GPIO.cleanup()
