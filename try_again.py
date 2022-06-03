#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Backup code
import time
import oss2
from threading import Thread

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

# setting up input and output pins
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
        self.__switch()
        self.__sensor()
        self.lcd_1 = self.LCD()

    @staticmethod
    def __switch():
        time.sleep(1)
        print("Switches have been set up")

    @staticmethod
    def __sensor():
        # set sensor ports as input and output
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
            print("LCD has been set up")

        def lcd_init(self):
            # Initialise display
            pass

        def lcd_byte(self):
            # Send byte to data pins
            # bits = data
            # mode = True  for character
            #        False for command

            # RS

            # High bits

            # Toggle 'Enable' pin
            self.lcd_toggle_enable()

            # Low bits
            self.lcd_toggle_enable()

        @staticmethod
        def lcd_toggle_enable():
            # Toggle enable
            time.sleep(E_DELAY)

            time.sleep(E_PULSE)

            time.sleep(E_DELAY)

        def lcd_string(self, message):
            # Cast to string
            message = str(message)
            # Send string to display
            message = message.ljust(LCD_WIDTH, " ")
            print(message)
            pass

        @staticmethod
        def display():
            # Send some test
            print(" Ultracount  ")
            print("Setup Completed")
            time.sleep(3)  # 3 second delay


class Main:

    def __init__(self):
        self.__connect_oss()
        self.counting_mode = 0  # alternating counting mode
        self.abort_count = 0
        self.data1 = ""
        self.data2 = ""
        self.setting_gap = False
        self.sensor_1_get_time = self.sensor_2_get_time = 0
        self.stop = False  # progress_abort variables
        self.pause = False
        self.sensor_1 = self.bucket.append_object(OSS_object_name_1, 0, "")
        self.sensor_2 = self.bucket.append_object(OSS_object_name_1, 0, "")
        self.a1 = Thread(target=self.mono_counting)
        self.a2 = Thread(target=self.bi_counting)
        self.a3 = Thread(target=self.progress_abort)
        self.break_flag = False

    @staticmethod
    def commencement():
        def get_ip():
            pass

        def __wifi_check_status():

            pass

        __wifi_check_status()
        print("press button to commence the program")

    def __connect_oss(self):
        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        # Aliyun account and accessKey
        self.auth = oss2.Auth(OSS_id, OSS_key)
        print('using %s : %s' % (OSS_id, OSS_key))
        # endpoint to the region where the bucket is located
        self.bucket = oss2.Bucket(self.auth, OSS_endpoint, OSS_bucket_name, connect_timeout=OSS_timeout)
        print("Success: %s:%s" % (OSS_endpoint, OSS_bucket_name))
        self.initialise_oss()
        pass

    def initialise_oss(self):
        if self.bucket.object_exists(OSS_object_name_1):
            pass
        if self.bucket.object_exists(OSS_object_name_2):
            pass
        else:
            pass
        print("Initialised!")

    def switch_control(self, initial):
        no = input("Select mode: ")
        while bool:
            if no == "1":
                self.counting_mode = 1
                break
            elif no == "2":
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
        pass

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
        device.lcd_1.lcd_string("Mono counting")  # display on lcd screen
        while not self.stop:
            while not self.stop and self.pause:
                print("pass")
                time.sleep(1)
                pass
            check_point = input("in = 1: ")
            if not self.setting_gap:
                if check_point == "1" and not self.pedestrian_detected_1:
                    self.no_of_pedestrians_1 += 1
                    self.pedestrian_detected_1 = True
                    self.setting_gap = True
                    print("In Count: " + str(self.no_of_pedestrians_1))
                    print("Pedestrian count: " + str(self.no_of_pedestrians_1))
            else:
                pass
            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                pass

    setting_gap_1 = False
    setting_gap_2 = False

    def bi_counting(self):
        time2 = time.time()
        print("Bidir counting")
        while not self.stop:
            while not self.stop and self.pause:
                pass
            check_point = input("in=1,out=2: ")
            wait_bool = True
            while wait_bool:
                if check_point == "1":
                    self.no_of_pedestrians_1 += 1
                    print("In Count: " + str(self.no_of_pedestrians_1) + " Out Count: " + str(self.no_of_pedestrians_2))
                    print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
                    wait_bool = False
                elif check_point == "2":
                    self.no_of_pedestrians_2 += 1
                    print("In Count: " + str(self.no_of_pedestrians_1) + " Out Count: " + str(self.no_of_pedestrians_2))
                    print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
                    wait_bool = False
                else:
                    check_point = input("in=1, out=2: ")
                # upload file every UPDATE_FREQUENCY time
                time_now = time.time()
                if (time_now - time2) >= 10:
                    # self.append_file(self.counting_mode)
                    print("updated")
                    time2 = time.time()
            time.sleep(waiting_time)

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
    print("clean up")
    time.sleep(2)
