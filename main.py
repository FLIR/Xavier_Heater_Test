#!/usr/bin/python3

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

from boson_video import BosonCamera


class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, app, camera):
        super().__init__(app)
        self.camera = camera

    def run(self):
        self.camera.start(self.set_image)

    def set_image(self, img):
        h, w, c = img.shape
        convertToQtFormat = QImage(img, w, h, w * c, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 513, Qt.KeepAspectRatio)
        self.changePixmap.emit(p)


class App(QWidget):
    def __init__(self, camera):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 512

        self.camera = camera

        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(1000, 800)
        # create a label
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 512)
        th = VideoThread(self, self.camera)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()

if __name__ == '__main__':
    cam = BosonCamera()
    cam.initialize()

    app = QApplication(sys.argv)
    ex = App(cam)
    app.exit(app.exec_())
    cam.close()

