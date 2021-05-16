import signal
import sys
from time import sleep

import picamera
import RPi.GPIO as GPIO

from machine import Circuit, HallEffectSensor, StepperMotor


close_requested = False

def cleanup_and_close(sig, frame):
    global close_requested
    close_requested = True

signal.signal(signal.SIGINT, cleanup_and_close)

GPIO.setmode(GPIO.BCM)

sleep(1)

circuit12v = Circuit(switch_pin=6)
circuit12v.turn_on()

motor = StepperMotor(enable_pin=16, direction_pin=21, step_pin=20)
sensor = HallEffectSensor(input_pin=26)

motor.enable()

# with picamera.PiCamera() as camera:
if True:
    # Run motor unless interupted
    i = 0
    photo_index = 249
    leaving = True
    while True:
        if sensor.rising_edge_detected and not leaving:
            motor.decelerate()
            print(f"Taking photo {photo_index} at {i}")
            # camera.capture(f"testrun/img{photo_index:05}.jpg")
            sleep(0.7)
            photo_index += 1
            i = 0
            leaving = True

            if close_requested:
                motor.disable()
                circuit12v.turn_off()
                GPIO.cleanup()
                sys.exit(0)
            else:
                motor.accelerate()
        
        if leaving and i > 200:
            leaving = False
            sensor.rising_edge_detected = False

        motor.step()
        i += 1
