from collections import deque
from io import BytesIO
import logging
import os
from pathlib import Path
from threading import Event
import time

from picamerax import PiCamera
import pigpio
from pydng.core import RPICAM2DNG


# Setup logging (to console)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class HallEffectSensor:
    """
    Hall effect sensor interfaced via `pigpio`.

    Parameters
    ----------
    pi : pigpio.pi
        Raspberry Pi that the stepper motor is connected to.
    input_pin : int
        Broadcom number of the GPIO header pin receiving a digital signal from the sensor.
    
    Attributes
    ---------
    is_armed : bool
        Flag set to true when the sensor is armed, i.e. setup to call a callback function whenever
        the Hall effect is detected.
    """

    def __init__(self, pi, input_pin):
        self._pi = pi
        self._input_pin = input_pin
        
        self._pi.set_mode(self._input_pin, pigpio.INPUT)
        
        self.is_armed = False
    
    def arm(self, callback):
        """
        Setup the sensor to run a callback function whenever the Hall effect is detected.

        Parameters
        ----------
        callback : function
            Callback function that is called everytime the sensor detects the Hall effect. The
            function should receive no parameters nor return anything.
        """
        assert not self.is_armed, "Cannot arm armed Hall Effect sensor!"
        self.is_armed = True
        self._callback = callback
        self._pgpio_callback = self._pi.callback(self._input_pin, pigpio.RISING_EDGE, self._detect)
    
    def disarm(self):
        """Stop calling the callback function when the Hall effect is detected."""
        assert self.is_armed, "Can only disarm armed Hall Effect sensor!"
        self._pgpio_callback.cancel()
        self.is_armed = False

    def _detect(self, pin, level, tick):
        """Internal callback for `pgpio` which calls the sensor's callback function."""
        logger.debug("Hall effect sensor detected")
        self._callback()


class Light:
    """
    Light controlled via `pigpio`.

    Parameters
    ----------
    pi : pigpio.pi
        Raspberry Pi that the stepper motor is connected to.
    switch_pin : int
        Broadcom number of the GPIO header pin used to turn the light on and off.
    
    Attributes
    ---------
    is_on : bool
        Flag representing the light's state, `True` when the light is on and `False` when it is off.
    """
    
    def __init__(self, pi, switch_pin):
        self.pi = pi
        self.switch_pin = switch_pin

        self.pi.set_mode(self.switch_pin, pigpio.OUTPUT)
        
        self.turn_on()
    
    def turn_on(self):
        """Turn the light on."""
        self.pi.write(self.switch_pin, 1)
        self.is_on = True
    
    def turn_off(self):
        """Turn the light off."""
        self.pi.write(self.switch_pin, 0)
        self.is_on = False


class StepperMotor:
    """
    Stepper motor controlled via `pigpio`.

    Parameters
    ----------
    pi : pigpio.pi
        Raspberry Pi that the stepper motor is connected to.
    enable_pin : int
        Broadcom number of the GPIO header pin connected to the stepper driver's `SLEEP` input.
    direction_pin : int
        Broadcom number of the GPIO header pin connected to the stepper driver's `DIR` input.
    step_pin : int
        Broadcom number of the GPIO header pin connected to the stepper driver's `STEP` input.
    
    Attributes
    ---------
    is_enabled : bool
        Enable status of the motor. The motor must be enabled to provide a holding force or be able
        to run.
    speed : int
        Current speed of the motor in RPM.
    """

    _STEPS_PER_ROUND = 200
    _PWM_FREQUENCIES = [320, 500, 800, 1000, 1600, 2000]

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
        self.speed = 0
    
    def __del__(self):
        self.pi.wave_clear()
    
    def enable(self):
        """Enable the stepper motor (and its holding force as well as ability to step)."""
        self.pi.write(self.enable_pin, 0)
        self.is_enabled = True
    
    def disable(self):
        """Disable the stepper motor (and its holding force as well as ability to step)."""
        self.pi.write(self.enable_pin, 1)
        self.is_enabled = False

    def start(self, speed=300, acceleration=24):
        """
        Start running the stepper motor.

        Parameters
        ----------
        speed : int, optional
            Desired target speed to run at in RPM. The achieved motor speed may be slightly slower.
        acceleration : int, optional
            Acceleration with which to approach the target speed in `rounds / (minute * second)`.
        """

        assert self.is_enabled, "Cannot start a disabled stepper motor!"

        pwm_frequency = self._rpm2hz(speed)
        pwm_acceleration = self._rpm2hz(acceleration)

        self.speed = speed

        ramp = self._make_ramp(pwm_frequency, pwm_acceleration, stay=10000)
        self._send_ramp(ramp)

    def stop(self, deceleration=24):
        """
        Stop the stepper motor.

        Parameters
        ----------
        deceleration : int, optional
            Deceleration with which to stop the motor in `rounds / (minute * second)`.
        """
        pwm_frequency = self._rpm2hz(self.speed)
        pwm_deceleration = self._rpm2hz(deceleration)

        self.speed = 0

        ramp = self._make_ramp(pwm_frequency, -pwm_deceleration)
        self._send_ramp(ramp)
    
    def _rpm2hz(self, rpm):
        """Convert RPM to PWM frequency in Hz for this particular stepper motor."""
        return self._STEPS_PER_ROUND * rpm / 60
    
    def _make_ramp(self, target_frequency, acceleration, stay=0):
        """
        Make list of `(frequency, step)` pairs to ramp up the motor and stay at the target speed
        for `stay` steps.
        """
        frequencies = [f for f in self._PWM_FREQUENCIES if f <= target_frequency]

        ramp = [(speed, int(speed/abs(acceleration))) for speed in frequencies[:-1]]
        if stay > 0:
            ramp.append((frequencies[-1], stay))
        
        return ramp if acceleration > 0 else list(reversed(ramp))
    
    def _send_ramp(self, ramp):
        """Send wave chain that describes list of `(frequency, step)` pairs to step pin."""
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

    class AdvanceTimeoutError(Exception):
        """
        Raised when the the frame sensor was not reached within some threshold time. This may have
        one of two possible causes: (A) The magnet passed the Hall effect sensor undetected. (B) The
        motor skipped steps, for example because it got stuck.
        """
        def __init__(self):
            super().__init__("Frame sensor not reached in time. It was either missed, or the motor "
                             "got stuck.")

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

        self._dng_converter = RPICAM2DNG()

        self._stop_requested = False

        self.last_steps = 0

        self.backlight.turn_on()
        self.motor.enable()

    def __del__(self):
        self.backlight.turn_off()
        self.motor.disable()

        self.camera.close()

        del(self.motor)
        
        self.pi.stop()
    
    def scan(self, output_directory, n_frames=3900, start_index=0):
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        self._setup_logging_to_file(output_directory)

        logger.info(f"Start scanning frames {start_index} to {n_frames} into \"{output_directory}\"")

        time.sleep(5)
        t_start = time.time()
        t_last = t_start

        for i in range(start_index, n_frames):
            filename = f"frame-{i:05d}.dng"
            filepath = os.path.join(output_directory, filename)

            time.sleep(0.2)

            self.capture_frame(filepath)

            t_now = time.time()
            dt = t_now - t_last
            fps = 1 / dt
            logger.info(f"Captured \"{filepath}\" ({fps:.2f} fps)")
            t_last = t_now
            
            self.advance()

            if self._stop_requested:
                break

        t = t_now - t_start
        fps = (i + 1) / t
        logger.info(f"Scanned {i+1} frames in {t:.2f} seconds ({fps:.2f} fps)")

        return i + 1

    def advance(self, n=1):
        t_threshold = 0.487 * 1.025

        for _ in range(n):
            self.motor.start(speed=300, acceleration=24)

            time.sleep(t_threshold * 0.25)  # Move magnet out of range before arming Hall effect sensor

            frame_detected_event = Event()
            frame_detected_event.clear()

            self.frame_sensor.arm(callback=frame_detected_event.set)

            was_frame_detected = frame_detected_event.wait(timeout=t_threshold*0.75)

            self.motor.stop(deceleration=24)
            self.frame_sensor.disarm()

            if not was_frame_detected:
                raise FilmScanner.AdvanceTimeoutError()
            
            if self._stop_requested:
                break
        
        logger.debug(f"Advanced {n} frames")
    
    def capture_frame(self, filepath):
        self.camera.shutter_speed = int(1e6 * 1 / 2000)
            
        stream = BytesIO()
        self.camera.capture(stream, format="jpeg", bayer=True)
        
        stream.seek(0)
        dng = self._dng_converter.convert(stream)
        
        with open(filepath, "wb") as file:
            file.write(dng)

        logger.debug(f"Saved {filepath}")
    
    def stop(self):
        self._stop_requested = True
        logger.info("Stop requested")
    
    def _setup_logging_to_file(self, directory):
        logpath = os.path.join(directory, "scanner.log")

        file_handler = logging.FileHandler(logpath)
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
