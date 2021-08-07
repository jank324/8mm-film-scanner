from collections import deque
from io import BytesIO
import os
from pathlib import Path
import time

import numpy as np
from picamerax import PiCamera
import pigpio
from pydng.core import RPICAM2DNG

from notification import send_notification


class HallEffectSensor:

    def __init__(self, pi, input_pin):
        self.pi = pi
        self.input_pin = input_pin
        
        self.pi.set_mode(self.input_pin, pigpio.INPUT)
        
        self.reset()
        self.armed = False
    
    def arm(self):
        assert not self.armed, "Cannot arm armed Hall Effect sensor!"
        self.armed = True
        self.reset()
        self.callback = self.pi.callback(self.input_pin, pigpio.RISING_EDGE, self.detect)
    
    def disarm(self):
        assert self.armed, "Can only disarm armed Hall Effect sensor!"
        self.callback.cancel()
        self.armed = False

    def detect(self, pin, level, tick):
        self.has_detected = True
    
    def reset(self):
        self.has_detected = False


class Light:
    
    def __init__(self, pi, switch_pin):
        self.pi = pi
        self.switch_pin = switch_pin

        self.pi.set_mode(self.switch_pin, pigpio.OUTPUT)
        
        self.turn_on()
    
    def turn_on(self):
        self.pi.write(self.switch_pin, 1)
        self.is_on = True
    
    def turn_off(self):
        self.pi.write(self.switch_pin, 0)
        self.is_on = False


class StepperMotor:

    def __init__(self, pi, enable_pin, direction_pin, step_pin):
        self.pi = pi
        self.enable_pin = enable_pin
        self.direction_pin = direction_pin
        self.step_pin = step_pin

        self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
        self.disable()
        
        self.pi.set_mode(self.direction_pin, pigpio.OUTPUT)
        self.pi.write(self.direction_pin, 0)    # Set motor direction counter-clockwise
        
        self.pi.set_PWM_dutycycle(self.step_pin, 0)
        self.pi.set_PWM_frequency(self.step_pin, 800)
    
    def enable(self):
        self.pi.write(self.enable_pin, 0)
        self.is_enabled = True
    
    def disable(self):
        self.pi.write(self.enable_pin, 1)
        self.is_enabled = False

    def start(self):
        assert self.is_enabled, "Cannot start a disabled stepper motor!"
        self.pi.set_PWM_dutycycle(self.step_pin, 128)

    def stop(self):
        self.pi.set_PWM_dutycycle(self.step_pin, 0)


class FilmScanner:

    def __init__(self):
        self.pi = pigpio.pi()

        self.backlight = Light(self.pi, 6)
        self.motor = StepperMotor(self.pi, 16, 21, 20)
        self.frame_sensor = HallEffectSensor(self.pi, 26)

        self.camera = PiCamera(resolution=(1024,768))
        self.camera.exposure_mode = "off"
        self.camera.analog_gain = 1
        self.camera.digital_gain = 1
        self.camera.shutter_speed = int(1e6 * 1 / 2000)    # 1/2000s
        self.camera.awb_mode = "tungsten"
        time.sleep(2)

        self.close_requested = False
        self.advanced_once = False

        self.last_steps = 0

    def __del__(self):
        self.motor.disable()
        self.backlight.turn_off()
        self.camera.close()
        
        self.pi.stop()

    def advance(self):
        self.motor.enable()
        
        t1 = time.time()
        self.motor.start()

        time.sleep(0.2)
        self.frame_sensor.reset()
        while False: # not self.frame_sensor.has_detected:
            t2 = time.time()
            if t2 - t1 > 0.58 and self.advanced_once:
                raise ValueError(f"It seems the frame sensor was missed or the motor got stuck")
        
        time.sleep(0.3)

        self.motor.stop()
        
        self.advanced_once = True

        # self.motor.accelerate()

        # for _ in range(200):
        #     self.motor.step()
        # self.frame_sensor.reset()
        
        # i = 0
        # while not self.frame_sensor.has_detected:
        #     self.motor.step()
        #     i += 1
        #     if i > 260:
        #         raise ValueError(f"It seems the frame sensor was missed ({i} steps)")
        
        # self.last_steps = i

        # self.motor.decelerate()

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
            
            # with open(filepath, "wb") as file:
            #     file.write(dng)
            
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
