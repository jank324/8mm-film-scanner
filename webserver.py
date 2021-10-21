from io import BytesIO
import time

import cv2
from flask import Flask, render_template, Response

from filmscanner import FilmScanner


app = Flask(__name__)
scanner = FilmScanner()
scanner.camera.resolution = (800, 600)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/advance", methods=["POST"])
def advance():
    scanner.advance()
    return ("", 204)


@app.route("/fastforward", methods=["POST"])
def fast_forward():
    scanner.fast_forward()
    return ("", 204)


@app.route("/liveview")
def liveview():

    def liveview_stream():
        for frame in scanner.liveview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 

    return Response(liveview_stream(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/stop", methods=["POST"])
def stop():
    scanner._stop_requested = True
    return ("", 204)


@app.route("/togglefocuszoom", methods=["POST"])
def toggle_focus_zoom():
    scanner._live_view_zoom_toggle_requested = True
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
