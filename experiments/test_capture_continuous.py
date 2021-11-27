from collections import deque
from io import BytesIO
import time

import numpy as np
from picamerax import PiCamera


def main():
    with PiCamera() as camera:
        camera.resolution = (4032, 3040)
        camera.exposure_mode = "off"
        camera.analog_gain = 1
        camera.digital_gain = 1
        camera.shutter_speed = int(1e6 * 1 / 2000)    # 1/2000s
        camera.awb_mode = "tungsten"

        fps_queue = deque(maxlen=30)

        buffer = BytesIO()
        t1 = time.time()
        for _ in camera.capture_continuous(buffer, format="jpeg", use_video_port=True):
            # TODO: Hack!
            # camera.shutter_speed = int(1e6 * 1 / 2000)

            buffer.truncate()
            buffer.seek(0)
    
            t2 = time.time()
            fps = 1 / (t2 - t1)
            t1 = t2

            fps_queue.append(fps)
            
            print(f"FPS = {np.mean(fps_queue):.2f} - ({np.std(fps_queue):.2f})")


if __name__ == "__main__":
    main()
