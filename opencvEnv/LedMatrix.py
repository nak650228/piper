#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

RCLK  = 40 
SRCLK = 38 
SDI   = 37 

tab = [0xfe,0xfd,0xfb,0xf7,0xef,0xdf,0xbf,0x7f]
message_ok = [
                0x60,0x90,0x90,0x69,0x0A,0x0C,0x0A,0x09,
		]
message_question = [
                0x38,0x6C,0x44,0x08,0x10,0x10,0x00,0x10
                ]
message_smile = [
                0x3C,0x42,0xA5,0x81,0x81,0x99,0x42,0x3C
                ]
message_null = [
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                ]

def print_msg():
    print ('Program is running...')
    print ('Press Ctrl+C to end the program...')

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)    # Number GPIOs by its physical location
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    GPIO.output(SDI, GPIO.LOW)
    GPIO.output(RCLK, GPIO.LOW)
    GPIO.output(SRCLK, GPIO.LOW)

def hc595_in(dat):
    for bit in range(0, 8):	
        GPIO.output(SDI, 0x80 & (dat << bit))
        GPIO.output(SRCLK, GPIO.HIGH)
        GPIO.output(SRCLK, GPIO.LOW)

def hc595_out():
    GPIO.output(RCLK, GPIO.HIGH)
    GPIO.output(RCLK, GPIO.LOW)

def loop(message):
    for i in range(0, 100):
        for j in range(0, 8):
            hc595_in(message[j])
            hc595_in(tab[j])
            hc595_out()
            time.sleep(0.00125)

def display_message(message_info,interval):
    setup()
    
    for ltime in range(1,interval):
        loop(message_info) 
    loop(message_null)

def destroy():   # When program ending, the function is executed. 
	GPIO.cleanup()

if __name__ == '__main__':   # Program starting from here 
    print_msg()
    setup()
    try:
        display_message(message_smile,5)  
        display_message(message_question,5)
        display_message(message_ok,5)

    except KeyboardInterrupt:  
        destroy()  


