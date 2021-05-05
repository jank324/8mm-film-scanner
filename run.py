import RPi.GPIO as GPIO
from machine import Stepper
from time import sleep


GPIO.setmode(GPIO.BCM)

motor = Stepper(enable_pin=16, direction_pin=21, step_pin=20)

hallpin=26
GPIO.setup(hallpin, GPIO.IN)

motor.enable()

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

    motor.step()
    i += 1

