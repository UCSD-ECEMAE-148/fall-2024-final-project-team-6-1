def calculate_steering_offset(cx, frame_width, centerline):
    """Calculate the steering offset based on the line's position."""
    centerline_x = int(frame_width * centerline / 100)
    offset = (cx - centerline_x) / centerline_x  # Normalize offset to range [-1, 1]
    return offset

