#!/usr/bin/python
# import
import RPi.GPIO as GPIO
import time
from device.device_constants import LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7, \
    LCD_WIDTH, LCD_CMD, LCD_CHR, E_DELAY, E_PULSE, LCD_LINE_1, LCD_LINE_2

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # Use BOARD GPIO numbers

def lcd_setup():
    # Main program block
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # D4
    GPIO.setup(LCD_D5, GPIO.OUT)  # D5
    GPIO.setup(LCD_D6, GPIO.OUT)  # D6
    GPIO.setup(LCD_D7, GPIO.OUT)  # D7

    # Initialise display
    lcd_init()

def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
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
    lcd_toggle_enable()

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
    lcd_toggle_enable()


def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_display(message, line):
    # Cast to string
    message = str(message)
    # Send string to display
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def initialisation_success_display():
    # Send some test
    lcd_display(" Ultracount  ", LCD_LINE_1)
    lcd_display("Setup Completed", LCD_LINE_2)
    time.sleep(3)  # 3 second delay
