import sys
from threading import Thread

import RPi.GPIO as GPIO
import time

from aliyun.thing_properties import device_properties
from device.device_constants import LCD_LINE_1, LCD_LINE_2, LED, TRIG_1, TRIG_2, ECHO_1, ECHO_2, BUTTON_1, BUTTON_2
from device.lcd import lcd_setup, lcd_display, initialisation_success_display, lcd_byte


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(BUTTON_1, GPIO.IN)
    GPIO.setup(BUTTON_2, GPIO.IN)
    GPIO.setup(TRIG_1, GPIO.OUT)
    GPIO.setup(ECHO_1, GPIO.IN)
    GPIO.output(TRIG_1, False)  # set the Trigger pin low
    GPIO.setup(TRIG_2, GPIO.OUT)
    GPIO.setup(ECHO_2, GPIO.IN)
    GPIO.output(TRIG_2, False)  # set the Trigger pin low
    lcd_setup()
    initialisation_success_display()

def wifi_check_status():
    lcd_display("WiFiNotConnected", LCD_LINE_2)
    while True:
        GPIO.output(LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED, GPIO.LOW)
        time.sleep(0.5)
        if len(device_properties.IpAddress) > 10:
            GPIO.output(LED, GPIO.HIGH)
            lcd_display("Wifi connected", LCD_LINE_1)
            lcd_display(device_properties.IpAddress, LCD_LINE_2)
            time.sleep(5)
            GPIO.output(LED, GPIO.LOW)
            break

def standby():
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    time.sleep(2)
    while not device_properties.RunningState:
        lcd_display("On standby", LCD_LINE_1)
        lcd_display("Press to restart", LCD_LINE_2)
        if GPIO.input(BUTTON_1) == GPIO.HIGH:
            device_properties.RunningState = 1
            break

def thread_start_listener():
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    Thread(target=button_listener).start()


def button_listener():
    while device_properties.RunningState:
        if GPIO.input(BUTTON_1) == GPIO.HIGH:
            GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            device_properties.RunningState = 0
            lcd_display("1 - Standby", LCD_LINE_1)
            lcd_display("2 - Quit", LCD_LINE_2)

            while True:
                time.sleep(1) # wait for 1 second
                if GPIO.input(BUTTON_1) == GPIO.HIGH:  # standby
                    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                    break
                if GPIO.input(BUTTON_2) == GPIO.HIGH:  # close program
                    clean_up()
                    sys.exit()
            time.sleep(1) # wait for 1 second

def clean_up():
    lcd_byte(0x01, False)
    lcd_display("Counting Ended", LCD_LINE_1)
    print("Counting ended")
    time.sleep(2)
    GPIO.cleanup()  # cleanup
