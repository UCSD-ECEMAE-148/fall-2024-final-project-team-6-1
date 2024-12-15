def crop_frame(frame, horizontal_y_percent):
    """Crop the frame to keep only the area below the horizontal line."""
    height = frame.shape[0]
    horizontal_y = int(height * (1 - horizontal_y_percent / 100))
    return frame[horizontal_y:, :]

