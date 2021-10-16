from io import BytesIO
import time

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

    def generator():
        buffer = BytesIO()
        t1 = time.time()
        for _ in scanner.camera.capture_continuous(buffer, format="jpeg", use_video_port=True):
            # TODO: Hack!
            scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

            buffer.truncate()
            buffer.seek(0)
            frame = buffer.read()
            buffer.seek(0)
            
            t2 = time.time()
            fps = 1 / (t2 - t1)
            t1 = t2

            print(f"Generated frame: camera_fps={scanner.camera.framerate}, true_fps={fps:.2f}")

            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + buffer.read() + b"\r\n\r\n" 

            buffer.seek(0)

    return Response(generator(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/counter")
def counter():
    return "foobar"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
