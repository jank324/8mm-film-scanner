import sys
from threading import Event

import cv2
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from numpy.lib.histograms import histogram

from filmscanner import FilmScanner


def cv2qt(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb.shape
    bytes_per_line = channels * width
    q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)


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


class Histogram(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

        self.ax.set_xlim([0, 257])
        self.ax.set_ylim([0, None])
        # self.ax.set_xticks([])
        # self.ax.set_yticks([])
        
        self.plot_blue, = self.ax.plot(np.zeros(256), color="b")
        self.plot_green, = self.ax.plot(np.zeros(256), color="g")
        self.plot_red, = self.ax.plot(np.zeros(256), color="r")

        # self.fig.tight_layout()

        self.setFixedSize(300, 150)
    
    @pyqtSlot(np.ndarray)
    def update_data(self, histogram):
        print(histogram.max())
        self.plot_blue.set_xdata(histogram[0])
        self.plot_green.set_xdata(histogram[1])
        self.plot_red.set_xdata(histogram[2])

        # self.ax.set_ylim([0, histogram.max()])
        self.ax.set_ylim([0, 0.003])

        self.draw()


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.scanner = FilmScanner()

        self.setWindowTitle("Live View")

        self.image_label = QLabel()
        self.image_label.resize(1024, 768)

        self.histogram = Histogram()

        self.button = QPushButton("Advance")
        self.button.clicked.connect(self.clicked_advance)

        self.button2 = QPushButton("Other")

        hbox = QHBoxLayout()
        hbox.addWidget(self.image_label)
        vbox = QVBoxLayout()
        vbox.addWidget(self.histogram)
        vbox.addWidget(self.button)
        vbox.addWidget(self.button2)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        self.video_thread = VideoThread(self.scanner.camera)
        self.video_thread.change_image_signal.connect(self.update_image)
        self.video_thread.change_histogram_signal.connect(self.histogram.update_data)
        self.video_thread.start()
    
    @pyqtSlot(np.ndarray)
    def update_image(self, image):
        q_pixmap = cv2qt(image)
        # print(histogram)
        self.image_label.setPixmap(q_pixmap)
    
    @pyqtSlot()
    def clicked_advance(self):
        self.video_thread.not_advancing_event.clear()
        self.scanner.advance()
        self.video_thread.not_advancing_event.set()
    

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
    sys.exit(app.exec_())
