import RPi.GPIO as GPIO
from time import sleep

ENABLE_PIN = 16
DIRECTION_PIN = 21
STEP_PIN = 20

STEPS_PER_ROTATION = 200
DELAY = 0.0006

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(DIRECTION_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(STEP_PIN, GPIO.OUT, initial=GPIO.LOW)

# Enable stepper motor
GPIO.output(ENABLE_PIN, GPIO.LOW)
print("Motor enabled")

print("Set direction left")
# Set direction left
GPIO.output(DIRECTION_PIN, GPIO.LOW)

print("Stepper step output on HIGH")
while(True):
    GPIO.output(STEP_PIN, GPIO.HIGH)
