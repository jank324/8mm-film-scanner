import cv2
from imutils.video.pivideostream import PiVideoStream
from flask import Flask, render_template, Response


app = Flask(__name__)

video_stream = PiVideoStream(resolution=(1024,768))
video_stream.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/videostream")
def videostream():
    frame = video_stream.read()
    _, jpeg = cv2.imencode(".jpg", frame)
    jpeg_bytes = jpeg.tobytes()
    packaged = b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n\r\n"
    return Response(packaged, mimetype="multipart/x-mixed-replace; boundry=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
