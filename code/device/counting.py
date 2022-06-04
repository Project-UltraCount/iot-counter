import RPi.GPIO as GPIO
import time
from threading import Thread
from device.lcd import lcd_display
from device.device_constants import TRIG_1, TRIG_2, ECHO_1, ECHO_2, calibration_offset, min_human_width, reset_threshold, \
    detection_threshold, waiting_time, LCD_LINE_1, LCD_LINE_2, max_range, min_range, calibration_samples


class Counting:
    def __init__(self, mode):
        self.stop = False
        self.a1 = Thread(target=self.uni_counting)
        self.a2 = Thread(target=self.bi_counting)
        self.mode = mode
        # constants to be declared
        if mode in (1,2):
            if mode == 1:
                self.no_of_pedestrians_1 = 0
                self.pedestrian_inflow = 0
            if mode == 2:
                self.no_of_pedestrians_2 = 0
                self.pedestrian_inflow = 0
            self.count_1 = 0
            self.reset_count_1 = 0
            self.pedestrian_detected_1 = False
            self.setting_gap = False
            self.__calibration_start_sensor(1)

        elif mode == 3:
            self.count_1 = 0
            self.reset_count_1 = 0
            self.no_of_pedestrians_1 = 0
            self.pedestrian_inflow = 0
            self.pedestrian_detected_1 = False
            self.count_2 = 0
            self.reset_count_2 = 0
            self.no_of_pedestrians_2 = 0
            self.pedestrian_outflow = 0
            self.pedestrian_detected_2 = False
            self.setting_gap_1 = False
            self.setting_gap_2 = False
            self.no_of_pedestrians_total = 0
            self.sensor_1_get_time = 0
            self.sensor_2_get_time = 0
            self.__calibration_start_sensor(1)
            self.__calibration_start_sensor(2)

    def __calibration_start_sensor(self, sensor_no):
        echo = trig = 0
        if sensor_no == 1:
            echo = ECHO_1
            trig = TRIG_1
        if sensor_no == 2:
            echo = ECHO_2
            trig = TRIG_2

        GPIO.setup(echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Sensor " + str(sensor_no) + " calibration starts...")
        sum_of_measurement = 0
        for i in range(calibration_samples):
            t0 = time.time()
            time.localtime()
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(trig, GPIO.LOW)
            GPIO.wait_for_edge(echo, GPIO.FALLING, timeout=24)
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
        average_dist = round(sum_of_measurement / calibration_samples, 2)
        if sensor_no == 1:
            self.average_dist_1 = average_dist
        if sensor_no == 2:
            self.average_dist_2 = average_dist
        print("Average range without pedestrian for sensor " + str(sensor_no) + " : " + str(average_dist) + " cm")
        lcd_display("Sensor " + str(sensor_no) + " tuned", LCD_LINE_1)
        time.sleep(1)

    def uni_counting(self, no_of_pedestrians=0):
        lcd_display("Uni counting", LCD_LINE_1)  # display on lcd screen
        while not self.stop:
            # sensor 1
            t1 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=24)
            duration_1 = time.time() - t1 - calibration_offset
            distance_1 = round(duration_1 * 17150, 2)

            if not self.setting_gap:
                if distance_1 < self.average_dist_1 - min_human_width: # detected obstacles
                    self.count_1 += 1
                    self.reset_count_1 = 0
                else:
                    self.count_1 = 0

                # detect the obstacle multiple times, regard as 1 count, reset other parameters
                if self.count_1 >= detection_threshold and not self.pedestrian_detected_1:
                    self.pedestrian_detected_1 = True
                    no_of_pedestrians += 1
                    # distinguish entrance and exit
                    if self.mode == 1:
                        self.no_of_pedestrians_1 += 1
                        self.pedestrian_inflow += 1
                        lcd_display("Entrance: " + str(no_of_pedestrians), LCD_LINE_2)
                    elif self.mode == 2:
                        self.no_of_pedestrians_2 += 1
                        self.pedestrian_outflow += 1
                        lcd_display("Exit: " + str(no_of_pedestrians), LCD_LINE_2)
                    self.setting_gap = True
            else:
                if distance_1 < self.average_dist_1 - min_human_width:
                    self.reset_count_1 = 0
                elif distance_1 > self.average_dist_1 - min_human_width and self.pedestrian_detected_1: # no obstacles
                    self.reset_count_1 += 1
                    if self.reset_count_1 >= reset_threshold:
                        self.reset_counter(1)
                        self.setting_gap = False

            time.sleep(waiting_time)

    def bi_counting(self):
        pseudo_count = 0
        lcd_display("Bidir counting", LCD_LINE_1)
        while not self.stop:
            # sensor 1
            t1 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=24)
            duration_1 = time.time() - t1 - calibration_offset
            distance_1 = round(duration_1 * 17150, 2)

            if not self.setting_gap_1:
                if distance_1 < self.average_dist_1 - min_human_width:
                    self.count_1 += 1
                    self.reset_count_1 = 0
                else:
                    self.count_1 = 0
                if self.count_1 >= detection_threshold and not self.pedestrian_detected_1:
                    pseudo_count += 1
                    self.setting_gap_1 = True
                    self.pedestrian_detected_1 = True
                    self.sensor_1_get_time = time.time()
                    print("sensor 1 gets it")
                else:
                    pass
            else:
                if distance_1 < self.average_dist_1 - min_human_width:
                    self.reset_count_1 = 0
                elif distance_1 > self.average_dist_1 - min_human_width and self.pedestrian_detected_1:
                    self.reset_count_1 += 1
                    if self.reset_count_1 >= reset_threshold:
                        pseudo_count = 0
                        self.reset_counter(1)
                        self.setting_gap_1 = False
                        print("sensor 1 resets")

            time.sleep(waiting_time)

            # identify direction from time difference
            if pseudo_count >= 2:
                if self.sensor_1_get_time < self.sensor_2_get_time:
                    self.no_of_pedestrians_1 += 1
                    self.pedestrian_inflow += 1
                    print("In Count: " + str(self.no_of_pedestrians_1))
                elif self.sensor_1_get_time > self.sensor_2_get_time:
                    self.no_of_pedestrians_2 += 1
                    self.pedestrian_outflow += 1
                    print("Out Count: " + str(self.no_of_pedestrians_2))
                pseudo_count = 0
                self.sensor_1_get_time = self.sensor_2_get_time = time.time()  # reset sensor 1 and sensor 2 time
                self.reset_counter(2)  # reset counting constants
                lcd_display("In: " + str(self.no_of_pedestrians_1) + " Out: "
                            + str(self.no_of_pedestrians_2), LCD_LINE_1)
                lcd_display("Total: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                            LCD_LINE_2)
                print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
            else:
                pass

            # sensor 2
            t2 = time.time()
            GPIO.output(TRIG_2, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_2, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_2, GPIO.FALLING, timeout=24)
            duration_2 = time.time() - t2 - calibration_offset
            distance_2 = round(duration_2 * 17150, 2)

            if not self.setting_gap_2:
                if distance_2 < self.average_dist_2 - min_human_width:
                    self.count_2 += 1
                    self.reset_count_2 = 0
                elif self.pedestrian_detected_2:
                    self.reset_count_2 += 1
                    if self.reset_count_2 >= reset_threshold:
                        self.reset_counter(2)
                else:
                    self.count_2 = 0
                if self.count_2 >= detection_threshold and not self.pedestrian_detected_2:
                    pseudo_count += 1
                    self.setting_gap_2 = True
                    self.pedestrian_detected_2 = True
                    self.sensor_2_get_time = time.time()
                    print("sensor 2 gets it")
                else:
                    pass
            else:
                if distance_2 < self.average_dist_2 - min_human_width:
                    self.reset_count_2 = 0
                elif distance_2 > self.average_dist_2 - min_human_width and self.pedestrian_detected_2:
                    self.reset_count_2 += 1
                    if self.reset_count_2 >= reset_threshold:
                        pseudo_count = 0
                        self.reset_counter(2)
                        self.setting_gap_2 = False
                        print("sensor 2 resets")

            # identify direction from time difference
            if pseudo_count >= 2:
                if self.sensor_1_get_time < self.sensor_2_get_time:
                    self.no_of_pedestrians_1 += 1
                    print("In Count: " + str(self.no_of_pedestrians_1))
                elif self.sensor_1_get_time > self.sensor_2_get_time:
                    self.no_of_pedestrians_2 += 1
                    print("Out Count: " + str(self.no_of_pedestrians_2))
                pseudo_count = 0
                self.sensor_1_get_time = self.sensor_2_get_time = time.time()  # reset sensor 1 and sensor 2 time
                self.reset_counter(1)  # reset counting constants
                lcd_display("In: " + str(self.no_of_pedestrians_1) + " Out: "
                            + str(self.no_of_pedestrians_2), LCD_LINE_1)
                lcd_display("Combined: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                            LCD_LINE_2)
                print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
            else:
                pass
            time.sleep(waiting_time)

    def reset_counter(self, mode):
        if mode == 1:
            self.count_1 = self.reset_count_1 = 0
            self.pedestrian_detected_1 = False
        if mode == 2:
            self.count_2 = self.reset_count_2 = 0
            self.pedestrian_detected_2 = False

    def thread_start_counting(self):
        if self.mode in (1,2):
            self.a1.start()
            time.sleep(1)
        else:
            self.a2.start()
            time.sleep(1)

    def thread_stop_counting(self):
        self.stop = True

    def get_flow_count(self):
        if self.mode == 1:
            inflow = self.pedestrian_inflow
            self.pedestrian_inflow = 0 # reset inflow count
            return inflow, 0
        elif self.mode == 2:
            outflow = self.pedestrian_outflow
            self.pedestrian_outflow = 0  # reset inflow count
            return 0, outflow
        elif self.mode == 3:
            inflow = self.pedestrian_inflow
            self.pedestrian_inflow = 0  # reset inflow count
            outflow = self.pedestrian_outflow
            self.pedestrian_outflow = 0  # reset inflow count
            return inflow, outflow
