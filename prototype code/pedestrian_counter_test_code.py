import RPi.GPIO as GPIO
import time
import ftplib
from ftplib import FTP

FTP_HOST = "www.projectireye.com"
FTP_USER = "arduino1@projectireye.com"
FTP_PASS = "projectireye2.0"
FTP_TIMEOUT = 1000
FileName = "test"  # local filename to upload
FILE_UPDATE_FREQUENCY = 10
WRITE_FILE_FREQUENCY = 2.5

# time.time() -> Seconds since epoch
# connect to the FTP server

timeout = 0.0180  # about 3 meters
waiting_time = 0.00003
detection_threshold = 5
calibration_samples = 100
max_range = 300  # 3 meters
min_range = 100  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 5  # no of times the range is back to normal

# Rpi 3A USB-C supply
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND

GPIO.setmode(GPIO.BOARD)

# name input and output pins to refer to later in the code
TRIG = 16
ECHO = 18
print("Distance measurement in progress")

# set these ports as input and output
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)  # set the Trigger pin low
print("Waiting for sensors to settle")


class Count:
    def __init__(self):
        self.__calibration_start()
        self.__connect_ftp()
        self.test_file = None

    def __calibration_start(self):
        print("Calibration starts...")
        sum_of_measurement = 0
        pulse_begin = 0
        pulse_finish = 0
        for i in range(calibration_samples):
            GPIO.output(TRIG, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG, GPIO.LOW)
            time.sleep(0.00001)

            while GPIO.input(ECHO) == 0:
                pulse_begin = time.time()
            while GPIO.input(ECHO) == 1:
                pulse_finish = time.time()
            duration = pulse_finish - pulse_begin
            distance = round(duration * 17150, 2)
            print(str(distance))

            if max_range > distance > min_range:
                sum_of_measurement += distance
            else:
                sum_of_measurement += min_range
            i += 1
            time.sleep(0.01)
        print("Calibration ends...")
        self.average_dist = round(sum_of_measurement / calibration_samples, 2)
        print("Average range without pedestrian: " + str(self.average_dist) + " cm")

    def __connect_ftp(self):
        self.ftp = FTP(FTP_HOST)
        print('using %s : %s' % (FTP_USER, FTP_PASS))
        self.ftp.login(FTP_USER, FTP_PASS)
        print("Success: %s:%s" % (FTP_USER, FTP_PASS))

    def write_file(self):
        with open(FileName, "a") as test_file:
            test_file.write(str(int(time.time()*1000)) + " " + str(self.no_of_pedestrians) + "\n")

    def upload_file(self):
        with open(FileName, "rb") as file:
            # Use FTP's STOR command to upload the file
            self.ftp.storbinary(f"STOR {FileName}", file)
    # constants to be declared
    count = 0
    reset_count = 0
    no_of_pedestrians = 0
    pedestrian_detected = False

    def counting(self):
        pulse_end1 = 0
        pulse_start1 = 0
        time2 = time3 = time.time()
        while True:
            GPIO.output(TRIG, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG, GPIO.LOW)
            time.sleep(0.00001)

            while GPIO.input(ECHO) == 0:
                pulse_start1 = time.time()
            while GPIO.input(ECHO) == 1:
                pulse_end1 = time.time()
            duration = pulse_end1 - pulse_start1
            distance = duration * 17150

            if distance < self.average_dist - min_human_width:
                self.count += 1
                self.reset_count = 0
            elif self.pedestrian_detected:
                self.reset_count += 1
                if self.reset_count >= reset_threshold:
                    self.count = 0  # reset counter
                    self.reset_count = 0
                    self.pedestrian_detected = False
            else:
                self.count = 0
            if self.count >= detection_threshold and not self.pedestrian_detected:
                self.no_of_pedestrians += 1
                self.pedestrian_detected = True
                print("Pedestrian count: " + str(self.no_of_pedestrians))
            time.sleep(waiting_time)

            # upload file every UPDATE_FREQUENCY time
            time_now = time.time()
            if (time_now - time2) >= FILE_UPDATE_FREQUENCY:
                time2 = time_now
                self.upload_file()
                print("uploaded")
            if (time_now - time3) >= WRITE_FILE_FREQUENCY:
                time3 = time.time()
                self.write_file()
                print("written")


# instantiate the Count functions
trial_1 = Count()
try:
    trial_1.counting()
except ftplib.error_perm as error:
    if error:
        print('Login Failed')
except KeyboardInterrupt:
    # Close the Connection
    trial_1.ftp.quit()
