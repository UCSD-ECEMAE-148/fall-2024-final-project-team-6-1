import cv2
import numpy as np
import depthai as dai
import control_vals as cv

CONTROL_VALS_FILE = "control_vals.py"

def empty(a):
    """Dummy function for trackbar callback."""
    pass

def create_crop_trackbar():
    """Create trackbars to adjust the cropping range."""
    cv2.namedWindow("Crop Adjustment")
    cv2.resizeWindow("Crop Adjustment", 400, 100)

    # Create trackbars for high crop (top) and low crop (bottom)
    cv2.createTrackbar("High Crop", "Crop Adjustment", cv.HIGH_CROP, 100, empty)
    cv2.createTrackbar("Low Crop", "Crop Adjustment", cv.LOW_CROP, 100, empty)

def get_crop_values():
    """Get the current cropping range from the trackbars."""
    high_crop = cv2.getTrackbarPos("High Crop", "Crop Adjustment")
    low_crop = cv2.getTrackbarPos("Low Crop", "Crop Adjustment")
    return high_crop, low_crop

def save_crop_values(high_crop, low_crop):
    """Save the adjusted cropping range to control_vals.py."""
    with open(CONTROL_VALS_FILE, "r") as file:
        lines = file.readlines()

    # Update the HIGH_CROP and LOW_CROP values in control_vals.py
    for i, line in enumerate(lines):
        if line.strip().startswith("HIGH_CROP ="):
            lines[i] = f"HIGH_CROP = {high_crop}\n"
        elif line.strip().startswith("LOW_CROP ="):
            lines[i] = f"LOW_CROP = {low_crop}\n"

    with open(CONTROL_VALS_FILE, "w") as file:
        file.writelines(lines)
    print(f"Crop values saved: High Crop = {high_crop}%, Low Crop = {low_crop}%")

def main():
    # Create the camera pipeline
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)

    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")

    cam_rgb.preview.link(xout_rgb.input)

    # Create trackbars for adjusting crop range
    create_crop_trackbar()

    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite. Starting crop adjustment...")

        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            # Get the latest frame from the camera
            in_frame = rgb_queue.get()
            frame = in_frame.getCvFrame()

            # Get the current crop values
            high_crop, low_crop = get_crop_values()

            # Ensure valid crop ranges
            if high_crop > low_crop:
                high_crop, low_crop = low_crop, high_crop

            # Convert crop values from percentages to pixel ranges
            height = frame.shape[0]
            high_pixel = int(height * high_crop / 100)
            low_pixel = int(height * low_crop / 100)

            # Draw the cropped region on the frame
            display_frame = frame.copy()
            cv2.rectangle(display_frame, (0, high_pixel), (frame.shape[1], low_pixel), (0, 255, 0), 2)

            # Display the frame with the cropping overlay
            cv2.imshow("Crop Adjustment", display_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                save_crop_values(high_crop, low_crop)
                print("Exiting...")
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

