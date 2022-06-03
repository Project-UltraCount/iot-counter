#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Backup code
import sys

import RPi.GPIO as GPIO
import time
import oss2
from threading import Thread
from subprocess import check_output

# OSS constants to be declared
OSS_id = "LTAI5t5jK7G15gb9D7yRMV16"
OSS_key = "Uy4lVE2ZWqVdZLxWKP7Vl2u7iGvzco"
OSS_endpoint = r"https://oss-ap-southeast-1.aliyuncs.com"
OSS_bucket_name = "projectultracount"
OSS_object_name_1 = "Gate1@Entrance.txt"
OSS_object_name_2 = "Gate1@Exit.txt"
OSS_timeout = 1000

FILE_UPDATE_FREQUENCY = 60  # only need to upload, writing to local file is not needed

# time.time() -> Seconds since epoch
# connect to the FTP server
timeout = 0.0180  # about 3 meters
waiting_time = 0.00003  # 30 microseconds
detection_threshold = 4
abortion_threshold = 1000
calibration_samples = 100
max_range = 300  # 3 meters
min_range = 70  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 4  # no of times the range is back to normal
calibration_offset = 0.00243  # calibration for ultrasonic distance measuring

# Rpi 3A USB-C supply
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND
GPIO.setwarnings(False)

# setting up input and output pins
# ultrasonic sensor 1 for entrance
TRIG_1 = 11
ECHO_1 = 3
# ultrasonic sensor 2 for exit
TRIG_2 = 13
ECHO_2 = 5
# Button switch to commence the program / switch between alternate modes of measurement
BUTTON_1 = 19
BUTTON_2 = 21
# LED_1 indicating progress abort
LED_1 = 23
# LED_2 indicating successful Wifi connection
LED_2 = 37
# LCD screen
LCD_RS = 8
LCD_E = 10
LCD_D4 = 12
LCD_D5 = 36
LCD_D6 = 38
LCD_D7 = 40

# Define lcd constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
E_PULSE = 0.0005
E_DELAY = 0.0005


class Setup:

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.__switch()
        self.__sensor()
        self.lcd_1 = self.LCD()

    @staticmethod
    def __switch():
        GPIO.setup(LED_1, GPIO.OUT)
        GPIO.setup(BUTTON_1, GPIO.IN)
        GPIO.setup(BUTTON_2, GPIO.IN)
        print("Switches have been set up")

    @staticmethod
    def __sensor():
        # set sensor ports as input and output
        GPIO.setup(TRIG_1, GPIO.OUT)
        GPIO.setup(ECHO_1, GPIO.IN)
        GPIO.output(TRIG_1, False)  # set the Trigger pin low
        GPIO.setup(TRIG_2, GPIO.OUT)
        GPIO.setup(ECHO_2, GPIO.IN)
        GPIO.output(TRIG_2, False)  # set the Trigger pin low
        print("Sensors have been set up")

    class LCD:
        def __init__(self):
            self.lcd()
            self.lcd_init()
            self.display()
            self.test_file = None

        @staticmethod
        def lcd():
            # set lcd ports as input and output
            GPIO.setwarnings(False)
            GPIO.setup(LCD_E, GPIO.OUT)  # E
            GPIO.setup(LCD_RS, GPIO.OUT)  # RS
            GPIO.setup(LCD_D4, GPIO.OUT)  # D4
            GPIO.setup(LCD_D5, GPIO.OUT)  # D5
            GPIO.setup(LCD_D6, GPIO.OUT)  # D6
            GPIO.setup(LCD_D7, GPIO.OUT)  # D7
            print("LCD has been set up")

        def lcd_init(self):
            # Initialise display
            self.lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
            self.lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
            self.lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
            self.lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
            self.lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
            self.lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
            time.sleep(E_DELAY)

        def lcd_byte(self, bits, mode):
            # Send byte to data pins
            # bits = data
            # mode = True  for character
            #        False for command

            GPIO.output(LCD_RS, mode)  # RS

            # High bits
            GPIO.output(LCD_D4, False)
            GPIO.output(LCD_D5, False)
            GPIO.output(LCD_D6, False)
            GPIO.output(LCD_D7, False)
            if bits & 0x10 == 0x10:
                GPIO.output(LCD_D4, True)
            if bits & 0x20 == 0x20:
                GPIO.output(LCD_D5, True)
            if bits & 0x40 == 0x40:
                GPIO.output(LCD_D6, True)
            if bits & 0x80 == 0x80:
                GPIO.output(LCD_D7, True)

            # Toggle 'Enable' pin
            self.lcd_toggle_enable()

            # Low bits
            GPIO.output(LCD_D4, False)
            GPIO.output(LCD_D5, False)
            GPIO.output(LCD_D6, False)
            GPIO.output(LCD_D7, False)
            if bits & 0x01 == 0x01:
                GPIO.output(LCD_D4, True)
            if bits & 0x02 == 0x02:
                GPIO.output(LCD_D5, True)
            if bits & 0x04 == 0x04:
                GPIO.output(LCD_D6, True)
            if bits & 0x08 == 0x08:
                GPIO.output(LCD_D7, True)

            # Toggle 'Enable' pin
            self.lcd_toggle_enable()

        @staticmethod
        def lcd_toggle_enable():
            # Toggle enable
            time.sleep(E_DELAY)
            GPIO.output(LCD_E, True)
            time.sleep(E_PULSE)
            GPIO.output(LCD_E, False)
            time.sleep(E_DELAY)

        def lcd_string(self, message, line):
            # Cast to string
            message = str(message)
            # Send string to display
            message = message.ljust(LCD_WIDTH, " ")

            self.lcd_byte(line, LCD_CMD)

            for i in range(LCD_WIDTH):
                self.lcd_byte(ord(message[i]), LCD_CHR)

        def display(self):
            # Send some test
            self.lcd_string(" Ultracount  ", LCD_LINE_1)
            self.lcd_string("Setup Completed", LCD_LINE_2)
            time.sleep(3)  # 3 second delay


class Main:

    def __init__(self):
        self.__calibration_start_sensor(1)
        self.__calibration_start_sensor(2)
        self.__connect_oss()
        self.sensor_1 = self.bucket.append_object(OSS_object_name_1, 0, "")
        self.sensor_2 = self.bucket.append_object(OSS_object_name_1, 0, "")
        self.counting_mode = 0  # alternating counting mode
        self.abort_count = 0
        self.data1 = ""
        self.data2 = ""
        self.setting_gap = False
        self.sensor_1_get_time = self.sensor_2_get_time = 0
        self.stop = False  # progress_abort variables
        self.pause = False
        self.a1 = Thread(target=self.mono_counting)
        self.a2 = Thread(target=self.bi_counting)
        self.a3 = Thread(target=self.progress_abort)
        self.break_flag = False

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
        device.lcd_1.lcd_string("Sensor " + str(sensor_no) + " tuned", LCD_LINE_1)
        time.sleep(1)

    @staticmethod
    def commencement():
        def get_ip():
            cmd = "hostname -I"
            return check_output(cmd, shell=True).decode("utf-8").strip()

        def __wifi_check_status():
            GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            device.lcd_1.lcd_string("WiFiNotConnected", LCD_LINE_2)
            while True:
                GPIO.output(LED_1, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(LED_1, GPIO.LOW)
                time.sleep(0.5)
                if len(get_ip()) > 10:
                    GPIO.output(LED_1, GPIO.HIGH)
                    device.lcd_1.lcd_string("Wifi connected", LCD_LINE_1)
                    device.lcd_1.lcd_string(get_ip(), LCD_LINE_2)
                    time.sleep(10)
                    GPIO.output(LED_1, GPIO.LOW)
                    break

        __wifi_check_status()
        print("press button to commence the program")
        device.lcd_1.lcd_string("To be commenced", LCD_LINE_1)
        GPIO.wait_for_edge(BUTTON_1, GPIO.BOTH)

    def __connect_oss(self):
        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        self.auth = oss2.Auth(OSS_id, OSS_key)
        print('using %s : %s' % (OSS_id, OSS_key))
        # yourEndpoint填写Bucket所在地域对应的Endpoint。
        self.bucket = oss2.Bucket(self.auth, OSS_endpoint, OSS_bucket_name, connect_timeout=OSS_timeout)
        print("Success: %s:%s" % (OSS_endpoint, OSS_bucket_name))
        self.initialise_oss()

    def initialise_oss(self):
        if self.bucket.object_exists(OSS_object_name_1):
            self.bucket.delete_object(OSS_object_name_1)
        elif self.bucket.object_exists(OSS_object_name_2):
            self.bucket.delete_object(OSS_object_name_2)
        else:
            pass
        print("Initialised!")
        device.lcd_1.lcd_string("Initialised", LCD_LINE_2)

    def switch_control(self, initial):
        GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        device.lcd_1.lcd_string("Select mode", LCD_LINE_1)
        while True:
            if GPIO.input(BUTTON_1) == GPIO.HIGH:
                self.counting_mode = 1
                break
            if GPIO.input(BUTTON_2) == GPIO.HIGH:
                self.counting_mode = 2
                break
        if self.counting_mode == 1:
            self.reset_counter(1, True)
            self.a1 = Thread(target=self.mono_counting)
            self.a1.start()
            time.sleep(1)
        if self.counting_mode == 2:
            self.reset_counter(1, True)
            self.reset_counter(2, True)
            self.a2 = Thread(target=self.bi_counting)
            self.a2.start()
            time.sleep(1)
        if initial:
            self.a3 = Thread(target=self.progress_abort)
            self.a3.start()

    def progress_abort(self):
        GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        while True:
            if GPIO.input(BUTTON_1) == GPIO.HIGH:
                self.pause = True
                GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                device.lcd_1.lcd_string("1 - resume", LCD_LINE_1)
                device.lcd_1.lcd_string("2 - abort", LCD_LINE_2)
                while True:
                    if GPIO.input(BUTTON_1) == GPIO.HIGH: # resume
                        GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                        if self.counting_mode == 1:
                            device.lcd_1.lcd_string("Mono counting", LCD_LINE_1)
                            device.lcd_1.lcd_string("In Count: " + str(self.no_of_pedestrians_1), LCD_LINE_2)
                        if self.counting_mode == 2:
                            device.lcd_1.lcd_string("In: " + str(self.no_of_pedestrians_1) + " Out: "
                                                    + str(self.no_of_pedestrians_2), LCD_LINE_1)
                            device.lcd_1.lcd_string(
                                "Total: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                                LCD_LINE_2)
                        break
                    if GPIO.input(BUTTON_2) == GPIO.HIGH: # abort
                        GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                        device.lcd_1.lcd_string("1 - restart", LCD_LINE_1)
                        device.lcd_1.lcd_string("2 - terminate", LCD_LINE_2)
                        while not self.break_flag:
                            self.stop = True
                            if self.counting_mode == 1:
                                self.a1.join()
                            if self.counting_mode == 2:
                                self.a2.join()
                            if GPIO.input(BUTTON_1) == GPIO.HIGH:  # restart
                                GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                                self.break_flag = True
                                self.stop = False
                                device.__init__()
                                Main.commencement()
                                self.__init__()
                                self.switch_control(False)
                            if GPIO.input(BUTTON_2) == GPIO.HIGH:  # terminate
                                GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                                self.break_flag = True
                                device.lcd_1.lcd_byte(0x01, LCD_CMD)
                                device.lcd_1.lcd_string("Counting Ended", LCD_LINE_1)
                                time.sleep(1)
                                GPIO.cleanup()
                                sys.exit()
                        if self.break_flag:
                            self.break_flag = False
                            break
                self.pause = False
                GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                time.sleep(2)
            time.sleep(0.2)

    # constants to be declared
    count_1 = 0
    reset_count_1 = 0
    no_of_pedestrians_1 = 0
    pedestrian_detected_1 = False

    count_2 = 0
    reset_count_2 = 0
    no_of_pedestrians_2 = 0
    pedestrian_detected_2 = False

    no_of_pedestrians_total = 0

    def reset_counter(self, mode, boolean):
        if mode == 0:
            self.count_1 = 0
            self.reset_count_1 = 0
            self.count_2 = 0
            self.reset_count_2 = 0
        if mode == 1:
            self.count_1 = 0
            self.reset_count_1 = 0
            self.pedestrian_detected_1 = False
            if boolean:
                self.no_of_pedestrians_1 = 0
        if mode == 2:
            self.count_2 = 0
            self.reset_count_2 = 0
            self.pedestrian_detected_2 = False
            if boolean:
                self.no_of_pedestrians_2 = 0

    def mono_counting(self):
        time2 = time.time()
        device.lcd_1.lcd_string("Mono counting", LCD_LINE_1)  # display on lcd screen
        while not self.stop:
            while not self.stop and self.pause:
                print("pass")
                time.sleep(1)
                pass
            # sensor 1
            t1 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=24)
            duration_1 = time.time() - t1 - calibration_offset
            distance_1 = round(duration_1 * 17150, 2)

            if not self.setting_gap:
                if distance_1 < self.average_dist_1 - min_human_width:
                    self.count_1 += 1
                    self.reset_count_1 = 0
                elif self.pedestrian_detected_1:
                    self.reset_count_1 += 1
                    if self.reset_count_1 >= reset_threshold:
                        self.reset_counter(1, False)
                else:
                    self.count_1 = 0
                if self.count_1 >= detection_threshold and not self.pedestrian_detected_1:
                    self.no_of_pedestrians_1 += 1
                    self.pedestrian_detected_1 = True
                    self.setting_gap = True
                    device.lcd_1.lcd_string("In Count: " + str(self.no_of_pedestrians_1), LCD_LINE_2)
                    print("Pedestrian count: " + str(self.no_of_pedestrians_1))
            else:
                if distance_1 < self.average_dist_1 - min_human_width:
                    self.count_1 += 1
                    self.reset_count_1 = 0
                elif distance_1 > self.average_dist_1 - min_human_width and self.pedestrian_detected_1:
                    self.reset_count_1 += 1
                    if self.reset_count_1 >= reset_threshold:
                        self.reset_counter(1, False)
                        self.setting_gap = False
            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                self.write_file(1)
                time2 = time.time()
                print("written")

    setting_gap_1 = False
    setting_gap_2 = False

    def bi_counting(self):
        time2 = time.time()
        self.sensor_1_get_time = 0
        self.sensor_2_get_time = 0
        pseudo_count = 0
        device.lcd_1.lcd_string("Bidir counting", LCD_LINE_1)
        while not self.stop:
            while not self.stop and self.pause:
                pass
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
                elif self.pedestrian_detected_1:
                    self.reset_count_1 += 1
                    if self.reset_count_1 >= reset_threshold:
                        self.reset_counter(1, False)
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
                        self.reset_counter(1, False)
                        self.setting_gap_1 = False
                        print("sensor 1 resets")

            time.sleep(waiting_time)

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
                        self.reset_counter(2, False)
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
                        self.reset_counter(2, False)
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
                self.reset_counter(0, False)  # reset counting constants
                device.lcd_1.lcd_string("In: " + str(self.no_of_pedestrians_1) + " Out: "
                                        + str(self.no_of_pedestrians_2), LCD_LINE_1)
                device.lcd_1.lcd_string("Total: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                                        LCD_LINE_2)
                print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
            else:
                pass

            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                pass

    def write_file(self, mode):
        FileName_1 = "Gate1@Entrance.txt"
        FileName_2 = "Gate1@Exit.txt"
        if mode == 1:
            with open(FileName_1, "a") as test_file_1:
                test_file_1.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_1) + "\n")
        if mode == 2:
            with open(FileName_1, "a") as test_file_1:
                test_file_1.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_1) + "\n")
            with open(FileName_2, "a") as test_file_2:
                test_file_2.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_2) + "\n")

    def append_file(self, mode):
        self.data1 = str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_1) + "\n"
        self.data2 = str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_2) + "\n"
        if mode == 1:
            self.sensor_1 = self.bucket.append_object(OSS_object_name_1, self.sensor_1.next_position, self.data1)
            print("appended")
        if mode == 2:
            self.sensor_1 = self.bucket.append_object(OSS_object_name_1, self.sensor_1.next_position, self.data1)
            self.sensor_2 = self.bucket.append_object(OSS_object_name_2, self.sensor_2.next_position, self.data2)


# Set up ultrasonic sensor and lcd screen
device = Setup()

# check wifi connection before pressing button to commence the program
Main.commencement()

# instantiate the sensor and lcd functions
trial_1 = Main()

try:
    # using button to switch between alternative modes of counting (mono counting / bidirectional counting)
    trial_1.switch_control(True)

except KeyboardInterrupt:
    # Close the Connection
    device.lcd_1.lcd_byte(0x01, LCD_CMD)
    device.lcd_1.lcd_string("Counting Ended", LCD_LINE_1)
    print("clean up")
    time.sleep(2)
    GPIO.cleanup()
