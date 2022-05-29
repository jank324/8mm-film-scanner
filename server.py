from flask import Flask, Response, request

from filmscanner import FilmScanner
from notification import MailCallback
from utils import DashboardCallback


app = Flask(__name__, static_folder="frontend/build", static_url_path="/")

dashboard_callback = DashboardCallback()
mail_callback = MailCallback()

scanner = FilmScanner(callback=[dashboard_callback,mail_callback])
scanner.camera.resolution = (800, 600)  # TODO Does this need to be here?


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/backend/advance", methods=("GET","POST"))
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


@app.route("/backend/dashboard-sse")
def dashboard_sse():
    return Response(dashboard_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/backend/dismiss", methods=("POST",))
def dismiss():
    scanner.last_scan_end_info = "dismissed"
    return "", 204


@app.route("/backend/fastforward", methods=("GET","POST"))
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


@app.route("/backend/focuszoom", methods=("GET","POST"))
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


@app.route("/backend/light", methods=("GET","POST"))
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


@app.route("/backend/poweroff", methods=("POST",))
def poweroff():
    scanner.poweroff()
    return "", 204


@app.route("/backend/preview")
def preview():
    def generate():
        for frame in scanner.preview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n" 
    return app.response_class(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/backend/scan", methods=("GET","POST"))
def scan():
    if request.method == "GET":
        return {
            "is_scanning": scanner.is_scanning,
            "output_directory": scanner.output_directory,
            "n_frames": scanner.n_frames,
            "current_frame_index": scanner.current_frame_index if scanner.is_scanning else 0,
            "last_scan_end_info": scanner.last_scan_end_info,
            "time_remaining": dashboard_callback.str_time_remaining
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
