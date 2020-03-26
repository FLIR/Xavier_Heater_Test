#!/usr/bin/python3

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import threading

class BosonCamera:
    stop_signal = False
    vid = None
    current_frame = None
    overlay = True
    pn = ""

    def __init__(self):
        self.save_lock = threading.RLock()

    def initialize(self):
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'RGGB'))
        self.vid.set(cv2.CAP_PROP_CONVERT_RGB, False)

    def start(self, on_new_frame):
        stop_signal = False

        while self.vid.isOpened() and not self.stop_signal:
            empty, frame = self.vid.read()
            with self.save_lock:
                self.current_frame = np.repeat(frame[:, :, np.newaxis], 3, axis=2)
                on_new_frame(self.current_frame)

        self.vid.release()

    def stop(self):
        stop_signal = True

    def set_overlay(self, overlay):
        self.overlay = overlay

    def set_pn(self, pn):
        self.pn = pn

    def save_image(self):
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        filename = os.path.join(desktop, f'{self.pn}.png')
        with self.save_lock:
            cv2.imwrite(filename, self.current_frame)

