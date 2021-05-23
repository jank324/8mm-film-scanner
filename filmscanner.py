import os
from pathlib import Path
from time import sleep

import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO


class HallEffectSensor:

    def __init__(self, input_pin):
        self.input_pin = input_pin
        
        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.add_event_detect(self.input_pin, GPIO.RISING, callback=self.detect)

        self.reset()

    def detect(self, channel):
        self.has_detected = True
    
    def reset(self):
        self.has_detected = False


class Light:
    
    def __init__(self, switch_pin):
        self.switch_pin = switch_pin

        GPIO.setup(switch_pin, GPIO.OUT, initial=GPIO.LOW)

        self.is_on = False
    
    def turn_on(self):
        GPIO.output(self.switch_pin, GPIO.HIGH)
        self.is_on = True
    
    def turn_off(self):
        GPIO.output(self.switch_pin, GPIO.LOW)
        self.is_on = False


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


class FilmScanner:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.backlight = Light(6)
        self.motor = StepperMotor(16, 21, 20)
        self.frame_sensor = HallEffectSensor(26)

        self.camera = PiCamera()

        self.close_requested = False

    def __del__(self):
        self.motor.disable()
        self.backlight.turn_off()
        self.camera.close()
        
        GPIO.cleanup()

    def advance(self):
        self.motor.enable()

        self.motor.accelerate()

        for _ in range(200):
            self.motor.step()
        self.frame_sensor.reset()
        
        i = 0
        while not self.frame_sensor.has_detected:
            self.motor.step()
            i += 1
            if i > 300:
                raise ValueError(f"It seems the frame sensor was missed")

        self.motor.decelerate()

        self.motor.disable()

    def scan(self, output_directory, n_frames=3900, start_index=0):
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        self.camera.iso = 100

        sleep(2)

        for i in range(start_index, n_frames):
            filename = f"frame-{i:05d}.jpg"
            filepath = os.path.join(output_directory, filename)

            self.camera.capture(filepath, bayer=True)

            self.advance()

            if self.close_requested == True:
                break
