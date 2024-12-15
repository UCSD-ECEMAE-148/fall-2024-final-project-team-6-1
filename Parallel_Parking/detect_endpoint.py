import cv2

def detect_endpoint(mask, vertical_lines, debug_frame=None):
    """
    Detect if yellow is present outside the vertical lines (left and right)
    and below the horizontal line.
    """
    height, width = mask.shape
    line1_x = int(width * vertical_lines["line1_x_percent"] / 100)
    line2_x = int(width * vertical_lines["line2_x_percent"] / 100)

    left_region = mask[:, :line1_x]
    right_region = mask[:, line2_x:]

    yellow_in_left = cv2.countNonZero(left_region) > 0
    yellow_in_right = cv2.countNonZero(right_region) > 0

    if debug_frame is not None:
        cv2.line(debug_frame, (line1_x, 0), (line1_x, height), (0, 255, 0), 2)
        cv2.line(debug_frame, (line2_x, 0), (line2_x, height), (0, 255, 0), 2)

    return yellow_in_left and yellow_in_right

