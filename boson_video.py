#!/usr/bin/python3

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import threading

IMG_FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE_COLOR = (255, 255, 255)

class BosonCamera:
    stop_signal = False
    vid = None
    current_frame = None
    overlay = True
    pn = ""
    width = 640
    height = 513

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
        self.stop_signal = True

    def set_overlay(self, overlay):
        self.overlay = overlay

    def set_pn(self, pn):
        self.pn = pn

    def save_image(self):
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        filename = os.path.join(desktop, f'{self.pn}.png')
        with self.save_lock:
            image = self.current_frame
            if(self.overlay):
                image = self.add_text_to_image()
            cv2.imwrite(filename, image)

    def add_text_to_image(self):
        loc = self.text_position()
        return cv2.putText(self.current_frame, self.pn, loc, IMG_FONT, .5, WHITE_COLOR, 1,
                cv2.LINE_AA)

    def text_position(self):
        y_loc = self.height - 10
        x_loc = 20
        return (x_loc, y_loc)
