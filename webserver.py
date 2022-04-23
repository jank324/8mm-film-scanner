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


@app.route("/fastforward", methods=("POST",))
def fast_forward():
    if not scanner.is_fast_forwarding:
        scanner.fast_forward()
    else:
        scanner.stop_requested = True
    return "", 204


@app.route("/preview")
def liveview():
    def generate():
        for frame in scanner.liveview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 
    return app.response_class(generate(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/light", methods=("POST",))
def toggle_light():
    if scanner.backlight.is_on:
        scanner.backlight.turn_off()
    else:
        scanner.backlight.turn_on()
    return "", 204


@app.route("/focuszoom", methods=("POST",))
def toggle_focus_zoom():
    scanner.live_view_zoom_toggle_requested = True
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
