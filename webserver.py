from flask import Flask, Response, request
from flask_cors import CORS

from filmscanner import FilmScanner
from utils import AdvanceTriggerManager, FastForwardToggleManager, LightToggleManager, ZoomToggleManager


app = Flask(__name__)
cors = CORS(app)

advance_trigger_manager = AdvanceTriggerManager()
fast_forward_manager = FastForwardToggleManager()
light_toggle_manager = LightToggleManager()
zoom_toggle_manager = ZoomToggleManager()
scanner = FilmScanner(
    callback=[advance_trigger_manager,fast_forward_manager,zoom_toggle_manager],
    backlight_callback=light_toggle_manager
)
scanner.camera.resolution = (800, 600)


@app.route("/advance", methods=("GET","POST"))
def advance():
    if request.method == "GET":
        return Response(advance_trigger_manager.messenger.subscribe(), mimetype="text/event-stream")
    elif request.method == "POST":
        scanner.advance()
        return "", 204
    return "", 400


@app.route("/fastforward", methods=("GET","POST"))
def fast_forward():
    if request.method == "GET":
        return Response(fast_forward_manager.messenger.subscribe(), mimetype="text/event-stream")
    elif request.method == "POST":
        if not scanner.is_fast_forwarding:
            scanner.fast_forward()
        else:
            scanner.stop_requested = True
        return "", 204
    return "", 400


@app.route("/preview")
def liveview():
    def generate():
        for frame in scanner.liveview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 
    return app.response_class(generate(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/light", methods=("GET","POST"))
def toggle_light():
    if request.method == "GET":
        return Response(light_toggle_manager.messenger.subscribe(), mimetype="text/event-stream")
    elif request.method == "POST":
        if not scanner.is_scanning:
            scanner.backlight.toggle()
        return "", 204
    return "", 400


@app.route("/focuszoom", methods=("GET","POST"))
def toggle_focus_zoom():
    if request.method == "GET":
        return  Response(zoom_toggle_manager.messenger.subscribe(), mimetype="text/event-stream")
    elif request.method == "POST":
        scanner.live_view_zoom_toggle_requested = True
        return "", 204
    return "", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
