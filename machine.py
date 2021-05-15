from time import sleep

import numpy as np
import RPi.GPIO as GPIO


class StepperMotor:

    min_speed = 0.001
    max_speed = 0.0009

    def __init__(self, enable_pin, direction_pin, step_pin):
        self.enable_pin = enable_pin
        self.direction_pin = direction_pin
        self.step_pin = step_pin

        GPIO.setup(self.enable_pin, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.direction_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.step_pin, GPIO.OUT, initial=GPIO.LOW)

        self.enabled = False

        # Set motor direction counter-clockwise
        GPIO.output(self.direction_pin, GPIO.LOW)
    
    def enable(self):
        GPIO.output(self.enable_pin, GPIO.LOW)
        self.enabled = True
    
    def disable(self):
        GPIO.output(self.enable_pin, GPIO.LOW)
        self.enabled = False
    
    def accelerate(self, steps=10):
        for delay in np.linspace(self.min_speed, self.max_speed, steps):
            self.step(delay=delay)
    
    def step(self, delay=0.0009):
        GPIO.output(self.step_pin, GPIO.HIGH)
        sleep(self.max_speed)
        GPIO.output(self.step_pin, GPIO.LOW)
        sleep(self.max_speed)
        
    def decelerate(self, steps=10):
        for delay in np.linspace(self.max_speed, self.min_speed, steps):
            self.step(delay=delay)


class HallEffectSensor:

    def __init__(self, input_pin):
        self.input_pin = input_pin
        self.rising_edge_detected = False
        
        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.add_event_detect(self.input_pin, GPIO.RISING, callback=self.detect_rising_edge)

    def detect_rising_edge(self, channel):
        self.rising_edge_detected = True
