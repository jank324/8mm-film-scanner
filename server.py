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

@app.route("/advance", methods=["POST"])
def advance():
    machine.advance()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
