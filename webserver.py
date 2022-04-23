from flask import Flask, Response, request
from flask_cors import CORS

from filmscanner import FilmScanner


app = Flask(__name__)
cors = CORS(app)

scanner = FilmScanner()
scanner.camera.resolution = (800, 600)


@app.route("/advance", methods=("GET","POST"))
def advance():
    if request.method == "GET":
        def get_data():
            while True:
                yield f"data: {scanner.is_actively_advancing} \n\n"
        return Response(get_data(), mimetype="text/event-stream")
    elif request.method == "POST":
        scanner.advance()
    return "", 204


@app.route("/fastforward", methods=("GET","POST"))
def fast_forward():
    if request.method == "GET":
        def get_data():
            while True:
                yield f"data: {scanner.is_fast_forwarding} \n\n"
        return Response(get_data(), mimetype="text/event-stream")
    elif request.method == "POST":
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


@app.route("/light", methods=("GET","POST"))
def toggle_light():
    if request.method == "GET":
        def get_data():
            while True:
                yield f"data: {scanner.backlight.is_on} \n\n"
        return Response(get_data(), mimetype="text/event-stream")
    elif request.method == "POST":
        scanner.backlight.toggle()
    return "", 204


@app.route("/focuszoom", methods=("GET","POST"))
def toggle_focus_zoom():
    if request.method == "GET":
        def get_data():
            while True:
                yield f"data: {scanner.is_zoomed} \n\n"
        return Response(get_data(), mimetype="text/event-stream")
    elif request.method == "POST":
        scanner.live_view_zoom_toggle_requested = True
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
