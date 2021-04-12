import RPi.GPIO as GPIO
from time import sleep

DIRPIN, STEPPIN = 21, 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIRPIN, GPIO.OUT)
GPIO.setup(STEPPIN, GPIO.OUT)

def set_direction_left():
    GPIO.output(DIRPIN, GPIO.LOW)

def set_direction_right():
    GPIO.output(DIRPIN, GPIO.HIGH)

def step(delay=0.005):
    GPIO.output(STEPPIN, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEPPIN, GPIO.LOW)
    sleep(delay)

set_direction_left()

while(True):
    step(delay=0.0025)

# GPIO.cleanup()
