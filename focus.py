import cv2
import numpy as np
from picamera import PiCamera
import RPi.GPIO as GPIO

from machine import FilmScanner


if __name__ == "__main__":

    scanner = FilmScanner()

    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 24

        bgr = np.empty((768,1024,3), dtype=np.uint8)

        for _ in camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            cv2.imshow("Live View", bgr)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("a"):
                scanner.advance()
        
        cv2.destroyAllWindows()
