# Backup code
import RPi.GPIO as GPIO
import time
import urllib.request
import ftplib
from ftplib import FTP

# FTP constants to be declared
FTP_HOST = "www.projectireye.com"
FTP_USER = "arduino1@projectireye.com"
FTP_PASS = "projectireye2.0"
FTP_TIMEOUT = 1000
FileName_1 = "Gate1@Entrance"  # Sensor 1 data file
FileName_2 = "Gate1@Exit"  # Sensor 2 data file
FILE_UPDATE_FREQUENCY = 60
WRITE_FILE_FREQUENCY = 15

# time.time() -> Seconds since epoch
# connect to the FTP server
timeout = 0.0180  # about 3 meters
waiting_time = 0.00003
detection_threshold = 5
calibration_samples = 100
max_range = 300  # 3 meters
min_range = 70  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 5  # no of times the range is back to normal
calibration_offset = 0.00243  # calibration for ultrasonic distance measuring

# Rpi 3A USB-C supply
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# setting up input and output pins
# ultrasonic sensor 1 for entrance
TRIG_1 = 20  # Board: 38
ECHO_1 = 21  # 40
# ultrasonic sensor 2 for exit
TRIG_2 = 5  # 29
ECHO_2 = 6  # 31
# Button switch to commence the program / switch between alternate modes of measurement
BUTTON_1 = 16  # 36
BUTTON_2 = 12  # 32
# LED indicating successful Wifi connection
LED = 19  # 35
# LCD screen
LCD_RS = 25  # 22
LCD_E = 24  # 18
LCD_D4 = 23  # 16
LCD_D5 = 17  # 11
LCD_D6 = 18  # 12
LCD_D7 = 22  # 15

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
        self.__calibration_start_sensor_1()
        self.__calibration_start_sensor_2()
        self.__connect_ftp()
        self.mode = 0

    def __calibration_start_sensor_1(self):
        GPIO.setup(ECHO_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Sensor 1 calibration starts...")
        sum_of_measurement = 0
        for i in range(calibration_samples):
            t0 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=5000)
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
        device.lcd_1.lcd_string("Sensor 1 tuned", LCD_LINE_1)

    def __calibration_start_sensor_2(self):
        GPIO.setup(ECHO_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Sensor 2 calibration starts...")
        sum_of_measurement = 0
        for i in range(calibration_samples):
            t0 = time.time()
            GPIO.output(TRIG_2, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_2, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_2, GPIO.FALLING, timeout=5000)
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
        device.lcd_1.lcd_string("Sensor 2 tuned", LCD_LINE_1)

    @staticmethod
    def commencement():
        def __wifi_check_status():
            GPIO.setup(LED, GPIO.OUT)
            GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            connection_status = False  # initialise connection status for WiFi
            check_url = "https://www.google.com"
            if urllib.request.urlopen(check_url):
                device.lcd_1.lcd_string("WiFi connected", LCD_LINE_2)
                connection_status = True
                GPIO.output(LED, GPIO.HIGH)
            if connection_status is not True:
                device.lcd_1.lcd_string("WiFiNotConnected", LCD_LINE_2)
                while True:
                    GPIO.output(LED, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(LED, GPIO.LOW)
                    time.sleep(0.5)
                    if urllib.request.urlopen(check_url):
                        device.lcd_1.lcd_string("WiFi connected", LCD_LINE_2)
                        connection_status = True
                    if connection_status:
                        break
            else:
                GPIO.output(LED, GPIO.HIGH)

        __wifi_check_status()
        print("press button to commence the program")
        device.lcd_1.lcd_string("To be commenced", LCD_LINE_1)
        GPIO.wait_for_edge(BUTTON_1, GPIO.BOTH)

    def __connect_ftp(self):
        self.ftp = FTP(FTP_HOST)
        print('using %s : %s' % (FTP_USER, FTP_PASS))
        self.ftp.login(FTP_USER, FTP_PASS)
        print("Success: %s:%s" % (FTP_USER, FTP_PASS))
        device.lcd_1.lcd_string("FTP connected", LCD_LINE_1)

    def switch_control(self):
        GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        device.lcd_1.lcd_string("Select mode", LCD_LINE_1)
        while True:
            if GPIO.input(BUTTON_1) == GPIO.HIGH:
                self.mode = 1
                break
            if GPIO.input(BUTTON_2) == GPIO.HIGH:
                self.mode = 2
                break
        if self.mode == 1:
            self.mono_counting()
        if self.mode == 2:
            self.bi_counting()

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

    def mono_counting(self):
        time2 = time3 = time.time()
        device.lcd_1.lcd_string("Mono counting", LCD_LINE_1)  # display on lcd screen
        while True:
            # sensor 1
            t1 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=5000)
            duration_1 = time.time() - t1 - calibration_offset
            distance_1 = round(duration_1 * 17150, 2)

            if distance_1 < self.average_dist_1 - min_human_width:
                self.count_1 += 1
                self.reset_count_1 = 0
            elif self.pedestrian_detected_1:
                self.reset_count_1 += 1
                if self.reset_count_1 >= reset_threshold:
                    self.count_1 = 0  # reset counter
                    self.reset_count_1 = 0
                    self.pedestrian_detected_1 = False
            else:
                self.count_1 = 0
            if self.count_1 >= detection_threshold and not self.pedestrian_detected_1:
                self.no_of_pedestrians_1 += 1
                self.pedestrian_detected_1 = True
                device.lcd_1.lcd_string("In Count: " + str(self.no_of_pedestrians_1), LCD_LINE_2)
                print("Pedestrian count: " + str(self.no_of_pedestrians_1))
            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                time2 = time_now
                self.upload_file(1)
                print("uploaded")
            if (time_now - time3) >= WRITE_FILE_FREQUENCY:
                time3 = time.time()
                self.write_file(1)
                print("written")

    def bi_counting(self):
        time2 = time3 = time.time()
        device.lcd_1.lcd_string("Bidir counting", LCD_LINE_1)
        while True:
            # sensor 1
            t1 = time.time()
            GPIO.output(TRIG_1, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_1, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_1, GPIO.FALLING, timeout=5000)
            duration_1 = time.time() - t1 - calibration_offset
            distance_1 = round(duration_1 * 17150, 2)

            if distance_1 < self.average_dist_1 - min_human_width:
                self.count_1 += 1
                self.reset_count_1 = 0
            elif self.pedestrian_detected_1:
                self.reset_count_1 += 1
                if self.reset_count_1 >= reset_threshold:
                    self.count_1 = 0  # reset counter
                    self.reset_count_1 = 0
                    self.pedestrian_detected_1 = False
            else:
                self.count_1 = 0
            if self.count_1 >= detection_threshold and not self.pedestrian_detected_1:
                self.no_of_pedestrians_1 += 1
                self.pedestrian_detected_1 = True
                print("In Count: " + str(self.no_of_pedestrians_1))
                device.lcd_1.lcd_string("In: " + str(self.no_of_pedestrians_1) + " Out: " +
                                        str(self.no_of_pedestrians_2), LCD_LINE_1)
                device.lcd_1.lcd_string("Total: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                                        LCD_LINE_2)
                print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))

            # sensor 2
            t2 = time.time()
            GPIO.output(TRIG_2, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_2, GPIO.LOW)
            GPIO.wait_for_edge(ECHO_2, GPIO.FALLING, timeout=5000)
            duration_2 = time.time() - t2 - calibration_offset
            distance_2 = round(duration_2 * 17150, 2)

            if distance_2 < self.average_dist_2 - min_human_width:
                self.count_2 += 1
                self.reset_count_2 = 0
            elif self.pedestrian_detected_2:
                self.reset_count_2 += 1
                if self.reset_count_2 >= reset_threshold:
                    self.count_2 = 0  # reset counter
                    self.reset_count_2 = 0
                    self.pedestrian_detected_2 = False
            else:
                self.count_2 = 0
            if self.count_2 >= detection_threshold and not self.pedestrian_detected_2:
                self.no_of_pedestrians_2 += 1
                self.pedestrian_detected_2 = True

                print("Out Count: " + str(self.no_of_pedestrians_2))
                device.lcd_1.lcd_string("In: " + str(self.no_of_pedestrians_1) + " Out: "
                                        + str(self.no_of_pedestrians_2), LCD_LINE_1)
                device.lcd_1.lcd_string("Total: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2),
                                        LCD_LINE_2)
                print("Combined count: " + str(self.no_of_pedestrians_1 - self.no_of_pedestrians_2))
            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                time2 = time_now
                self.upload_file(2)
                print("uploaded")
            if (time_now - time3) >= WRITE_FILE_FREQUENCY:
                time3 = time.time()
                self.write_file(2)
                print("written")

    def write_file(self, mode):
        if mode == 1:
            with open(FileName_1, "a") as test_file_1:
                test_file_1.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_1) + "\n")
        if mode == 2:
            with open(FileName_1, "a") as test_file_1:
                test_file_1.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_1) + "\n")
            with open(FileName_2, "a") as test_file_2:
                test_file_2.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians_2) + "\n")

    def upload_file(self, mode):
        if mode == 1:
            with open(FileName_1, "rb") as file_1:
                self.ftp.storbinary(f"STOR {FileName_1}", file_1)
        if mode == 2:
            with open(FileName_1, "rb") as file_1:
                self.ftp.storbinary(f"STOR {FileName_1}", file_1)
            with open(FileName_2, "rb") as file_2:
                self.ftp.storbinary(f"STOR {FileName_2}", file_2)


# Set up ultrasonic sensor and lcd screen
device = Setup()

# check wifi connection before pressing button to commence the program
Main.commencement()

# instantiate the sensor and lcd functions
trial_1 = Main()

try:
    # using button to switch between alternative modes of counting (mono counting / bidirectional counting)
    trial_1.switch_control()

except ftplib.error_perm as error:
    if error:
        print('Login Failed')
except KeyboardInterrupt:
    # Close the Connection
    trial_1.ftp.quit()
    device.lcd_1.lcd_byte(0x01, LCD_CMD)
    device.lcd_1.lcd_string("Counting Ended", LCD_LINE_1)
    print("clean up")
    time.sleep(2)
    GPIO.cleanup()
