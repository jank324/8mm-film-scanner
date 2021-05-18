from time import sleep

import cv2
from imutils.video.pivideostream import PiVideoStream
import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO


class HallEffectSensor:

    def __init__(self, input_pin):
        self.input_pin = input_pin
        self.rising_edge_detected = False
        
        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.add_event_detect(self.input_pin, GPIO.RISING, callback=self.detect_rising_edge)

    def detect_rising_edge(self, channel):
        self.rising_edge_detected = True


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
        
        # self.camera = PiCamera()
        # self.video_stream = PiVideoStream(resolution=(1024,768))
        # self.video_stream.start()

        self.close_requested = False

    def __del__(self):
        self.motor.disable()
        self.backlight.turn_off()
        # self.camera.close()
        
        GPIO.cleanup()
    
    def current_frame(self):
        frame = cv2.imread("mercedes_a-class_review31.jpg", cv2.IMREAD_COLOR)
    #     frame = self.video_stream.read()
        _, jpeg = cv2.imencode(".jpg", frame)
        jpeg_bytes = jpeg.tobytes()
        packaged = b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n\r\n"
        return packaged
    #     while True:
    #         yield packaged

    def advance(self):
        if not self.motor.enabled:
            self.motor.enable()

        self.motor.accelerate()

        for _ in range(200):
            self.motor.step()
        self.frame_sensor.rising_edge_detected = False
        
        while not self.frame_sensor.rising_edge_detected:
            self.motor.step()
        
        self.motor.decelerate()

    def run(self, capture=False):
        # self.backlight.turn_on()
        sleep(1)
        self.motor.enable()

        # Run motor unless interupted
        i = 0
        photo_index = 249
        leaving = True
        while True:
            if self.frame_sensor.rising_edge_detected and not leaving:
                self.motor.decelerate()
                print(f"Taking photo {photo_index} at {i}")
                if capture:
                    self.camera.capture(f"testrun/img{photo_index:05}.jpg")
                else:
                    sleep(0.7)
                photo_index += 1
                i = 0
                leaving = True

                if self.close_requested:
                    self.motor.disable()
                    self.backlight.turn_off()
                    break
                else:
                    self.motor.accelerate()
            
            if leaving and i > 200:
                leaving = False
                self.frame_sensor.rising_edge_detected = False

            self.motor.step()
            i += 1
