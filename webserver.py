from io import BytesIO
import time

import cv2
from flask import Flask, render_template, Response

from filmscanner import FilmScanner


app = Flask(__name__)
scanner = FilmScanner()
scanner.camera.resolution = (1024, 768)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/advance", methods=["POST"])
def advance():
    scanner.advance()
    return ("", 204)


@app.route("/liveview")
def liveview():
    
    # def generator():
    #     while True:
    #         frame = scanner.camera.get_frame()
    #         yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"

    # def generator():
    #     buffer = BytesIO()
    #     t1 = time.time()
    #     for _ in scanner.camera.capture_continuous(buffer, format="jpeg", use_video_port=True):
    #         # TODO: Hack!
    #         scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

    #         buffer.truncate()
    #         buffer.seek(0)
    #         frame = buffer.read()
    #         buffer.seek(0)
            
    #         t2 = time.time()
    #         fps = 1 / (t2 - t1)
    #         t1 = t2

    #         print(f"Generated frame: camera_fps={scanner.camera.framerate}, true_fps={fps:.2f}")

    #         yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 

    #         buffer.seek(0)
    
    def generator():

        cap = cv2.VideoCapture("stream_test/Designing Desire  Introducing the new Volvo S90.mp4")
        print("cap.isOpened()", cap.isOpened())

        frames = []
        while cap.isOpened() and len(frames) < 100:
            ret, bgr = cap.read()

            if not ret:
                return
            
            width = int(bgr.shape[1] / 2)
            height = int(bgr.shape[0] / 2)
            dim = (width, height)
            resized = cv2.resize(bgr, dim, interpolation=cv2.INTER_AREA)

            _, encoded = cv2.imencode(".jpg", resized)
            frame = encoded.tobytes()

            frames.append(frame)

            print(f"Read {len(frames)} frames")

        t1 = time.time()
        i = 0
        while True:
            frame = frames[i]
            i = (i + 1) % len(frames)

            t2 = time.time()
            fps = 1 / (t2 - t1)
            t1 = t2

            print(f"Generated frame: camera_fps=25, true_fps={fps:.2f}")

            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 

    return Response(generator(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/counter")
def counter():
    return "foobar"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
