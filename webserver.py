from flask import Flask, Response, request
from flask_cors import CORS

from filmscanner import FilmScanner
from notification import MailCallback
from utils import (
    AdvanceToggleCallback,
    FastForwardToggleCallback,
    LightToggleCallback,
    ScanControlsCallback,
    ZoomToggleCallback
)


app = Flask(__name__)
cors = CORS(app)

advance_toggle_callback = AdvanceToggleCallback()
fast_forward_toggle_callback = FastForwardToggleCallback()
light_toggle_callback = LightToggleCallback()
mail_callback = MailCallback()
scan_controls_callback = ScanControlsCallback()
zoom_toggle_callback = ZoomToggleCallback()

scanner = FilmScanner(
    callback=[
        advance_toggle_callback,
        light_toggle_callback,
        fast_forward_toggle_callback,
        mail_callback,
        scan_controls_callback,
        zoom_toggle_callback
    ]
)
scanner.camera.resolution = (800, 600)


@app.route("/advance", methods=("GET","POST"))
def advance():
    if request.method == "GET":
        return {
            "is_active": scanner.is_advancing and not (scanner.is_fast_forwarding or scanner.is_scanning),
            "is_enabled": not any([
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
    return Response(advance_toggle_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/dismiss", methods=("POST",))
def dismiss():
    scanner.last_scan_end_info = "dismissed"
    return "", 204


@app.route("/fastforward", methods=("GET","POST"))
def fast_forward():
    if request.method == "GET":
        return {
            "is_active": scanner.is_fast_forwarding,
            "is_enabled": not (scanner.is_advancing or scanner.is_scanning)
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
    return Response(fast_forward_toggle_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/focuszoom", methods=("GET","POST"))
def toggle_focus_zoom():
    if request.method == "GET":
        return {
            "is_active": scanner.is_zoomed,
            "is_enabled": not scanner.is_scanning
        }
    elif request.method == "POST":
        scanner.live_view_zoom_toggle_requested = True
        return "", 204
    return "", 400


@app.route("/focuszoom-stream")
def focuszoom_stream():
    return Response(zoom_toggle_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/light", methods=("GET","POST"))
def toggle_light():
    if request.method == "GET":
        return {
            "is_active": scanner.is_light_on,
            "is_enabled": not scanner.is_scanning
        }
    elif request.method == "POST":
        if not scanner.is_scanning:
            scanner.toggle_light()
        return "", 204
    return "", 400


@app.route("/light-stream")
def light_stream():
    return Response(light_toggle_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/poweroff", methods=("POST",))
def poweroff():
    print("Pretending to power off")
    # scanner.poweroff()
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
            "is_scanning": scanner.is_scanning,
            "output_directory": scanner.output_directory,
            "n_frames": scanner.n_frames,
            "current_frame_index": scanner.current_frame_index if scanner.is_scanning else 0,
            "last_scan_end_info": scanner.last_scan_end_info
        }
    elif request.method == "POST":
        if not scanner.is_scanning:
            scanner.start_scan(
                output_directory=request.get_json()["output_directory"],
                n_frames=int(request.get_json()["n_frames"])
            )
        else:
            scanner.stop_scan()
        return "", 204
    return "", 400


@app.route("/scan-stream")
def scan_stream():
    return Response(scan_controls_callback.subscribe_to_sse(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
