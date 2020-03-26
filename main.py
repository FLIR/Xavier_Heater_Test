#!/usr/bin/python3

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QPainter

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


class OverlayImage(QWidget):
    def __init__(self):
        super.__init__()

    def initUI(self):
        self.img_container = QLabel()
        self.img_container.setPixmap(QPixmap())
        self.overlay_text = QLabel("Test")

    def setImage(self, pixmap):
        self.img_container.setPixmap(pixmap)


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
        self.img_container.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Layout
        self.img_container = QLabel()
        pn_input_form = QFormLayout()
        self.pn_input = QLineEdit()
        pn_input_form.addRow(QLabel("PN:"), self.pn_input)
        overlay_check_form = QFormLayout()
        self.overlay_check = QCheckBox()
        overlay_check_form.addRow(QLabel("Overlay:"), self.overlay_check)
        self.save_button = QPushButton("Save")
        self.error_message_box = QLabel()
        self.overlay_text = QLabel(self)

        self.overlay_text.setText("Test")
        self.overlay_text.move(100, 100)

        self.error_message_box.setText("asdfd")
        self.error_message_box.setStyleSheet("color: red")

        main_grid = QVBoxLayout()
        main_grid.addStretch()
        img_grid = QGridLayout()
        control_grid = QHBoxLayout()
        control_grid.addStretch()
        control_grid.setSpacing(20)

        self.img_container.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        img_grid.addWidget(self.img_container)
        # img_grid.addWidget(self.overlay_text)
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

        v_offset = 100
        move_p = QPoint(200, -200)
        self.overlay_text.move(move_p)

        th = VideoThread(self, self.camera)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()

    def overlayChanged(self):
        value = self.overlay_check.isChecked()
        self.camera.set_overlay(value)

    def pnChanged(self):
        self.camera.set_pn(self.pn_input.text())

    def saveImage(self):
        self.camera.save_image()

if __name__ == '__main__':
    cam = BosonCamera()
    cam.initialize()

    app = QApplication(sys.argv)
    ex = App(cam)
    app.exit(app.exec_())
    cam.stop()

