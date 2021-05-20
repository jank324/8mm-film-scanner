from time import sleep

from imutils.video.pivideostream import PiVideoStream
from flask import Flask, render_template, Response

from machine import FilmScanner


app = Flask(__name__)

machine = FilmScanner()


@app.route("/")
def index():
    return render_template("index.html")

def gen_liveview():
    return machine.current_frame()
    while True:
        frame = machine.current_frame()
        yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"

@app.route("/liveview")
def liveview():
    sleep(2)
    return Response(gen_liveview(), mimetype="multipart/x-mixed-replace; boundry=frame")

@app.route("/advance", methods=["POST"])
def advance():
    machine.camera.pause()
    machine.advance()
    machine.camera.resume()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
