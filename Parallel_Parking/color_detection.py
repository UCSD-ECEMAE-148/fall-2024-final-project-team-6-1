# color_detection.py

import cv2
import depthai as dai
import logging
import numpy as np
import control_vals as cv

# Initialize logger
logger = logging.getLogger('LineFollowing')

def detect_color_in_boxes(color, device):
    """
    Searches for the specified color in designated boxes.
    Returns True and the side ('Left' or 'Right') if the color is detected in both required boxes on either side.
    
    Now using top-to-bottom logic:
    Row 1 = Top, Row 2 = Middle, Row 3 = Bottom

    Left side: boxes (1,2) and (3,2)  # top and bottom row in column 2
    Right side: boxes (1,4) and (3,4) # top and bottom row in column 4
    """
    left_boxes = [(1,2), (3,2)]
    right_boxes = [(1,4), (3,4)]
    color_hsv = cv.HSV_VALUES.get(color)

    if not color_hsv:
        logger.error(f"HSV values for color '{color}' not found.")
        return (False, None)

    rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
    in_frame = rgb_queue.get()
    frame = in_frame.getCvFrame()

    def get_roi(frame, row, col):
        h, w = frame.shape[:2]

        # Convert bar positions from bottom to top-based coordinates:
        y_h1 = h - int(h * cv.BAR_POSITIONS['horizontal1'] / 100)
        y_h2 = h - int(h * cv.BAR_POSITIONS['horizontal2'] / 100)

        # Rows top-to-bottom:
        # Row 1 (top):    0 to y_h2
        # Row 2 (middle): y_h2 to y_h1
        # Row 3 (bottom): y_h1 to h
        if row == 1:
            y1, y2 = 0, y_h2
        elif row == 2:
            y1, y2 = y_h2, y_h1
        elif row == 3:
            y1, y2 = y_h1, h
        else:
            logger.error(f"Invalid row number: {row}")
            return None

        x_v1 = int(w * cv.BAR_POSITIONS['vertical1'] / 100)
        x_v2 = int(w * cv.BAR_POSITIONS['vertical2'] / 100)
        x_v3 = int(w * cv.BAR_POSITIONS['vertical3'] / 100)
        x_v4 = int(w * cv.BAR_POSITIONS['vertical4'] / 100)

        if col == 1:
            x1, x2 = 0, x_v1
        elif col == 2:
            x1, x2 = x_v1, x_v2
        elif col == 3:
            x1, x2 = x_v2, x_v3
        elif col == 4:
            x1, x2 = x_v3, x_v4
        elif col == 5:
            x1, x2 = x_v4, w
        else:
            logger.error(f"Invalid column number: {col}")
            return None

        return frame[y1:y2, x1:x2]

    def detect_color_in_roi(roi, hsv_values):
        if roi is None or roi.size == 0:
            return False
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower = np.array([hsv_values["LOW_H"], hsv_values["LOW_S"], hsv_values["LOW_V"]])
        upper = np.array([hsv_values["HIGH_H"], hsv_values["HIGH_S"], hsv_values["HIGH_V"]])
        mask = cv2.inRange(hsv, lower, upper)
        return cv2.countNonZero(mask) > 0

    # Check left side boxes
    left_detected = all([detect_color_in_roi(get_roi(frame, r, c), color_hsv) for (r, c) in left_boxes])

    # Check right side boxes
    right_detected = all([detect_color_in_roi(get_roi(frame, r, c), color_hsv) for (r, c) in right_boxes])

    if left_detected:
        return (True, "Left")
    elif right_detected:
        return (True, "Right")
    else:
        return (False, None)


def is_color_present_in_row(color, device, row):
    """
    Checks if the specified color is present in the given row across columns 2 and 4.
    Row indexing top-to-bottom: 1=Top, 2=Middle, 3=Bottom
    """
    columns = [2, 4]
    color_hsv = cv.HSV_VALUES.get(color)

    if not color_hsv:
        logger.error(f"HSV values for color '{color}' not found.")
        return False

    rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
    in_frame = rgb_queue.get()
    frame = in_frame.getCvFrame()

    def get_roi(frame, row, col):
        h, w = frame.shape[:2]

        y_h1 = h - int(h * cv.BAR_POSITIONS['horizontal1'] / 100)
        y_h2 = h - int(h * cv.BAR_POSITIONS['horizontal2'] / 100)

        if row == 1:
            y1, y2 = 0, y_h2
        elif row == 2:
            y1, y2 = y_h2, y_h1
        elif row == 3:
            y1, y2 = y_h1, h
        else:
            logger.error(f"Invalid row number: {row}")
            return None

        x_v1 = int(w * cv.BAR_POSITIONS['vertical1'] / 100)
        x_v2 = int(w * cv.BAR_POSITIONS['vertical2'] / 100)
        x_v3 = int(w * cv.BAR_POSITIONS['vertical3'] / 100)
        x_v4 = int(w * cv.BAR_POSITIONS['vertical4'] / 100)

        if col == 1:
            x1, x2 = 0, x_v1
        elif col == 2:
            x1, x2 = x_v1, x_v2
        elif col == 3:
            x1, x2 = x_v2, x_v3
        elif col == 4:
            x1, x2 = x_v3, x_v4
        elif col == 5:
            x1, x2 = x_v4, w
        else:
            logger.error(f"Invalid column number: {col}")
            return None

        return frame[y1:y2, x1:x2]

    def detect_color_in_roi(roi, hsv_values):
        if roi is None or roi.size == 0:
            return False
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower = np.array([hsv_values["LOW_H"], hsv_values["LOW_S"], hsv_values["LOW_V"]])
        upper = np.array([hsv_values["HIGH_H"], hsv_values["HIGH_S"], hsv_values["HIGH_V"]])
        mask = cv2.inRange(hsv, lower, upper)
        return cv2.countNonZero(mask) > 0

    for col in columns:
        roi = get_roi(frame, row, col)
        if roi is None:
            continue
        if detect_color_in_roi(roi, color_hsv):
            return True

    return False

