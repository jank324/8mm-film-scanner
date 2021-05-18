from imutils.video.pivideostream import PiVideoStream
from flask import Flask, render_template, Response

from machine import FilmScanner


app = Flask(__name__)

machine = FilmScanner()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/videostream")
def videostream():
    return Response(machine.current_frame(), mimetype="multipart/x-mixed-replace; boundry=frame")

@app.route("/light", methods=["POST"])
def toggle_light():
    import RPi.GPIO as GPIO
    GPIO.output(6, GPIO.LOW)
    # print("foo_1")
    # if machine.backlight.is_on:
    #     print("foo_2a")
    #     machine.backlight.turn_off()
    # else:
    #     print("foo_2b")
    #     machine.backlight.turn_on()
    # print("foo_3")
    return ("", 204)

@app.route("/advance", methods=["POST"])
def advance():
    machine.advance()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
