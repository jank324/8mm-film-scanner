import RPi.GPIO as GPIO
from time import sleep

ENABLE_PIN = 16
DIRECTION_PIN = 21
STEP_PIN = 20
HALL_PIN = 26

STEPS_PER_ROTATION = 200
DELAY = 0.03

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(DIRECTION_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(STEP_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(HALL_PIN, GPIO.IN)

print("Enable motor")
GPIO.output(ENABLE_PIN, GPIO.HIGH)

print("Set motor direction counter-clockwise")
GPIO.output(DIRECTION_PIN, GPIO.LOW)

# Run motor and read hall effect sensor
i = 0
while True:
    i += 1
    print(f"{i} {'Magnet detected' if GPIO.input(HALL_PIN) else 'no magnet'}")
    if GPIO.input(HALL_PIN):
        print(f"{i} Magnet detected")
    else:
        print

    # GPIO.output(STEP_PIN, GPIO.HIGH)
    # sleep(DELAY)
    # GPIO.output(STEP_PIN, GPIO.LOW)
    # sleep(DELAY)
