from io import BytesIO
import time

from filmscanner import FilmScanner


waited = 0

scanner = FilmScanner()
scanner.camera.resolution = (1024, 768)

buffer = BytesIO()
t1 = time.time()
for _ in scanner.camera.capture_continuous(buffer, format="jpeg", use_video_port=True):
    # TODO: Hack!
    scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

    if waited == 6:
        time.sleep(3)

    buffer.truncate()
    buffer.seek(0)
    
    t2 = time.time()
    fps = 1 / (t2 - t1)
    t1 = t2

    print(f"Generated frame: camera_fps={scanner.camera.framerate}, true_fps={fps:.2f}")

    buffer.seek(0)

    waited += 1
