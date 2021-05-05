from time import sleep

import RPi.GPIO as GPIO

enpin = 16
dirpin = 21
steppin = 20
hallpin = 26

steps_per_rotation = 200
delay = 0.0015

GPIO.setmode(GPIO.BCM)
GPIO.setup(enpin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(dirpin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(steppin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(hallpin, GPIO.IN)

print("Enable motor")
GPIO.output(enpin, GPIO.LOW)

print("Set motor direction counter-clockwise")
GPIO.output(dirpin, GPIO.LOW)

# Run motor
while True:
    GPIO.output(steppin, GPIO.HIGH)
    sleep(delay)
    GPIO.output(steppin, GPIO.LOW)
    sleep(delay)
