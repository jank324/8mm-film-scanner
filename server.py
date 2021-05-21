from time import sleep
from time import time

from imutils.video.pivideostream import PiVideoStream
from flask import Flask, render_template, Response

from machine import FilmScanner


app = Flask(__name__)

machine = FilmScanner()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/liveview")
def liveview():

    def generator():
        while True:
            frame = machine.camera.get_frame()
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"

    return Response(generator(), mimetype="multipart/x-mixed-replace; boundry=frame")

@app.route("/advance", methods=["POST"])
def advance():
    machine.camera.pause()
    machine.advance()
    machine.camera.resume()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
