import RPi.GPIO as GPIO
from time import sleep

DIRPIN, STEPPIN = 21, 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIRPIN, GPIO.OUT)
GPIO.setup(STEPPIN, GPIO.OUT)

GPIO.output(DIRPIN, GPIO.HIGH)
GPIO.output(STEPPIN, GPIO.LOW)
