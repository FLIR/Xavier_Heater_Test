#!/usr/bin/python3

import cv2
import numpy as np
import matplotlib.pyplot as plt


class BosonCamera:
    stop_signal = False

    def start(self, on_new_frame):
        stop_signal = False

        vid = cv2.VideoCapture(0)
        vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'RGGB'))
        vid.set(cv2.CAP_PROP_CONVERT_RGB, False)

        while vid.isOpened() and not self.stop_signal:
            empty, frame = vid.read()

            cv2.imshow("s", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        vid.release()

    def stop(self):
        stop_signal = True
