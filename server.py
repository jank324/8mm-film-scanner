import cv2
from flask import Flask, render_template, Response


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/videostream")
def videostream():
    image = cv2.imread("test00.jpg", cv2.IMREAD_COLOR)
    _, jpeg = cv2.imencode(".jpg", image)
    jpeg_bytes = jpeg.tobytes()
    packaged = b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n\r\n"
    return Response(packaged, mimetype="multipart/x-mixed-replace; boundry=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
