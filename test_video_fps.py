from collections import deque
import time

import numpy as np
from picamerax import PiCamera


class FPSMeter:

    def __init__(self):
        self.t1 = time.time()
        self.t2 = time.time()
        self.fps_queue = deque(maxlen=30)
    
    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            self.t2 = time.time()
            fps = 1 / (self.t2 - self.t1)
            self.t1 = self.t2

            self.fps_queue.append(fps)
            
            print(f"FPS = {np.mean(self.fps_queue):.2f} - ({np.std(self.fps_queue):.2f})")


def main():
    with PiCamera() as camera:
        camera.resolution = (4032, 3040)
        camera.exposure_mode = "off"
        camera.analog_gain = 1
        camera.digital_gain = 1
        camera.shutter_speed = int(1e6 * 1 / 2000)    # 1/2000s
        camera.awb_mode = "tungsten"

        fps_meter = FPSMeter()
        camera.start_recording(fps_meter, format="mjpeg")
        camera.wait_recording(20)
        camera.stop_recording()


if __name__ == "__main__":
    main()
