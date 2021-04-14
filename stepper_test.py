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

print("Motor disabled")
sleep(3)

# Enable stepper motor
GPIO.output(ENABLE_PIN, GPIO.LOW)
print("Motor enabled")
sleep(3)

print("Motor running")
# Set direction left
GPIO.output(DIRECTION_PIN, GPIO.LOW)

# Do roations
for i in range(5):
    print(f"Iteration {i}")
    for rotation in range(3):
        for step in range(STEPS_PER_ROTATION):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            sleep(DELAY)
            GPIO.output(STEP_PIN, GPIO.LOW)
            sleep(DELAY)
    sleep(1)

print("Motor stopped and enabled")
sleep(3)

# Disable stepper motor
GPIO.output(ENABLE_PIN, GPIO.HIGH)
print("Motor disabled")
sleep(3)

GPIO.cleanup()
