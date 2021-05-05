import signal
import sys
from time import sleep

import RPi.GPIO as GPIO
from machine import StepperMotor, HallEffectSensor


close_requested = False

def cleanup_and_close(sig, frame):
    global close_requested
    close_requested = True

signal.signal(signal.SIGINT, cleanup_and_close)

GPIO.setmode(GPIO.BCM)

motor = StepperMotor(enable_pin=16, direction_pin=21, step_pin=20)
sensor = HallEffectSensor(input_pin=26)

motor.enable()

# Run motor unless interupted
i = 0
leaving = True
while True:
    if sensor.rising_edge_detected and not leaving:
        print(f"Taking photo at {i}")
        sleep(1)
        i = 0
        leaving = True

        if close_requested:
            motor.disable()
            GPIO.cleanup()
            sys.exit(0)
    
    if leaving and i > 200:
        leaving = False
        sensor.rising_edge_detected = False

    motor.step()
    i += 1

