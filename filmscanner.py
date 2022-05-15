from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import partial
from fractions import Fraction
from io import BytesIO
import logging
import os
from pathlib import Path
from threading import Event
import time

from picamerax import PiCamera
import pigpio

from utils import BaseCallback, CallbackList, Viewer


# Setup logging (to console)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class FilmScanner:

    def __init__(self, callback=BaseCallback()):
        self.callback = CallbackList(callback) if isinstance(callback, list) else callback
        self.callback.setup(self)

        self.pi = pigpio.pi()

        self.light = Light(6)
        self.motor = StepperMotor(16, 21, 20)
        self.frame_sensor = HallEffectSensor(26)

        self.camera = PiCamera(resolution=(800,600))
        self.camera.analog_gain = 1
        self.camera.digital_gain = 1
        # self.camera.exposure_mode = "off"
        self.camera.shutter_speed = int(1e6 * 1 / 250)    # 1/250
        self.camera.awb_mode = "off"
        self.camera.awb_gains = (Fraction(513,256), Fraction(703,256))
        time.sleep(2)

        self.is_advancing = False
        self.is_fast_forwarding = False
        self.is_scanning = False

        self.scan_started_event = Event()
        self.scan_stopped_event = Event()
        self.scan_stop_requested = False
        self.live_view_zoom_toggle_requested = False

        self.is_zoomed = False

        self.last_steps = 0

        self.img_stream = BytesIO()
        self.write_executor = ThreadPoolExecutor(max_workers=1)

        self.turn_on_light()

        self.is_liveview_active = False
        self.liveview_executor = ThreadPoolExecutor(max_workers=1)
        self.viewers = []
        self.liveview_stop_requested = False
        self.liveview_started_event = Event()
        self.liveview_stopped_event = Event()
        with open("placeholder_image.jpg", "rb") as f:
            self.preview_frame = f.read()
        
        self.zoom_toggled_event = Event()
        self.fast_forward_stopped_event = Event()
        
        self.scan_executor = ThreadPoolExecutor(max_workers=1)
        self.output_directory = "/media/pi/PortableSSD/test"
        self.n_frames = 3842
        self.scanned_frames = 0

    def __del__(self):
        self.turn_off_light()
        self.motor.disable()

        self.camera.close()

        del(self.motor)
        
        self.pi.stop()
    
    def start_scan(self, output_directory, n_frames, start_index=0):
        """
        Start a scan. The arguments are the same as those of `scan`.
        """
        logger.info(f"Starting scan (output_directory={output_directory} / frames={n_frames} / start_index={start_index})")
        self.scan_stop_requested = False
        self.is_scanning = True
        self.scan_started_event.clear()
        self.scan_executor.submit(
            self.debug_scan,
            output_directory=output_directory,
            n_frames=n_frames,
            start_index=start_index
        )
        self.scan_started_event.wait()
    
    def stop_scan(self):
        """
        Stop a scan prematurely. When called, the scanner will stop once the current frame finished
        scanning. This method returns only when the scan has actually been stopped.
        """
        logger.info("Stopping scan")
        self.scan_stopped_event.clear()
        self.scan_stop_requested = True
        self.scan_stopped_event.wait()
    
    def debug_scan(self, output_directory, n_frames=3900, start_index=0):
        """
        The same as `scan`, but exceptions are caught and printed to `stdout`.
        """
        try:
            self.scan(output_directory, n_frames, start_index)
        except Exception as e:
            print(f"AN ERROR HAS OCURRED: {e}")
    
    def scan(self, output_directory, n_frames=3900, start_index=0):
        """
        Scan a film reel frame-by-frame.

        Parameters
        ----------
        output_directory : string
            Directory that frames will be saved to. If the given directory does not exist, it will
            be created automatically.
        n_frames : int
            Number of frames on the reel. Try to figure out how much frames are in the reel you wish
            to scan and then add some frames for safety. A 15m (50 foot) reel has about 3600 frames,
            so to be save it it recommned to scan 3800 frames. Note that the actual number of frames scanned
            is `n_frames - start_index`.
        start_index: int, optional
            Frame index at which to start scanning if you are not scanning from the beginning.
            Reduces the number of frames scanning.
        """
        self.scan_started_event.set()

        logger.info("Setting up scan")

        self.output_directory = output_directory
        self.n_frames = n_frames

        self.turn_on_light()

        self.callback.on_scan_start()

        if self.is_liveview_active:
            self.stop_liveview()

        Path(output_directory).mkdir(parents=True, exist_ok=True)

        self.start_logging_to_output_directory()

        self.camera.resolution = (400, 300)

        time.sleep(5)
        t_start = time.time()
        t_last = t_start

        for i in range(start_index, n_frames):
            self.current_frame_number = i + 1

            filename = f"frame-{i:05d}.jpg"
            filepath = os.path.join(output_directory, filename)

            time.sleep(0.2)

            frame = self.capture_frame()
            self.wait_for_previous_save()
            self.submit_save_frame(frame, filepath)
            self.preview_frame = frame
            self.callback.on_frame_capture()

            t_now = time.time()
            dt = t_now - t_last
            fps = 1 / dt
            remaining_seconds = int((n_frames - i) / fps)
            remaining = timedelta(seconds=remaining_seconds)
            logger.info(f"Captured \"{filepath}\" ({fps:.2f} fps / {remaining} s remaining)")
            t_last = t_now

            if self.scan_stop_requested:
                break

        t = t_now - t_start
        fps = (i + 1) / t
        logger.info(f"Scanned {i+1} frames in {t:.2f} seconds ({fps:.2f} fps)")

        self.is_scanning = False
        self.callback.on_scan_end()

        self.scan_stopped_event.set()

        self.stop_logging_to_output_directory()

        if self.viewers:
            self.start_liveview()

        return i + 1
    
    def wait_for_previous_save(self):
        """
        If a frame is currently being saved, blocks until that save operation has finished.
        """
        # Wait for previous image to be saved if there was one
        if hasattr(self, "write_future"):
            _ = self.write_future.result()

    def submit_save_frame(self, frame, filepath):
        """
        Submit a frame for saving. Returns immediately while the frame is saved concurrently. Use
        `wait for previous save` to block until saving is finished. The arguments are the same as
        those of `save_frame`.
        """
        self.write_future = self.write_executor.submit(self.save_frame, frame, filepath)

    def advance(self, recover=True):
        """
        Advance film scanner by one frame.

        Parameters
        ----------
        recover : bool
            Set `true` to attempt to recevor the scanner when an error occurs during the advance.
        """
        self.is_advancing = True
        self.callback.on_advance_start()

        logger.debug("Advancing one frame")

        t_threshold = 0.487 * 1.025

        self.motor.enable()
        self.motor.start(speed=300, acceleration=24)
        time.sleep(t_threshold * 0.25)  # Move magnet out of range before arming Hall effect sensor
        was_frame_detected = self.frame_sensor.wait_for_trigger(timeout=t_threshold*0.75)
        self.motor.stop(deceleration=24)
        self.motor.disable()

        if not was_frame_detected:
            logger.error("Frame sensor was not reached in time")
            fixed = False
            if recover:
                fixed = self.recover()
            if not fixed:
                raise AdvanceTimeoutError()
        
        self.is_advancing = False
        self.callback.on_advance_end()
    
    def recover(self):
        """
        Attempt to recover the frame advance after an error has occurred.
        """
        attempts = 0
        pause = 1
        while True:
            logger.warning(f"Attempting frame sensor recovery (attempt={attempts}, pause={pause})")

            self.motor.direction = 1
            
            self.motor.enable()
            self.motor.start(speed=1, acceleration=1)
            self.frame_sensor.wait_for_trigger(timeout=1.0)
            self.motor.stop(deceleration=1)
            self.motor.disable()

            time.sleep(1)

            self.motor.direction = 0

            try:
                self.advance(recover=False)
            except AdvanceTimeoutError:
                if True: # attempts < 5:
                    attempts += 1
                    time.sleep(pause)
                    pause *= 2
                else:
                    return False
            else:
                return True
            
    def fast_forward(self, n=None):
        """
        Fast-forward a given number of frames or until stopped.

        Parameters
        ----------
        n : int
            Number of frames to advance. If set to `None`, fast-forward until stopped.
        """
        self.is_fast_forwarding = True
        self.callback.on_fast_forward_start()

        if n is None:
            logger.debug("Fast-forwarding until stopped")
            while not self.scan_stop_requested:
                self.advance()
            self.scan_stop_requested = False
        else:
            logger.debug(f"Fast-forwarding {n} frames")
            for _ in range(n):
                self.advance()
                if self.scan_stop_requested:
                    logger.debug("Stopping fast-forwarding early")
                    self.scan_stop_requested = False
                    break
        
        self.is_fast_forwarding = False
        self.fast_forward_stopped_event.set()
        self.callback.on_fast_forward_end()
            
    def capture_frame(self):
        """
        Capture the current frame.

        Returns
        -------
        frame : bytes
            JPEG encoded image with raw bayer data appended.
        """
        self.camera.shutter_speed = int(1e6 * 1 / 250)
        
        buffer = BytesIO()
        self.camera.capture(buffer, format="jpeg", bayer=True)

        buffer.seek(0)
        frame = buffer.read()

        return frame
    
    def save_frame(self, frame, filepath):
        """
        Save a frame to a the given path.

        Parameters
        ----------
        frame : bytes
            Frame to save encoded as bytes.
        filepath : str
            Path to save the frame to.
        """  
        with open(filepath, "wb") as f:
            f.write(frame)

        logger.debug(f"Saved {filepath}")
    
    @property
    def is_light_on(self):
        return self.light.is_on
    
    def turn_on_light(self):
        """
        Turn on the scanner's light.

        NOTE: Call this method instead of calling the light object directly in order to make sure
        that the callback is called.
        """
        self.light.turn_on()
        self.callback.on_light_on()
    
    def turn_off_light(self):
        """
        Turn off the scanner's light.

        NOTE: Call this method instead of calling the light object directly in order to make sure
        that the callback is called.
        """
        self.light.turn_off()
        self.callback.on_light_off()
    
    def toggle_light(self):
        """
        Toggle the scanner's light.

        NOTE: Call this method instead of calling the light directly in order to make sure that
        the callback is called.
        """
        if self.light.is_on:
            self.turn_off_light()
        else:
            self.turn_on_light()
    
    def start_logging_to_output_directory(self):
        """
        Start logging to `scan.log` file in the current output directory.
        
        Parameters
        ----------
        directory : str
            Directory to place the `scan.log` file in.
        """
        logpath = os.path.join(self.output_directory, "scan.log")

        self.scan_logging_handler = logging.FileHandler(logpath)
        self.scan_logging_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(message)s")
        self.scan_logging_handler.setFormatter(formatter)

        logger.addHandler(self.scan_logging_handler)
    
    def stop_logging_to_output_directory(self):
        """
        Stop logging to `scan.log` file in the current output directory.
        """
        if hasattr(self, "scan_logging_handler"):
            logger.removeHandler(self.scan_logging_handler)
    
    @property
    def preview_frame(self):
        return self._preview_frame
    
    @preview_frame.setter
    def preview_frame(self, value):
        self._preview_frame = value

        self.prune_viewers()
        self.notify_viewers()
    
    def prune_viewers(self):
        """
        Remove viewers that did not retreive the frame for longer than a threshold time.
        """
        now = datetime.now()
        self.viewers = [viewer for viewer in self.viewers if now - viewer.last_access < timedelta(minutes=1)]
        if not self.viewers and self.is_liveview_active:
            # TODO This could cause a race condition if a new viewer is added here (?)
            self.stop_liveview()

    def notify_viewers(self):
        """
        Notify viewers that a new frame is available.
        """
        for viewer in self.viewers:
            viewer.notify()
    
    def start_liveview(self):
        """
        Start a liveview to fill the preview frames.
        """
        logger.info("Starting liveview")
        self.is_liveview_active = True
        self.liveview_stop_requested = False
        self.liveview_started_event.clear()
        self.liveview_executor.submit(self.liveview)
        self.liveview_started_event.wait()
    
    def stop_liveview(self):
        """
        Stop the liveview from writing the preview frames.
        """
        logger.info("Stopping liveview")
        self.liveview_stopped_event.clear()
        self.liveview_stop_requested = True
        self.liveview_stopped_event.wait()
    
    def liveview(self):
        """
        Livewview function writing preview frames.
        """
        self.liveview_started_event.set()

        buffer = BytesIO()

        self.camera.resolution = (800, 600)
        
        for _ in self.camera.capture_continuous(buffer, format="jpeg", use_video_port=True):
            # TODO: Hack!
            self.camera.shutter_speed = int(1e6 * 1 / 100)

            if self.live_view_zoom_toggle_requested:
                if not self.is_zoomed:
                    self.is_zoomed = True
                    self.camera.zoom = (0.37, 0.37, 0.25, 0.25)
                    self.callback.on_zoom_in()
                else:
                    self.is_zoomed = False
                    self.camera.zoom = (0.0, 0.0, 1.0, 1.0)
                    self.callback.on_zoom_out()
                self.live_view_zoom_toggle_requested = False

            buffer.truncate()
            buffer.seek(0)
            frame = buffer.read()
            buffer.seek(0)

            self.preview_frame = frame

            if self.liveview_stop_requested:
                break
        
        self.is_liveview_active = False
        self.liveview_stopped_event.set()
            
    def preview(self):
        """
        Add a preview viewer and get its view.

        Returns
        -------
        view : generator
            Generator that yields preview frames when they become available.
        """
        # Activate liveview when not yet active (and not currently scanning)
        if not self.is_liveview_active and not self.is_scanning:
            self.start_liveview()

        viewer = Viewer(self)
        self.viewers.append(viewer)

        return viewer.view()
    
    def poweroff(self):
        """
        Turn the sanner off.
        """
        if self.is_scanning:
            self.stop_scan()
        if self.is_liveview_active:
            self.stop_liveview()
        
        os.system("sudo poweroff")


class AdvanceTimeoutError(Exception):
    """
    Raised when the the frame sensor was not reached within some threshold time. This may have
    one of two possible causes: (A) The magnet passed the Hall effect sensor undetected. (B) The
    motor skipped steps, for example because it got stuck.
    """
    def __init__(self):
        super().__init__(
            "Frame sensor not reached in time. It was either missed, or the motor got stuck.")


class HallEffectSensor:
    """
    Hall effect sensor interfaced via `pigpio`.

    Parameters
    ----------
    input_pin : int
        Broadcom number of the GPIO header pin receiving a digital signal from the sensor.
    
    Attributes
    ---------
    is_armed : bool
        Flag set to true when the sensor is armed, i.e. setup to call a callback function whenever
        the Hall effect is detected.
    """

    def __init__(self, input_pin):
        self.input_pin = input_pin
        
        self.pi = pigpio.pi()
        self.pi.set_mode(self.input_pin, pigpio.INPUT)
        
        self.is_armed = False
    
    def wait_for_trigger(self, timeout=None):
        frame_detected_event = Event()
        frame_detected_event.clear()

        self.arm(user_callback=frame_detected_event.set)

        has_detected = frame_detected_event.wait(timeout=timeout)
        if self.is_armed:
            self.disarm()

        return has_detected
    
    def arm(self, user_callback):
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
        self.callback = partial(self.sensor_callback, user_callback)
        self.pigpio_callback = self.pi.callback(self.input_pin, pigpio.RISING_EDGE, self.detect)
    
    def sensor_callback(self, user_callback):
        self.disarm()
        user_callback()
    
    def disarm(self):
        """
        Stop calling the callback function when the Hall effect is detected.
        """
        assert self.is_armed, "Can only disarm armed Hall Effect sensor!"
        self.pigpio_callback.cancel()
        self.is_armed = False

    def detect(self, pin, level, tick):
        """
        Internal callback for `pgpio` which calls the sensor's callback function.
        """
        logger.debug("Hall effect sensor detected")
        self.callback()


class Light:
    """
    Light controlled via `pigpio`.

    Parameters
    ----------
    switch_pin : int
        Broadcom number of the GPIO header pin used to turn the light on and off.
    
    Attributes
    ---------
    is_on : bool
        Flag representing the light's state, `True` when the light is on and `False` when it is off.
    """
    
    def __init__(self, switch_pin):
        self.switch_pin = switch_pin

        self.pi = pigpio.pi()
        self.pi.set_mode(self.switch_pin, pigpio.OUTPUT)
        
        self.turn_off()
    
    def turn_on(self):
        """
        Turn the light on.
        """
        self.pi.write(self.switch_pin, 0)
        self.is_on = True
    
    def turn_off(self):
        """
        Turn the light off.
        """
        self.pi.write(self.switch_pin, 1)
        self.is_on = False
    
    def toggle(self):
        """
        Toggle the light between on and off.
        """
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()


class StepperMotor:
    """
    Stepper motor controlled via `pigpio`.

    Parameters
    ----------
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

    STEPS_PER_ROUND = 200
    PWM_FREQUENCIES = [320, 500, 800, 1000, 1600, 2000]

    def __init__(self, enable_pin, direction_pin, step_pin):
        self.enable_pin = enable_pin
        self.direction_pin = direction_pin
        self.step_pin = step_pin

        self.pi = pigpio.pi()
        self.pi.set_mode(self.enable_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.direction_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)

        self.disable()
        self.direction = 0  # Set direction counter-clockwise
        self.speed = 0
    
    def __del__(self):
        self.pi.wave_clear()
    
    def enable(self):
        """
        Enable the stepper motor (and its holding force as well as ability to step).
        """
        self.pi.write(self.enable_pin, 0)
        self.is_enabled = True
    
    def disable(self):
        """
        Disable the stepper motor (and its holding force as well as ability to step).
        """
        self.pi.write(self.enable_pin, 1)
        self.is_enabled = False
    
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self.pi.write(self.direction_pin, value)

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

        pwm_frequency = self.rpm2hz(speed)
        pwm_acceleration = self.rpm2hz(acceleration)

        self.speed = speed

        ramp = self.make_ramp(pwm_frequency, pwm_acceleration, stay=10000)
        self.send_ramp(ramp)

    def stop(self, deceleration=24):
        """
        Stop the stepper motor.

        Parameters
        ----------
        deceleration : int, optional
            Deceleration with which to stop the motor in `rounds / (minute * second)`.
        """
        pwm_frequency = self.rpm2hz(self.speed)
        pwm_deceleration = self.rpm2hz(deceleration)

        self.speed = 0

        ramp = self.make_ramp(pwm_frequency, -pwm_deceleration)
        self.send_ramp(ramp)
    
    def rpm2hz(self, rpm):
        """
        Convert RPM to PWM frequency in Hz for this particular stepper motor.
        """
        return self.STEPS_PER_ROUND * rpm / 60
    
    def make_ramp(self, target_frequency, acceleration, stay=0):
        """
        Make list of `(frequency, step)` pairs to ramp up the motor and stay at the target speed
        for `stay` steps.
        """
        frequencies = [f for f in self.PWM_FREQUENCIES if f <= target_frequency]
        if not frequencies:
            frequencies = [self.PWM_FREQUENCIES[0]]

        ramp = [(speed, int(speed/abs(acceleration))) for speed in frequencies[:-1]]
        if stay > 0:
            ramp.append((frequencies[-1], stay))
        
        return ramp if acceleration > 0 else list(reversed(ramp))
    
    def send_ramp(self, ramp):
        """
        Send wave chain that describes list of `(frequency, step)` pairs to step pin.
        """
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
