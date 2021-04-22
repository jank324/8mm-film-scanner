import RPi.GPIO as GPIO
from time import sleep

ENABLE_PIN = 16
DIRECTION_PIN = 21
STEP_PIN = 20
HALL_PIN = 26

STEPS_PER_ROTATION = 200
DELAY = 0.0008

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(DIRECTION_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(STEP_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(HALL_PIN, GPIO.IN)

print("Enable motor")
GPIO.output(ENABLE_PIN, GPIO.LOW)

print("Set motor direction counter-clockwise")
GPIO.output(DIRECTION_PIN, GPIO.LOW)

print("Register hall effect detection")
is_detected = False
was_detected = False
def hall_detected(channel):
    global is_detected
    global was_detected
    global i
    if not was_detected:
        print("Hall effect detected -> stopping motor at", i)
        is_detected = True
        sleep(1)
        is_detected = False
        was_detected = True
        i = 0
GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=hall_detected)

# Run motor unless interupted
i = 0
while True:
    if not is_detected:
        GPIO.output(STEP_PIN, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        sleep(DELAY)
        i += 1
    if i > 100 and was_detected:
        was_detected = False
