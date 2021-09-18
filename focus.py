from io import BytesIO
import sys
from threading import Event
import time

import cv2
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
plt.style.use("dark_background")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from pidng.core import RPICAM2DNG
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from filmscanner import FilmScanner


class VideoThread(qtc.QThread):
    
    image_updated = qtc.pyqtSignal(np.ndarray)
    histogram_updated = qtc.pyqtSignal(np.ndarray)

    not_advancing_event = Event()

    def __init__(self, camera):
        super().__init__()

        self.camera = camera
        self.camera.resolution = (1024, 768)

        self.focus_zoom = False
        self.not_advancing_event.set()

    def run(self):
        while True:
            if self.focus_zoom:
                self.zoomed_capture()
            else:
                self.standard_capture()
    
    def toggle_focus_zoom(self):
        self.focus_zoom = not self.focus_zoom
    
    def standard_capture(self):
        self.camera.resolution = (1024, 768)

        bgr = np.empty((768, 1024,3), dtype=np.uint8)
        histogram = np.empty((3,256))

        for _ in self.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            for i in range(3):
                histogram[i] = cv2.calcHist([bgr], [i], None, [256], [0,256])[:,0]

            self.image_updated.emit(bgr)
            self.histogram_updated.emit(histogram)
            
            self.not_advancing_event.wait()

            # TODO: Hack!
            self.camera.shutter_speed = int(1e6 * 1 / 2000)

            if self.focus_zoom:
                break
    
    def zoomed_capture(self):
        self.camera.resolution = (4032, 3040)

        bgr = np.empty((3040,4032,3), dtype=np.uint8)
        histogram = np.empty((3,256))

        for _ in self.camera.capture_continuous(bgr, format="bgr"):#, use_video_port=True):
            zoomed = bgr[1520-384:1520+384,2016-512:2016+512,:]

            for i in range(3):
                histogram[i] = cv2.calcHist([zoomed], [i], None, [256], [0,256])[:,0]

            self.image_updated.emit(zoomed)
            self.histogram_updated.emit(histogram)
            
            self.not_advancing_event.wait()

            # TODO: Hack!
            self.camera.shutter_speed = int(1e6 * 1 / 2000)

            if not self.focus_zoom:
                break


class LiveView(qtw.QLabel):

    def __init__(self, camera):
        super().__init__()

        self.camera = camera

        self.grid = False
        self.focus_peaking = False
        self.rgb_black = False
        self.rgb_white = False

        self.video_thread = VideoThread(self.camera)
        self.video_thread.image_updated.connect(self.update_image)
        self.video_thread.start()

    @qtc.pyqtSlot(np.ndarray)
    def update_image(self, image):
        image = cv2.flip(image, 1)

        preview = image.copy()
        if self.focus_peaking:
            preview = self.draw_focus_peaking(preview, image)
        if self.rgb_black:
            preview = self.draw_rgb_black(preview, image)
        if self.rgb_white:
            preview = self.draw_rgb_white(preview, image)
        if self.grid:
            preview = self.draw_grid(preview)

        q_pixmap = self.cv2qt(preview)
        self.setPixmap(q_pixmap)
    
    def cv2qt(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        bytes_per_line = channels * width
        q_image = qtg.QImage(rgb.data, width, height, bytes_per_line, qtg.QImage.Format_RGB888)
        return qtg.QPixmap.fromImage(q_image)
    
    def pause(self):
        self.video_thread.not_advancing_event.clear()
    
    def resume(self):
        self.video_thread.not_advancing_event.set()
    
    def toggle_grid(self):
        self.grid = not self.grid
    
    def draw_grid(self, image):
        color = (255, 255, 255)
        for y in np.linspace(0, image.shape[0], 10)[1:]:
            cv2.line(image, (0,int(y)), (image.shape[1],int(y)), color)
        for x in np.linspace(0, image.shape[1], 10)[1:]:
            cv2.line(image, (int(x),0), (int(x),image.shape[0]), color)
        return image
    
    def toggle_rgb_black(self):
        self.rgb_black = not self.rgb_black
    
    def toggle_rgb_white(self):
        self.rgb_white = not self.rgb_white
    
    def draw_rgb_black(self, preview, image):
        preview[image[:,:,2]<10] = [255, 0, 0]
        preview[image[:,:,1]<10] = [255, 0, 0]
        preview[image[:,:,0]<10] = [255, 0, 0]
        return preview
    
    def draw_rgb_white(self, preview, image):
        preview[image[:,:,2]>245] = [0, 0, 255]
        preview[image[:,:,1]>245] = [0, 0, 255]
        preview[image[:,:,0]>245] = [0, 0, 255]
        return preview

    def toggle_focus_peaking(self):
        self.focus_peaking = not self.focus_peaking

    def draw_focus_peaking(self, preview, image):
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grey, 0, 255)
        overlay = cv2.add(preview, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
        return overlay
    
    def toggle_focus_zoom(self):
        self.video_thread.toggle_focus_zoom()


class Histogram(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.ax0 = self.fig.add_subplot(111)

        super().__init__(self.fig)

        self.ax0.set_xlim([0, 255])
        self.ax0.set_ylim([0, None])
        self.ax0.set_xticks([])
        self.ax0.set_yticks([])
        self.plot_blue, = self.ax0.plot(range(256), np.zeros(256), color="blue")
        self.plot_green, = self.ax0.plot(range(256), np.zeros(256), color="green")
        self.plot_red, = self.ax0.plot(range(256), np.zeros(256), color="red")

        self.fig.tight_layout()

        self.setFixedSize(300, 150)
    
    @qtc.pyqtSlot(np.ndarray)
    def update_rgb(self, histogram):
        self.plot_blue.set_ydata(histogram[0])
        self.plot_green.set_ydata(histogram[1])
        self.plot_red.set_ydata(histogram[2])

        self.ax0.set_ylim([0, max(1, histogram[:,20:].max())])

        self.draw()


class CameraControls(qtw.QWidget):

    shutter_speeds = [1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125, 1/60, 1/30, 1/15, 1/5, 1/2, 1]

    def __init__(self, camera):
        super().__init__()
        
        self.camera = camera

        self.shutter_speed_label = qtw.QLabel("Shutter Speed")
        self.shutter_speed_slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.shutter_speed_slider.setMinimum(0)
        self.shutter_speed_slider.setMaximum(11)
        self.shutter_speed_slider.valueChanged.connect(self.set_shutter_speed)
        self.shutter_speed_value_label = qtw.QLabel(f"1/{int(1/camera.shutter_speed)}")

        self.analog_gain_label = qtw.QLabel("Analog Gain")
        self.analog_gain_slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.analog_gain_slider.setMinimum(1)
        self.analog_gain_slider.setMaximum(16)
        self.analog_gain_slider.valueChanged.connect(self.set_analog_gain)
        self.analog_gain_value_label = qtw.QLabel()

        self.digital_gain_label = qtw.QLabel("Dgitial Gain")
        self.digital_gain_slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.digital_gain_slider.setMinimum(1)
        self.digital_gain_slider.setMaximum(16)
        self.digital_gain_slider.valueChanged.connect(self.set_digital_gain)
        self.digital_gain_value_label = qtw.QLabel()

        self.test_capture_button = qtw.QPushButton("Test Capture")
        self.test_capture_button.clicked.connect(self.test_capture)

        grid = qtw.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.shutter_speed_label, 0, 0, 1, 1)
        grid.addWidget(self.shutter_speed_slider, 0, 1, 1, 3)
        grid.addWidget(self.shutter_speed_value_label, 0, 5, 1, 1)
        grid.addWidget(self.analog_gain_label, 1, 0, 1, 1)
        grid.addWidget(self.analog_gain_slider, 1, 1, 1, 3)
        grid.addWidget(self.analog_gain_value_label, 1, 5, 1, 1)
        grid.addWidget(self.digital_gain_label, 2, 0, 1, 1)
        grid.addWidget(self.digital_gain_slider, 2, 1, 1, 3)
        grid.addWidget(self.digital_gain_value_label, 2, 5, 1, 1)
        grid.addWidget(self.test_capture_button, 3, 0, 1, 6)

        self.update_timer = qtc.QTimer()
        self.update_timer.timeout.connect(self.update_value_displays)
        self.update_timer.start(1000/24)
    
    def set_shutter_speed(self, value):
        speed = self.shutter_speeds[value]
        self.camera.shutter_speed = int(speed * 1000000)
    
    def set_analog_gain(self, value):
        self.camera.analog_gain = value
    
    def set_digital_gain(self, value):
        self.camera.digital_gain = value
    
    def update_value_displays(self):
        if self.camera.exposure_speed != 0:
            self.shutter_speed_value_label.setText(f"1/{int(1e6/self.camera.exposure_speed)}")
        else:
            self.shutter_speed_value_label.setText(f"1/{int(1e6/self.camera.shutter_speed)}")
        self.analog_gain_value_label.setText(f"{float(self.camera.analog_gain):.2f}")
        self.digital_gain_value_label.setText(f"{float(self.camera.digital_gain):.2f}")

    def test_capture(self):
        stream = BytesIO()
        self.camera.capture(stream, format="jpeg", bayer=True)
        
        stream.seek(0)
        dng = RPICAM2DNG().convert(stream)
        
        time_string = time.strftime("%Y%m%d%H%M%S")
        filename = f"test_capture/test_capture_{time_string}.dng"
        with open(filename, "wb") as file:
            file.write(dng)


class App(qtw.QWidget):

    def __init__(self):
        super().__init__()

        self.scanner = FilmScanner()

        self.setWindowTitle("8mm Film Scanner Setup")

        self.live_view = LiveView(self.scanner.camera)

        self.histogram = Histogram()
        self.live_view.video_thread.histogram_updated.connect(self.histogram.update_rgb)

        self.camera_controls = CameraControls(self.scanner.camera)

        self.advance_button = qtw.QPushButton("Advance")
        self.advance_button.clicked.connect(self.clicked_advance)

        self.grid_button = qtw.QPushButton("Grid")
        self.grid_button.clicked.connect(self.live_view.toggle_grid)
        
        self.focus_peaking_button = qtw.QPushButton("Focus Peaking")
        self.focus_peaking_button.clicked.connect(self.live_view.toggle_focus_peaking)

        self.focus_zoom_button = qtw.QPushButton("Focus Zoom")
        self.focus_zoom_button.clicked.connect(self.live_view.toggle_focus_zoom)

        self.rgb_black_button = qtw.QPushButton("RGB Black")
        self.rgb_black_button.clicked.connect(self.live_view.toggle_rgb_black)
        self.rgb_white_button = qtw.QPushButton("RGB White")
        self.rgb_white_button.clicked.connect(self.live_view.toggle_rgb_white)

        hbox = qtw.QHBoxLayout()
        hbox.addWidget(self.live_view)
        vbox = qtw.QVBoxLayout()
        vbox.addWidget(self.histogram)
        vbox.addWidget(qtw.QLabel("Camera Controls"))
        vbox.addWidget(self.camera_controls)
        vbox.addWidget(qtw.QLabel("Machine Controls"))
        vbox.addWidget(self.advance_button)
        vbox.addWidget(qtw.QLabel("View"))
        vbox.addWidget(self.grid_button)
        vbox.addWidget(self.focus_peaking_button)
        vbox.addWidget(self.focus_zoom_button)
        hbox2 = qtw.QHBoxLayout()
        hbox2.addWidget(self.rgb_black_button)
        hbox2.addWidget(self.rgb_white_button)
        vbox.addLayout(hbox2)
        vbox.addStretch()
        hbox.addLayout(vbox)
        self.setLayout(hbox)
    
    def clicked_advance(self):
        self.live_view.pause()
        self.scanner.advance()
        self.live_view.resume()
    
    def handle_application_exit(self):
        del(self.scanner)
    

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    # Force the style to be the same on all OSs
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors
    palette = qtg.QPalette()
    palette.setColor(qtg.QPalette.Window, qtg.QColor(53, 53, 53))
    palette.setColor(qtg.QPalette.WindowText, qtc.Qt.white)
    palette.setColor(qtg.QPalette.Base, qtg.QColor(25, 25, 25))
    palette.setColor(qtg.QPalette.AlternateBase, qtg.QColor(53, 53, 53))
    palette.setColor(qtg.QPalette.ToolTipBase, qtc.Qt.white)
    palette.setColor(qtg.QPalette.ToolTipText, qtc.Qt.white)
    palette.setColor(qtg.QPalette.Text, qtc.Qt.white)
    palette.setColor(qtg.QPalette.Button, qtg.QColor(53, 53, 53))
    palette.setColor(qtg.QPalette.ButtonText, qtc.Qt.white)
    palette.setColor(qtg.QPalette.BrightText, qtc.Qt.red)
    palette.setColor(qtg.QPalette.Link, qtg.QColor(42, 130, 218))
    palette.setColor(qtg.QPalette.Highlight, qtg.QColor(42, 130, 218))
    palette.setColor(qtg.QPalette.HighlightedText, qtc.Qt.black)
    app.setPalette(palette)

    window = App()
    window.show()

    app.aboutToQuit.connect(window.handle_application_exit)

    sys.exit(app.exec_())
