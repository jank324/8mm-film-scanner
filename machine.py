from time import sleep

import numpy as np
import RPi.GPIO as GPIO


class Circuit:
    
    def __init__(self, switch_pin, loads):
        self.switch_pin = switch_pin
        self.is_on = False
        self.loads = loads

        GPIO.setup(self.switch_pin, GPIO.OUT, initial=GPIO.LOW)

        for load in loads:
            load.circuit = self
    
    def turn_on(self):
        self.is_on = True
        GPIO.output(self.switch_pin, GPIO.HIGH)
    
    def turn_off(self):
        self.is_on = False
        GPIO.output(self.switch_pin, GPIO.LOW)
    
    def suggest_turn_off(self):
        if all(not load.is_on for load in self.loads):
            self.turn_off()


class HallEffectSensor:

    def __init__(self, input_pin):
        self.input_pin = input_pin
        self.rising_edge_detected = False
        
        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.add_event_detect(self.input_pin, GPIO.RISING, callback=self.detect_rising_edge)

    def detect_rising_edge(self, channel):
        self.rising_edge_detected = True


class Light:
    
    def __init__(self):
        self.is_on = False
    
    def turn_on(self):
        if self.circuit is not None:
            self.circuit.turn_on()
        
        self.is_on = True
    
    def turn_off(self):
        self.is_on = False

        if self.circuit is not None:
            self.circuit.suggest_turn_off()


class StepperMotor:

    min_speed = 0.001
    max_speed = 0.0006

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
    
    @property
    def is_on(self):
        return self.enabled
    
    def enable(self):
        if self.circuit is not None:
            self.circuit.turn_on()

        GPIO.output(self.enable_pin, GPIO.LOW)
        self.enabled = True
    
    def disable(self):
        GPIO.output(self.enable_pin, GPIO.LOW)
        self.enabled = False

        if self.circuit is not None:
            self.circuit.suggest_turn_off()
    
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
