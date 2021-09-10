from collections import deque
from io import BytesIO
import os
from pathlib import Path
from threading import Event
import time

from picamerax import PiCamera
import pigpio
from pydng.core import RPICAM2DNG

from notification import send_notification


class HallEffectSensor:

    def __init__(self, pi, input_pin):
        self.pi = pi
        self.input_pin = input_pin
        
        self.pi.set_mode(self.input_pin, pigpio.INPUT)
        
        self.armed = False
    
    def arm(self, callback):
        assert not self.armed, "Cannot arm armed Hall Effect sensor!"
        self.armed = True
        self.callback = callback
        self.pgpio_callback = self.pi.callback(self.input_pin, pigpio.RISING_EDGE, self.detect)
    
    def disarm(self):
        assert self.armed, "Can only disarm armed Hall Effect sensor!"
        self.pgpio_callback.cancel()
        self.armed = False

    def detect(self, pin, level, tick):
        print("HALL DETECT")
        self.callback()


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

    speeds = [320, 500, 800, 1000, 1600, 2000]

    def __init__(self, pi, enable_pin, direction_pin, step_pin):
        self.pi = pi
        self.enable_pin = enable_pin
        self.direction_pin = direction_pin
        self.step_pin = step_pin

        self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.direction_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)

        self.disable()
        self.pi.write(self.direction_pin, 0)    # Set direction counter-clockwise
        self.running = False
    
    def enable(self):
        self.pi.write(self.enable_pin, 0)
        self.is_enabled = True
    
    def disable(self):
        self.pi.write(self.enable_pin, 1)
        self.is_enabled = False

    def start(self, steps_per_second=1000, speed=4, acceleration=80):
        # Speed: Level of the speed, where speed in steps / second
        # Acceleration: In steps / second^2

        assert self.is_enabled, "Cannot start a disabled stepper motor!"

        self.running = True
        self.speed = speed
        self.acceleration = acceleration

        ramp_speeds = [speed for speed in self.speeds if speed <= steps_per_second]

        ramp = [(speed, int(speed/acceleration)) for speed in ramp_speeds[:-1]]
        ramp.append((ramp_speeds[-1], 10000))

        self.ramp = ramp
        print("ramp", ramp)

        self.generate_ramp(ramp)

    def stop(self):
        self.running = False

        ramp = list(reversed(self.ramp))

        self.generate_ramp(ramp)
    
    def generate_ramp(self, ramp):
        self.pi.wave_clear()
        length = len(ramp)
        wid = [-1] * length

        # Generate a wave ramp per ramp level
        for i in range(length):
            frequency = ramp[i][0]
            micros = int(5e5 / frequency)
            wf = []
            wf.append(pigpio.pulse(1<<self.step_pin, 0, micros))    # Pulse on
            wf.append(pigpio.pulse(0, 1<<self.step_pin, micros))    # Pulse off
            self.pi.wave_add_generic(wf)
            wid[i] = self.pi.wave_create()
        
        # Generate chain of waves
        chain = []
        for i in range(length):
            steps= ramp[i][1]
            x = steps & 255
            y = steps >> 8
            chain += [255, 0, wid[i], 255, 1, x, y]
        
        self.pi.wave_chain(chain)   # Transmit chain of wave forms


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

        self.last_steps = 0

    def __del__(self):
        self.motor.disable()
        self.backlight.turn_off()
        self.camera.close()
        
        self.pi.wave_clear()
        self.pi.stop()

    def advance(self):        
        self.motor.start()

        # Time = 0.487 seconds at 1/1000
        # time = 0.907 seconds at 1/500
        # dt = 0.907 * 1.025
        dt = 0.487 * 1.025


        # time.sleep(0.487)

        # time.sleep(0.1)
        t1 = time.time()
        time.sleep(dt * 0.25)

        frame_detected_event = Event()
        frame_detected_event.clear()

        self.frame_sensor.arm(callback=frame_detected_event.set)

        # was_frame_detected = frame_detected_event.wait(timeout=0.387)
        was_frame_detected = frame_detected_event.wait(timeout=dt*0.75)
        t2 = time.time()
        print(f"Took {t2-t1:.4f} / {dt:.4f} seconds (detected={was_frame_detected})")

        self.motor.stop()
        self.frame_sensor.disarm()

        if not was_frame_detected:
            raise ValueError(f"It seems the frame sensor was missed or the motor got stuck")
        
    def scan(self, output_directory, n_frames=3900, start_index=0):
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        d = RPICAM2DNG()
        frame_times = deque(maxlen=100)

        time.sleep(5)
        t_last = time.time()

        self.motor.enable()

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
        
        self.motor.disable()
        
        if not self.close_requested:
            send_notification(f"Finished scanning {i}/{n_frames}")
