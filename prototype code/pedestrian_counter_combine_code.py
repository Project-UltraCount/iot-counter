import RPi.GPIO as GPIO
import time
import ftplib
from ftplib import FTP

# FTP constants to be declared
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
min_range = 75  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 5  # no of times the range is back to normal

# Rpi 3A USB-C supply
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND

GPIO.setmode(GPIO.BCM)

# setting up input and output pins
TRIG = 20  # Board: 38
ECHO = 21  # 40
LCD_RS = 25  # 22
LCD_E = 24  # 18
LCD_D4 = 23  # 16
LCD_D5 = 17  # 11
LCD_D6 = 18  # 12
LCD_D7 = 22  # 15
print("Device setup in progress")

# Define lcd constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

E_PULSE = 0.0005
E_DELAY = 0.0005


class Setup:

  @staticmethod
  def sensor():
      # set sensor ports as input and output
      GPIO.setup(TRIG, GPIO.OUT)
      GPIO.setup(ECHO, GPIO.IN)
      GPIO.output(TRIG, False)  # set the Trigger pin low
      print("Sensors have been set up")

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


class UltrasonicSensor:

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
          test_file.write(str(int(time.time() * 1000)) + " " + str(self.no_of_pedestrians) + "\n")

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
      lcd_1.lcd_string("No. of people:  ", LCD_LINE_1)  # display on lcd screen
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
              lcd_1.lcd_string(str(self.no_of_pedestrians), LCD_LINE_2)
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


class LCD:

  def __init__(self):
      self.lcd_init()
      self.display()
      self.test_file = None

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
      self.lcd_string(" Project IReye  ", LCD_LINE_1)
      self.lcd_string("    Presents    ", LCD_LINE_2)
      time.sleep(3)  # 3 second delay

      # Send some text
      self.lcd_string("Pedestrian Count", LCD_LINE_1)
      self.lcd_string("LCD Test", LCD_LINE_2)
      time.sleep(3)


# Set up ultrasonic sensor and lcd screen
Setup.sensor()
Setup.lcd()
lcd_1 = LCD()

# instantiate the sensor and lcd functions
trial_1 = UltrasonicSensor()
try:
  trial_1.counting()
except ftplib.error_perm as error:
  if error:
      print('Login Failed')
except KeyboardInterrupt:
  # Close the Connection
  trial_1.ftp.quit()
  lcd_1.lcd_byte(0x01, LCD_CMD)
  lcd_1.lcd_string("Counting Ended",LCD_LINE_1)
  print("clean up")
  GPIO.cleanup()
