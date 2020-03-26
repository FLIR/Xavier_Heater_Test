#!/usr/bin/python3

import sys
from time import sleep

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *

from boson_video import BosonCamera
from boson_i2c import start_heater

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


class OverlayImage(QLabel):
    image = QImage()
    text = ""
    overlay = True
    capture_thread = None

    def __init__(self):
        super().__init__()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        qp.drawImage(QPoint(), self.image)

        if self.overlay:
            self.drawText(qp)

        qp.end()

    def drawText(self, qp):
        pen = QPen(Qt.yellow)
        pen.setWidth(1)
        qp.setPen(pen)

        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(14)
        qp.setFont(font)

        vpos = self.geometry().height() - 70
        hpos = self.geometry().width() / 2 - self.getTextOffset()
        qp.drawText(hpos, vpos, self.text)

    def getTextOffset(self):
        return 7.5 * len(self.text) / 2

    def setImage(self, image):
        self.image = image

    def setText(self, text):
        self.text = text

    def setOverlay(self, overlay):
        self.overlay = overlay


class App(QWidget):
    def __init__(self, camera):
        super().__init__()
        self.title = 'Boson Heater Test'
        self.left = 100
        self.top = 100
        self.width = 680
        self.height = 650

        self.camera = camera

        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.overlay_image.setImage(image)
        self.overlay_image.update()

    def onClose(self):
        if self.camera:
            self.camera.stop()
        self.capture_thread.wait()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Layout
        self.overlay_image = OverlayImage()
        pn_input_form = QFormLayout()
        self.pn_input = QLineEdit()
        pn_input_form.addRow(QLabel("PN:"), self.pn_input)
        overlay_check_form = QFormLayout()
        self.overlay_check = QCheckBox()
        overlay_check_form.addRow(QLabel("Overlay:"), self.overlay_check)
        self.save_button = QPushButton("Save")
        self.error_message_box = QLabel()

        self.error_message_box.setStyleSheet("color: red")

        main_grid = QVBoxLayout()
        main_grid.addStretch()
        img_grid = QGridLayout()
        control_grid = QHBoxLayout()
        control_grid.addStretch()
        control_grid.setSpacing(20)

        img_grid.addWidget(self.overlay_image)
        main_grid.addLayout(img_grid, 20)
        main_grid.addLayout(control_grid, 1)
        pn_input_form.setFormAlignment(Qt.AlignLeft)
        pn_input_form.setHorizontalSpacing(10)
        control_grid.addLayout(pn_input_form, 2)
        overlay_check_form.setHorizontalSpacing(10)
        control_grid.addLayout(overlay_check_form, 2)
        control_grid.addWidget(self.save_button, 1)
        self.error_message_box.setAlignment(Qt.AlignCenter)
        main_grid.addWidget(self.error_message_box, 1)

        self.setLayout(main_grid)

        self.overlay_check.setChecked(True)
        self.overlay_check.stateChanged.connect(self.overlayChanged)
        self.save_button.clicked.connect(self.saveImage)
        self.pn_input.textChanged.connect(self.pnChanged)

        self.capture_thread = VideoThread(self, self.camera)
        self.capture_thread.changePixmap.connect(self.setImage)
        self.capture_thread.start()
        self.show()

    def overlayChanged(self):
        value = self.overlay_check.isChecked()
        self.camera.set_overlay(value)
        self.overlay_image.setOverlay(value)

    def pnChanged(self):
        pn_text = self.pn_input.text()
        self.camera.set_pn(pn_text)
        self.overlay_image.setText(pn_text)

    def saveImage(self):
        self.error_message_box.setText('')
        if self.pn_input.text().strip() == '':
            self.error_message_box.setText('Must enter part number')
            return
        self.camera.save_image()


if __name__ == '__main__':
    cam = BosonCamera()
    cam.initialize()
    start_heater()

    try:
        app = QApplication(sys.argv)
        ex = App(cam)
        app.aboutToQuit.connect(ex.onClose)
        app.exit(app.exec_())
    finally:
        cam.stop()
