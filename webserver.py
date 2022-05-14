from flask import Flask, Response, request
from flask_cors import CORS

from filmscanner import FilmScanner
from notification import MailCallback
from utils import AdvanceTriggerManager, FastForwardToggleManager, LightToggleManager, ScanStateManager, ZoomToggleManager


app = Flask(__name__)
cors = CORS(app)

advance_trigger_manager = AdvanceTriggerManager()
fast_forward_manager = FastForwardToggleManager()
light_toggle_manager = LightToggleManager()
mail_callback = MailCallback()
scan_state_manager = ScanStateManager()
zoom_toggle_manager = ZoomToggleManager()

scanner = FilmScanner(
    callback=[
        advance_trigger_manager,
        light_toggle_manager,
        fast_forward_manager,
        mail_callback,
        scan_state_manager,
        zoom_toggle_manager
    ]
)
scanner.camera.resolution = (800, 600)


@app.route("/advance", methods=("GET","POST"))
def advance():
    if request.method == "GET":
        return {
            "on": scanner.is_advancing and not (scanner.is_fast_forwarding or scanner.is_scanning),
            "enabled": not any([
                scanner.is_advancing,
                scanner.is_fast_forwarding,
                scanner.is_scanning
            ])
        }
    elif request.method == "POST":
        scanner.advance()
        return "", 204
    return "", 400


@app.route("/advance-stream")
def advance_stream():
    return Response(advance_trigger_manager.messenger.subscribe(), mimetype="text/event-stream")


@app.route("/fastforward", methods=("GET","POST"))
def fast_forward():
    if request.method == "GET":
        return {
            "on": scanner.is_fast_forwarding,
            "enabled": not (scanner.is_advancing or scanner.is_scanning)
        }
    elif request.method == "POST":
        if not scanner.is_fast_forwarding:
            scanner.fast_forward()
        else:
            scanner.scan_stop_requested = True
        return "", 204
    return "", 400


@app.route("/fastforward-stream")
def fast_forward_stream():
    return Response(fast_forward_manager.messenger.subscribe(), mimetype="text/event-stream")


@app.route("/focuszoom", methods=("GET","POST"))
def toggle_focus_zoom():
    if request.method == "GET":
        return {
            "on": scanner.is_zoomed,
            "enabled": not scanner.is_scanning
        }
    elif request.method == "POST":
        scanner.live_view_zoom_toggle_requested = True
        return "", 204
    return "", 400


@app.route("/focuszoom-stream")
def focuszoom_stream():
    return Response(zoom_toggle_manager.messenger.subscribe(), mimetype="text/event-stream")


@app.route("/light", methods=("GET","POST"))
def toggle_light():
    if request.method == "GET":
        return {
            "on": scanner.is_backlight_on,
            "enabled": not scanner.is_scanning
        }
    elif request.method == "POST":
        if not scanner.is_scanning:
            scanner.toggle_backlight()
        return "", 204
    return "", 400


@app.route("/light-stream")
def light_stream():
    return Response(light_toggle_manager.messenger.subscribe(), mimetype="text/event-stream")


@app.route("/poweroff", methods=("POST",))
def poweroff():
    scanner.poweroff()
    return "", 204


@app.route("/preview")
def preview():
    def generate():
        for frame in scanner.preview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 
    return app.response_class(generate(), mimetype="multipart/x-mixed-replace; boundry=frame")


@app.route("/scan", methods=("GET","POST"))
def scan():
    if request.method == "GET":
        return {
            "isScanning": scanner.is_scanning,
            "path": scanner.output_directory,
            "frames": scanner.n_frames
        }
    elif request.method == "POST":
        if not scanner.is_scanning:
            scanner.start_scan(request.get_json()["path"], n_frames=int(request.get_json()["frames"]))
        else:
            scanner.stop_scan()
        return "", 204
    return "", 400


@app.route("/scan-stream")
def scan_stream():
    return Response(scan_state_manager.messenger.subscribe(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
