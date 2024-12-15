import cv2
import numpy as np
import control_vals as cv

def filter_yellow_line(frame):
    """Filter the yellow line using saved HSV values."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_values = cv.HSV_VALUES["yellow"]
    lower_bound = np.array([hsv_values["LOW_H"], hsv_values["LOW_S"], hsv_values["LOW_V"]])
    upper_bound = np.array([hsv_values["HIGH_H"], hsv_values["HIGH_S"], hsv_values["HIGH_V"]])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

