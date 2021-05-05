import RPi.GPIO as GPIO
from machine import StepperMotor, HallEffectSensor
from time import sleep


GPIO.setmode(GPIO.BCM)

motor = StepperMotor(enable_pin=16, direction_pin=21, step_pin=20)
sensor = HallEffectSensor(input_pin=26)

motor.enable()

# Run motor unless interupted
i = 0
leaving = False
while True:
    if sensor.rising_edge_detected and not leaving:
        print(f"Taking photo at {i}")
        sleep(1)
        i = 0
        leaving = True
    
    if leaving and i > 200:
        leaving = False
        sensor.rising_edge_detected = False

    motor.step()
    i += 1

