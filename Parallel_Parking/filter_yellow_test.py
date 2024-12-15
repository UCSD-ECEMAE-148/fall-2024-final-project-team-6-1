import cv2
import numpy as np
import depthai as dai

def filter_yellow_line(frame):
    """Apply color filtering to isolate the yellow line."""
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define an expanded HSV range for yellow
    lower_yellow = np.array([15, 80, 80])  # Lower bound for yellow
    upper_yellow = np.array([45, 255, 255])  # Upper bound for yellow

    # Create a mask for yellow color
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Apply the mask to the original frame
    yellow_line = cv2.bitwise_and(frame, frame, mask=mask)

    return yellow_line

def main():
    # Create the pipeline
    pipeline = dai.Pipeline()

    # Define a color camera node
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(1280, 720)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    # Create an XLinkOut node for RGB preview
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")

    # Link the camera to the XLinkOut
    cam_rgb.preview.link(xout_rgb.input)

    # Connect to the device and start the pipeline
    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite. Starting live view...")

        # Get the output queue for the RGB stream
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            # Get the latest frame from the camera
            in_frame = rgb_queue.get()
            frame = in_frame.getCvFrame()  # Convert to OpenCV format

            # Filter the yellow line
            yellow_line = filter_yellow_line(frame)

            # Display the original frame and the filtered yellow line
            cv2.imshow("Original Live View", frame)
            cv2.imshow("Filtered Yellow Line", yellow_line)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting...")
                break

        # Clean up
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

