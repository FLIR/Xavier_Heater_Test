#!/usr/bin/python3

import cv2
import numpy as np
import matplotlib.pyplot as plt


class BosonCamera:
    stop_signal = False
    vid = None
    current_frame = None

    def initialize(self):
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'RGGB'))
        self.vid.set(cv2.CAP_PROP_CONVERT_RGB, False)

    def start(self, on_new_frame):
        stop_signal = False

        while self.vid.isOpened() and not self.stop_signal:
            empty, self.current_frame = self.vid.read()
            color_frame = np.repeat(self.current_frame[:, :, np.newaxis], 3, axis=2)
            on_new_frame(color_frame)

    def stop(self):
        stop_signal = True

    def close(self):
        stop_signal = True
        self.vid.release()
