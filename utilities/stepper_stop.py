import RPi.GPIO as GPIO
from time import sleep

ENABLE_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENABLE_PIN, GPIO.OUT)

GPIO.output(ENABLE_PIN, GPIO.HIGH)
