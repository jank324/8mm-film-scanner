import cv2
import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO

from machine import Light


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    light = Light(6)

    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 24

        bgr = np.empty((768,1024,3), dtype=np.uint8)

        while True:
            camera.capture(bgr, format="bgr", use_video_port=True)
            cv2.imshow("Live View", bgr)

            if cv2.waitKey(1) == 27:
                break
        
        cv2.destroyAllWindows()

    GPIO.cleanup()
