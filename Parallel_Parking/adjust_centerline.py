import cv2
import numpy as np
import depthai as dai
import control_vals as cv

CONTROL_VALS_FILE = "control_vals.py"

def empty(a):
    """Dummy function for trackbar callback."""
    pass

def create_centerline_trackbar():
    """Create a trackbar to adjust the vertical centerline."""
    cv2.namedWindow("Centerline Adjustment")
    cv2.resizeWindow("Centerline Adjustment", 400, 100)

    # Create trackbar for centerline adjustment (0-100% of the frame width)
    cv2.createTrackbar("Centerline", "Centerline Adjustment", cv.VERTICAL_CENTERLINE, 100, empty)

def get_centerline():
    """Get the current centerline value from the trackbar."""
    return cv2.getTrackbarPos("Centerline", "Centerline Adjustment")

def save_centerline(value):
    """Save the adjusted centerline value to control_vals.py."""
    with open(CONTROL_VALS_FILE, "r") as file:
        lines = file.readlines()

    # Update the VERTICAL_CENTERLINE value in control_vals.py
    for i, line in enumerate(lines):
        if line.strip().startswith("VERTICAL_CENTERLINE ="):
            lines[i] = f"VERTICAL_CENTERLINE = {value}\n"
            break

    with open(CONTROL_VALS_FILE, "w") as file:
        file.writelines(lines)
    print(f"Centerline saved: {value}%")

def main():
    # Create trackbar for centerline adjustment
    create_centerline_trackbar()

    # Create the camera pipeline
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)

    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")

    cam_rgb.preview.link(xout_rgb.input)

    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite. Starting centerline adjustment...")

        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            # Get the latest frame from the camera
            in_frame = rgb_queue.get()
            frame = in_frame.getCvFrame()  # Convert to OpenCV format

            # Get the adjusted centerline value
            centerline = get_centerline()

            # Draw the centerline on the frame
            display_frame = frame.copy()
            center_x = int(frame.shape[1] * centerline / 100)
            cv2.line(display_frame, (center_x, 0), (center_x, frame.shape[0]), (0, 255, 0), 2)

            # Display the frame with the centerline
            cv2.imshow("Centerline Adjustment", display_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                save_centerline(centerline)
                print("Exiting...")
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

