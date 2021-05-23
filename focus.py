from time import time

import cv2
import numpy as np
from picamera import PiCamera

from machine import FilmScanner


if __name__ == "__main__":

    scanner = FilmScanner()

    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 24

        focus_peaking = False

        bgr = np.empty((768,1024,3), dtype=np.uint8)

        for _ in camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            if focus_peaking:
                grey = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(grey, 0, 255)
                overlay = cv2.add(bgr, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))

                cv2.imshow("Live View", overlay)
            else:
                cv2.imshow("Live View", bgr)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("a"):
                scanner.advance()
            elif key == ord("f"):
                focus_peaking = not focus_peaking
        
        cv2.destroyAllWindows()
