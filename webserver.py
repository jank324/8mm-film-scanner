import time

from flask import Flask
from flask_cors import CORS

from filmscanner import FilmScanner


app = Flask(__name__)
cors = CORS(app)

scanner = FilmScanner()
scanner.camera.resolution = (800, 600)


@app.route("/advance", methods=("POST",))
def advance():
    scanner.advance()
    return "", 204


@app.route("/counter")
def get_counter():
    def generator():
        counter = 0
        while True:
            time.sleep(0.2)
            yield f"data: {counter}\n\n"
            counter += 1
    return app.response_class(generator(), content_type="text/event-stream")


@app.route("/fastforward", methods=("POST",))
def fast_forward():
    scanner.fast_forward()
    return "", 204


@app.route("/preview")
def liveview():
    def generate():
        for frame in scanner.liveview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 
    return app.response_class(generate(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/stop", methods=("POST",))
def stop():
    scanner._stop_requested = True
    return "", 204


@app.route("/togglefocuszoom", methods=("POST",))
def toggle_focus_zoom():
    scanner._live_view_zoom_toggle_requested = True
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
