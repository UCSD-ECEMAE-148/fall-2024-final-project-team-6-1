import cv2

def get_line_position(mask):
    """Calculate the position of the yellow line in the cropped frame."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])  # x-coordinate of the centroid
            return cx
    return None

