import cv2
from imutils.video.pivideostream import PiVideoStream
from flask import Flask, render_template, Response


app = Flask(__name__)

video_stream = PiVideoStream(resolution=(1024,768))
video_stream.start()

import RPi.GPIO as GPIO
from machine import Light
GPIO.setmode(GPIO.BCM)
light = Light(6)


@app.route("/")
def index():
    return render_template("index.html")


def gen(stream):
    while True:
        frame = stream.read()
        _, jpeg = cv2.imencode(".jpg", frame)
        jpeg_bytes = jpeg.tobytes()
        packaged = b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n\r\n"
        yield packaged


@app.route("/videostream")
def videostream():
    return Response(gen(video_stream), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/light", methods=["POST"])
def toggle_light():
    if light.is_on:
        light.turn_off()
    else:
        light.turn_on()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
