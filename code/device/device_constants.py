# setting up input and output pins
# The ultrasonic sensor (HC- SR04) has 4 pins,Vcc,  Trigger, Echo and GND
#  Vcc(Sensor)---> Rpi 5V pin
#  Trigger ------> Rpi pin 16 i.e.GPIO23
#  Echo ---------> Rpi pin 18 i.e.GPIO24
#  GND (Sensor)--> Rpi GND
# ultrasonic sensor 1 for entrance
TRIG_1 = 31  # Board: 38
ECHO_1 = 33  # 40
# ultrasonic sensor 2 for exit
TRIG_2 = 37  # 29
ECHO_2 = 35  # 31
# button to restart counting
BUTTON_1 = 12  # 36
BUTTON_2 = 21  # 32
# LED indicating successful Wifi connection
LED = 29  # 35
# LCD screen
LCD_RS = 16  # 22
LCD_E = 18  # 18
LCD_D4 = 22  # 16
LCD_D5 = 24  # 11
LCD_D6 = 26  # 12
LCD_D7 = 32  # 15

# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# constants for ultrasonic detection
timeout = 0.0180  # about 3 meters
waiting_time = 0.00003  # 30 microseconds
detection_threshold = 4
abortion_threshold = 1000
calibration_samples = 100
max_range = 300  # 3 meters
min_range = 70  # min_range can be adjusted according to the estimated distance
min_human_width = 30  # 30cm
reset_threshold = 4  # no of times the range is back to normal
calibration_offset = 0.00064  # calibration for ultrasonic distance measuring
