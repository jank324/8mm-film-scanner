from collections import deque
from io import BytesIO
import os
from pathlib import Path
import time

import numpy as np
from picamerax import PiCamera
from pydng.core import RPICAM2DNG
import RPi.GPIO as GPIO

from notification import send_notification


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
    
    def step(self, delay=None):
        if delay is None:
            delay = self.max_speed

        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(self.max_speed)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(self.max_speed)
        
    def decelerate(self, steps=10):
        for delay in np.linspace(self.max_speed, self.min_speed, steps):
            self.step(delay=delay)


class FilmScanner:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.backlight = Light(6)
        self.motor = StepperMotor(16, 21, 20)
        self.frame_sensor = HallEffectSensor(26)

        self.camera = PiCamera(resolution=(1024,768))
        self.camera.exposure_mode = "off"
        self.camera.analog_gain = 1
        self.camera.digital_gain = 1
        self.camera.shutter_speed = int(1e6 * 1 / 2000)    # 1/2000s
        self.camera.awb_mode = "tungsten"
        time.sleep(2)

        self.close_requested = False

        self.last_steps = 0

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
            if i > 260:
                raise ValueError(f"It seems the frame sensor was missed ({i} steps)")
        
        self.last_steps = i

        self.motor.decelerate()

        self.motor.disable()

    def scan(self, output_directory, n_frames=3900, start_index=0):
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        d = RPICAM2DNG()
        frame_times = deque(maxlen=100)

        time.sleep(5)
        t_last = time.time()

        for i in range(start_index, n_frames):
            filename = f"frame-{i:05d}.dng"
            filepath = os.path.join(output_directory, filename)

            self.camera.shutter_speed = int(1e6 * 1 / 2000)
            
            stream = BytesIO()
            self.camera.capture(stream, format="jpeg", bayer=True)
            
            stream.seek(0)
            dng = d.convert(stream)
            
            with open(filepath, "wb") as file:
                file.write(dng)
            
            fps = len(frame_times) / sum(frame_times) if len(frame_times) != 0 else 0
            print(f"Saved {filepath} ({self.last_steps} steps / {fps:.1f} fps)")

            try:
                self.advance()
            except ValueError as e:
                send_notification(f"ERROR: Exceeded advance step limit at frame {i}")
                raise e
            time.sleep(0.2)

            t_now = time.time()
            frame_times.append(t_now - t_last)
            t_last = t_now

            if self.close_requested:
                send_notification(f"Film scan was manually terminated at frame {i}")
                break
        
        if not self.close_requested:
            send_notification(f"Finished scanning {i}/{n_frames}")
