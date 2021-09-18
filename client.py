import sys

import cv2
import numpy as np
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from remote_filmscanner import RemoteFilmScanner


class VideoThread(qtc.QThread):
    
    new_frame = qtc.pyqtSignal(np.ndarray)

    def __init__(self, scanner):
        super().__init__()

        self.scanner = scanner

    def run(self):
        while True:
            frame = self.scanner.receive_frame()
            self.new_frame.emit(frame)


class ImageView(qtw.QLabel):

    def __init__(self, image):
        super().__init__()

        self.show(image)
    
    def show(self, image):
        q_pixmap = self.cv2qt(image)
        self.setPixmap(q_pixmap)
    
    def cv2qt(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        bytes_per_line = channels * width
        q_image = qtg.QImage(rgb.data, width, height, bytes_per_line, qtg.QImage.Format_RGB888)
        return qtg.QPixmap.fromImage(q_image)


class App(qtw.QWidget):

    def __init__(self):
        super().__init__()

        self.scanner = RemoteFilmScanner(host="192.168.178.48", video_port=7778)

        self.setWindowTitle("8mm Film Scanner Setup")

        self.live_view = ImageView(np.zeros((768,1024,3), dtype=np.uint8))
        self.video_thread = VideoThread(self.scanner)
        self.video_thread.new_frame.connect(self.live_view.show)

        self.advance_button = qtw.QPushButton("Advance")
        # self.advance_button.clicked.connect(self.clicked_advance)

        hbox = qtw.QHBoxLayout()
        self.setLayout(hbox)
        hbox.addWidget(self.live_view)
        vbox = qtw.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addWidget(self.advance_button)
        vbox.addStretch()

        self.video_thread.start()
    
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
