from time import sleep

import RPi.GPIO as GPIO


relay_pin = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(relay_pin, GPIO.LOW)

GPIO.cleanup()
