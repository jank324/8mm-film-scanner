from flask import Flask, Response, request

from filmscanner import FilmScanner
from notification import MailCallback
from utils import DashboardCallback

app = Flask(__name__, static_folder="frontend/build", static_url_path="/")

dashboard_callback = DashboardCallback()
mail_callback = MailCallback()

scanner = FilmScanner(callback=[dashboard_callback, mail_callback])
scanner.camera.resolution = (800, 600)  # TODO Does this need to be here?


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/backend/advance", methods=("POST",))
def advance():
    if scanner.is_advance_allowed:
        scanner.advance()
    return "", 204


@app.route("/backend/dashboard")
def dashboard():
    return dashboard_callback.scanner_state_dict


@app.route("/backend/dashboard-sse")
def dashboard_sse():
    return Response(dashboard_callback.subscribe_to_sse(), mimetype="text/event-stream")


@app.route("/backend/dismiss", methods=("POST",))
def dismiss():
    scanner.last_scan_end_info = "dismissed"
    return "", 204


@app.route("/backend/fastforward", methods=("POST",))
def fast_forward():
    if not scanner.is_fast_forwarding and scanner.is_fast_forward_allowed:
        scanner.start_fast_forward()
    elif scanner.is_fast_forwarding:
        scanner.stop_fast_forward()
    return "", 204


@app.route("/backend/focuszoom", methods=("POST",))
def toggle_focus_zoom():
    if scanner.is_zoom_toggle_allowed:
        scanner.toggle_zoom()
    return "", 204


@app.route("/backend/light", methods=("POST",))
def toggle_light():
    if scanner.is_light_toggle_allowed:
        scanner.toggle_light()
    return "", 204


@app.route("/backend/poweroff", methods=("POST",))
def poweroff():
    scanner.poweroff()
    return "", 204


@app.route("/backend/preview")
def preview():
    def generate():
        for frame in scanner.preview():
            yield b"--frame\r\n" + b"ContentType: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"

    return app.response_class(
        generate(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/backend/scan", methods=("POST",))
def scan():
    if not scanner.is_scanning and scanner.is_scanning_allowed:
        scanner.start_scan(
            output_directory=request.get_json()["output_directory"],
            n_frames=int(request.get_json()["n_frames"]),
        )
    elif scanner.is_scanning:
        scanner.stop_scan()
    return "", 204


@app.route("/backend/scan-setup")
def scan_setup():
    return {"n_frames": scanner.n_frames, "output_directory": scanner.output_directory}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
