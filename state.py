import win32gui
import win32ui
from ctypes import windll
import numpy as np
import mss
import cv2
import time

class State:
    def __init__(self, monitor):

        self.monitor = monitor
        self.head = cv2.imread("head.jpeg",cv2.IMREAD_GRAYSCALE)
        self.sct = mss.mss()
        self.temp_result_value = 0

    def screenshot(self):
        with mss.mss() as sct:
            return cv2.cvtColor(np.array(sct.grab(self.monitor)), cv2.COLOR_BGRA2RGB)

    def process_frame(self, frame):
        # crop frame
        frame = frame[170: 330, 130:430]

        # get only black color

        frame = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))

        return frame

    def get_state(self):
        frame = self.screenshot()
        frame = frame[175: 345, 120:420]
        frame = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))
        result = cv2.matchTemplate(frame, self.head, cv2.TM_CCOEFF_NORMED)

        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
        x, y = maxLoc
        self.temp_result_value = result[y][x]
        # return [x / len(result[0]), y / len(result)]

        return [x / len(result[0])]

        # return self.process_frame(self.screenshot())

    def is_over(self):
        return self.temp_result_value < 0.45



