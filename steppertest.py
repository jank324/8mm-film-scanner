import RPi.GPIO as GPIO
from time import sleep

DIRPIN, STEPPIN = 21, 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIRPIN, GPIO.OUT)
GPIO.setup(STEPPIN, GPIO.OUT)

GPIO.output(DIRPIN, GPIO.HIGH)

def step():
    DELAY = 0.005
    GPIO.output(STEPPIN, GPIO.HIGH)
    sleep(DELAY)
    GPIO.output(STEPPIN, GPIO.LOW)
    sleep(DELAY)

for i in range(200):
    step()
    print(i)

GPIO.output(DIRPIN, GPIO.LOW)
for i in range(400):
    step()
    print(i)

GPIO.cleanup()