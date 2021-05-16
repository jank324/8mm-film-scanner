from time import sleep

import RPi.GPIO as GPIO

enpin = 16
dirpin = 21
steppin = 20
hallpin = 26

steps_per_rotation = 200
delay = 0.0009

GPIO.setmode(GPIO.BCM)
GPIO.setup(enpin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(dirpin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(steppin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(hallpin, GPIO.IN)

print("Enable motor")
GPIO.output(enpin, GPIO.LOW)

print("Set motor direction counter-clockwise")
GPIO.output(dirpin, GPIO.LOW)

print("Register hall effect detection")
hall_effect_detected = False
def hall_detected(channel):
    global hall_effect_detected
    hall_effect_detected = True
GPIO.add_event_detect(hallpin, GPIO.RISING, callback=hall_detected)

# Run motor unless interupted
i = 0
leaving = False
while True:
    if hall_effect_detected and not leaving:
        print(f"Taking photo at {i}")
        sleep(1)
        i = 0
        leaving = True
    
    if leaving and i > 200:
        leaving = False
        hall_effect_detected = False

    GPIO.output(steppin, GPIO.HIGH)
    sleep(delay)
    GPIO.output(steppin, GPIO.LOW)
    sleep(delay)
    i += 1
