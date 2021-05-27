from io import BytesIO
import sys
from threading import Event

import cv2
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
plt.style.use("dark_background")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from pydng.core import RPICAM2DNG

from filmscanner import FilmScanner


class VideoThread(QThread):
    
    change_image_signal = pyqtSignal(np.ndarray)
    change_histogram_signal = pyqtSignal(np.ndarray)
    not_advancing_event = Event()

    def __init__(self, camera):
        super().__init__()

        self.camera = camera
        self.camera.resolution = (1024, 768)

        self.not_advancing_event.set()

    def run(self):
        bgr = np.empty((768, 1024,3), dtype=np.uint8)
        histogram = np.empty((3,256))

        for _ in self.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            for i in range(3):
                histogram[i] = cv2.calcHist([bgr], [i], None, [256], [0,256])[:,0]

            self.change_image_signal.emit(bgr)
            self.change_histogram_signal.emit(histogram)
            
            self.not_advancing_event.wait()
        

class LiveView(QLabel):

    def __init__(self):
        super().__init__()

        self.grid = False
        self.focus_peaking = False
        self.rgb_black = False
        self.rgb_white = False
        self.bayer_black = False
        self.bayer_white = False

        self.bayer = None

    @pyqtSlot(np.ndarray)
    def update_image(self, image):
        image = cv2.flip(image, 0)

        preview = image.copy()
        if self.focus_peaking:
            preview = self.draw_focus_peaking(preview, image)
        if self.rgb_black:
            preview = self.draw_rgb_black(preview, image)
        if self.rgb_white:
            preview = self.draw_rgb_white(preview, image)
        if self.bayer_black:
            preview = self.draw_bayer_black(preview)
        if self.bayer_white:
            preview = self.draw_bayer_white(preview)
        if self.grid:
            preview = self.draw_grid(preview)

        q_pixmap = self.cv2qt(preview)
        self.setPixmap(q_pixmap)
    
    def cv2qt(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        bytes_per_line = channels * width
        q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)
    
    @pyqtSlot()
    def toggle_grid(self):
        self.grid = not self.grid
    
    def draw_grid(self, image):
        color = (255, 255, 255)
        for y in np.linspace(0, image.shape[0], 10)[1:]:
            cv2.line(image, (0,int(y)), (image.shape[1],int(y)), color)
        for x in np.linspace(0, image.shape[1], 10)[1:]:
            cv2.line(image, (int(x),0), (int(x),image.shape[0]), color)
        return image
    
    @pyqtSlot()
    def toggle_rgb_black(self):
        self.rgb_black = not self.rgb_black
    
    @pyqtSlot()
    def toggle_rgb_white(self):
        self.rgb_white = not self.rgb_white
    
    @pyqtSlot()
    def toggle_bayer_black(self):
        self.bayer_black = not self.bayer_black
    
    @pyqtSlot()
    def toggle_bayer_white(self):
        self.bayer_white = not self.bayer_white
    
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
    
    def draw_bayer_black(self, preview):
        preview[self.bayer<40] = [255, 0, 0]
        preview[self.bayer<40] = [255, 0, 0]
        preview[self.bayer<40] = [255, 0, 0]
        return preview
    
    def draw_bayer_white(self, preview):
        preview[self.bayer>4020] = [0, 0, 255]
        preview[self.bayer>4020] = [0, 0, 255]
        preview[self.bayer>4020] = [0, 0, 255]
        return preview

    @pyqtSlot()
    def toggle_focus_peaking(self):
        self.focus_peaking = not self.focus_peaking

    def draw_focus_peaking(self, preview, image):
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grey, 0, 255)
        overlay = cv2.add(preview, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
        return overlay
    
    def update_bayer(self, raw):
        self.bayer = cv2.resize(raw, dsize=(1024,768), interpolation=cv2.INTER_NEAREST)


class Histogram(FigureCanvasQTAgg):

    def __init__(self, camera):
        self.camera = camera

        self.fig = Figure()
        self.ax0 = self.fig.add_subplot(211)
        self.ax1 = self.fig.add_subplot(212)

        super().__init__(self.fig)

        self.ax0.set_xlim([0, 255])
        self.ax0.set_ylim([0, None])
        self.ax0.set_xticks([])
        self.ax0.set_yticks([])
        self.plot_blue, = self.ax0.plot(range(256), np.zeros(256), color="blue")
        self.plot_green, = self.ax0.plot(range(256), np.zeros(256), color="green")
        self.plot_red, = self.ax0.plot(range(256), np.zeros(256), color="red")

        self.ax1.set_xlim([0, 4095])
        self.ax1.set_ylim([0, None])
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.plot_bayer, = self.ax1.plot(range(4096), np.zeros(4096), color="white")

        self.fig.tight_layout()

        self.setFixedSize(300, 300)
    
    @pyqtSlot(np.ndarray)
    def update_rgb(self, histogram):
        self.plot_blue.set_ydata(histogram[0])
        self.plot_green.set_ydata(histogram[1])
        self.plot_red.set_ydata(histogram[2])

        self.ax0.set_ylim([0, max(1, histogram[:,20:].max())])

        self.draw()
    
    def update_bayer(self, raw):
        histogram = cv2.calcHist([raw], [0], None, [4096], [0,4096])[:,0]
        self.plot_bayer.set_ydata(histogram)
        self.ax1.set_ylim([0, max(1, histogram[320:].max())])

        # self.draw()


class ShutterSpeedSelector(QWidget):

    def __init__(self, camera):
        super().__init__()

        self.camera = camera

        self.down_button = QPushButton("Down")
        self.down_button.clicked.connect(self.decrease)

        self.speed_label = QLabel("---")

        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.increase)

        hbox = QHBoxLayout()
        hbox.addWidget(self.down_button)
        hbox.addWidget(self.speed_label)
        hbox.addWidget(self.up_button)
        self.setLayout(hbox)

        self.options = [1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125, 1/60, 1/30, 1/15]

        self.value_index = 0
    
    @property
    def value_index(self):
        return self._value_index
    
    @value_index.setter
    def value_index(self, index):
        self._value_index = index
        speed = self.options[index]
        self.speed_label.setText(f"1/{int(1/speed)} s")
        self.camera.shutter_speed = int(speed * 1000000)
    
    @pyqtSlot()
    def decrease(self):
        self.value_index = max(0, self.value_index-1)
    
    @pyqtSlot()
    def increase(self):
        self.value_index = min(len(self.options)-1, self.value_index+1)


class ISOSelector(QWidget):

    def __init__(self, camera):
        super().__init__()

        self.camera = camera

        self.down_button = QPushButton("Down")
        self.down_button.clicked.connect(self.decrease)

        self.speed_label = QLabel("---")

        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.increase)

        hbox = QHBoxLayout()
        hbox.addWidget(self.down_button)
        hbox.addWidget(self.speed_label)
        hbox.addWidget(self.up_button)
        self.setLayout(hbox)

        self.options = [100, 200, 400, 800]

        self.value_index = 0
    
    @property
    def value_index(self):
        return self._value_index
    
    @value_index.setter
    def value_index(self, index):
        self._value_index = index
        iso = self.options[index]
        self.speed_label.setText(f"ISO {iso}")
        self.camera.iso = iso
    
    @pyqtSlot()
    def decrease(self):
        self.value_index = max(0, self.value_index-1)
    
    @pyqtSlot()
    def increase(self):
        self.value_index = min(len(self.options)-1, self.value_index+1)


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.scanner = FilmScanner()

        self.setWindowTitle("Live View")

        self.live_view = LiveView()

        self.histogram = Histogram(self.scanner.camera)

        self.shutter_speed_selector = ShutterSpeedSelector(self.scanner.camera)

        self.iso_selector = ISOSelector(self.scanner.camera)

        self.bayer_histogram_button = QPushButton("Bayer Histogram")
        self.bayer_histogram_button.clicked.connect(self.get_bayer)

        self.advance_button = QPushButton("Advance")
        self.advance_button.clicked.connect(self.clicked_advance)

        self.grid_button = QPushButton("Grid")
        self.grid_button.clicked.connect(self.live_view.toggle_grid)
        
        self.focus_peaking_button = QPushButton("Focus Peaking")
        self.focus_peaking_button.clicked.connect(self.live_view.toggle_focus_peaking)

        self.rgb_black_button = QPushButton("RGB Black")
        self.rgb_black_button.clicked.connect(self.live_view.toggle_rgb_black)
        self.rgb_white_button = QPushButton("RGB White")
        self.rgb_white_button.clicked.connect(self.live_view.toggle_rgb_white)
        self.bayer_black_button = QPushButton("Bayer Black")
        self.bayer_black_button.clicked.connect(self.live_view.toggle_bayer_black)
        self.bayer_white_button = QPushButton("Bayer White")
        self.bayer_white_button.clicked.connect(self.live_view.toggle_bayer_white)


        hbox = QHBoxLayout()
        hbox.addWidget(self.live_view)
        vbox = QVBoxLayout()
        vbox.addWidget(self.histogram)
        vbox.addWidget(self.bayer_histogram_button)
        vbox.addWidget(QLabel("Camera Controls"))
        vbox.addWidget(self.shutter_speed_selector)
        vbox.addWidget(self.iso_selector)
        vbox.addWidget(QLabel("Machine Controls"))
        vbox.addWidget(self.advance_button)
        vbox.addWidget(QLabel("Overlays"))
        vbox.addWidget(self.grid_button)
        vbox.addWidget(self.focus_peaking_button)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.rgb_black_button)
        hbox2.addWidget(self.rgb_white_button)
        hbox2.addWidget(self.bayer_black_button)
        hbox2.addWidget(self.bayer_white_button)
        vbox.addLayout(hbox2)
        vbox.addStretch()
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        self.video_thread = VideoThread(self.scanner.camera)
        self.video_thread.change_image_signal.connect(self.live_view.update_image)
        self.video_thread.change_histogram_signal.connect(self.histogram.update_rgb)
        self.video_thread.start()
    
    @pyqtSlot()
    def clicked_advance(self):
        self.video_thread.not_advancing_event.clear()
        self.scanner.advance()
        self.video_thread.not_advancing_event.set()
    
    @pyqtSlot()
    def handle_application_exit(self):
        del(self.scanner)
    
    @pyqtSlot()
    def get_bayer(self):
        stream = BytesIO()
        self.scanner.camera.capture(stream, format="jpeg", bayer=True)
        stream.seek(0)

        def save_data(raw):
            self.histogram.update_bayer(raw)
            self.live_view.update_bayer(raw)
            return raw

        RPICAM2DNG().convert(stream, process=save_data)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = App()
    window.show()

    app.aboutToQuit.connect(window.handle_application_exit)

    sys.exit(app.exec_())
