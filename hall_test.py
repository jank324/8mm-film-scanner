import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)
HALL_PIN = 26
GPIO.setup(HALL_PIN, GPIO.IN)

triggered = False

def trigger(channel):
    print("trigger", channel)

def untrigger(channel):
    print("untrigger", channel)

GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=trigger)
# GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=untrigger)

while True:
    sleep(0.1)
