import cv2
import depthai as dai
import numpy as np
import control_vals as cv  # Import the control values module


def save_bar_positions(horizontal1, horizontal2, vertical1, vertical2, vertical3, vertical4):
    """Save the adjusted bar positions to control_vals.py."""
    with open("control_vals.py", "r") as file:
        lines = file.readlines()

    with open("control_vals.py", "w") as file:
        inside_bar_positions = False
        for line in lines:
            if line.strip().startswith("BAR_POSITIONS ="):
                inside_bar_positions = True
                file.write(
                    f"BAR_POSITIONS = {{\n"
                    f"    'horizontal1': {horizontal1},  # Default position for the first horizontal bar\n"
                    f"    'horizontal2': {horizontal2},  # Default position for the second horizontal bar\n"
                    f"    'vertical1': {vertical1},    # Default position for the first vertical bar\n"
                    f"    'vertical2': {vertical2},    # Default position for the second vertical bar\n"
                    f"    'vertical3': {vertical3},    # Default position for the third vertical bar\n"
                    f"    'vertical4': {vertical4}     # Default position for the fourth vertical bar\n"
                    f"}}\n"
                )
            elif inside_bar_positions and line.strip() == "}":
                inside_bar_positions = False
            elif not inside_bar_positions:
                file.write(line)


def adjust_bars():
    """Adjust the horizontal and vertical bar positions using trackbars."""
    # Load initial bar positions from control_vals.py
    positions = cv.BAR_POSITIONS
    horizontal1 = positions["horizontal1"]
    horizontal2 = positions["horizontal2"]
    vertical1 = positions["vertical1"]
    vertical2 = positions["vertical2"]
    vertical3 = positions["vertical3"]
    vertical4 = positions["vertical4"]

    # Create separate windows: one for trackbars, one for camera feed
    cv2.namedWindow("Trackbars", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Camera Feed", cv2.WINDOW_AUTOSIZE)

    # Add trackbars in the "Trackbars" window
    cv2.createTrackbar("Horizontal 1", "Trackbars", horizontal1, 100, lambda x: None)
    cv2.createTrackbar("Horizontal 2", "Trackbars", horizontal2, 100, lambda x: None)
    cv2.createTrackbar("Vertical 1", "Trackbars", vertical1, 100, lambda x: None)
    cv2.createTrackbar("Vertical 2", "Trackbars", vertical2, 100, lambda x: None)
    cv2.createTrackbar("Vertical 3", "Trackbars", vertical3, 100, lambda x: None)
    cv2.createTrackbar("Vertical 4", "Trackbars", vertical4, 100, lambda x: None)

    # Initialize the OAK-D Lite pipeline
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    print("Adjust the bars using the sliders. Press 'q' to save and exit.")

    with dai.Device(pipeline) as device:
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            in_frame = rgb_queue.get()
            frame = in_frame.getCvFrame()

            height, width = frame.shape[:2]

            # Get trackbar positions
            horizontal1 = cv2.getTrackbarPos("Horizontal 1", "Trackbars")
            horizontal2 = cv2.getTrackbarPos("Horizontal 2", "Trackbars")
            vertical1 = cv2.getTrackbarPos("Vertical 1", "Trackbars")
            vertical2 = cv2.getTrackbarPos("Vertical 2", "Trackbars")
            vertical3 = cv2.getTrackbarPos("Vertical 3", "Trackbars")
            vertical4 = cv2.getTrackbarPos("Vertical 4", "Trackbars")

            # Calculate pixel positions
            h1_pixel = int(height * (1 - horizontal1 / 100))
            h2_pixel = int(height * (1 - horizontal2 / 100))
            v1_pixel = int(width * (vertical1 / 100))
            v2_pixel = int(width * (vertical2 / 100))
            v3_pixel = int(width * (vertical3 / 100))
            v4_pixel = int(width * (vertical4 / 100))

            # Draw the bars on the frame
            cv2.line(frame, (0, h1_pixel), (width, h1_pixel), (0, 255, 0), 2)      # Horizontal 1
            cv2.line(frame, (0, h2_pixel), (width, h2_pixel), (0, 255, 255), 2)    # Horizontal 2
            cv2.line(frame, (v1_pixel, 0), (v1_pixel, height), (255, 0, 0), 2)     # Vertical 1
            cv2.line(frame, (v2_pixel, 0), (v2_pixel, height), (255, 0, 255), 2)   # Vertical 2
            cv2.line(frame, (v3_pixel, 0), (v3_pixel, height), (255, 255, 0), 2)   # Vertical 3
            cv2.line(frame, (v4_pixel, 0), (v4_pixel, height), (255, 255, 255), 2) # Vertical 4

            # Display the frame in the "Camera Feed" window
            cv2.imshow("Camera Feed", frame)

            # Check for user input
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                # Save bar positions to control_vals.py
                save_bar_positions(horizontal1, horizontal2, vertical1, vertical2, vertical3, vertical4)
                print("Bar positions saved.")
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    adjust_bars()

