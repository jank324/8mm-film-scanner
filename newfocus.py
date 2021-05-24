import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel, QPushButton


def cv2qt(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb.shape
    bytes_per_line = channels * width
    q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        image = cv2.imread("mercedes_a-class_review31.jpg", cv2.IMREAD_COLOR)
        q_pixmap = cv2qt(image)

        self.setWindowTitle("Live View")

        hbox = QHBoxLayout()

        image_label = QLabel()
        image_label.setPixmap(q_pixmap)
        hbox.addWidget(image_label)

        button = QPushButton("Click me!")
        hbox.addWidget(button)

        self.setLayout(hbox)

        self.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
