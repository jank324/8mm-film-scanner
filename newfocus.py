import sys
from threading import Event

import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel, QPushButton

from filmscanner import FilmScanner


def cv2qt(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb.shape
    bytes_per_line = channels * width
    q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)


class VideoThread(QThread):
    
    change_pixmap_signal = pyqtSignal(np.ndarray)
    not_advancing_event = Event()

    def __init__(self, camera):
        super().__init__()

        self.camera = camera
        self.camera.resolution = (1024, 768)

        self.not_advancing_event.set()

    def run(self):
        bgr = np.empty((768, 1024,3), dtype=np.uint8)

        for _ in self.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            self.change_pixmap_signal.emit(bgr)
            self.not_advancing_event.wait()


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.scanner = FilmScanner()

        self.setWindowTitle("Live View")

        self.image_label = QLabel()
        self.image_label.resize(1024, 768)

        self.button = QPushButton("Advance")
        self.button.clicked.connect(self.clicked_advance)

        hbox = QHBoxLayout()
        hbox.addWidget(self.image_label)
        hbox.addWidget(self.button)
        self.setLayout(hbox)

        self.video_thread = VideoThread(self.scanner.camera)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()
    
    @pyqtSlot(np.ndarray)
    def update_image(self, image):
        q_pixmap = cv2qt(image)
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
