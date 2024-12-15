import cv2
import depthai as dai
import control_vals as cv


def save_lines_to_control_vals(line1_x_percent, line2_x_percent, horizontal_y_percent):
    """Save the vertical and horizontal line positions (as percentages) to control_vals.py."""
    with open("control_vals.py", "r") as file:
        lines = file.readlines()

    with open("control_vals.py", "w") as file:
        for line in lines:
            if line.strip().startswith("LINES"):
                file.write(
                    f"LINES = {{'line1_x_percent': {line1_x_percent}, 'line2_x_percent': {line2_x_percent}, "
                    f"'horizontal_y_percent': {horizontal_y_percent}}}\n"
                )
            else:
                file.write(line)


def load_saved_values():
    """Load the last saved values from control_vals.py."""
    try:
        saved_values = cv.LINES
        line1_x_percent = saved_values.get("line1_x_percent", 25)
        line2_x_percent = saved_values.get("line2_x_percent", 75)
        horizontal_y_percent = saved_values.get("horizontal_y_percent", 50)
    except AttributeError:
        # Fallback to default values if LINES is not defined
        line1_x_percent = 25
        line2_x_percent = 75
        horizontal_y_percent = 50

    return line1_x_percent, line2_x_percent, horizontal_y_percent


def main():
    # Load the saved values or use defaults
    line1_x_percent, line2_x_percent, horizontal_y_percent = load_saved_values()

    # Create the camera pipeline
    pipeline = dai.Pipeline()

    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)

    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")

    cam_rgb.preview.link(xout_rgb.input)

    def update_line1_percent(pos):
        """Update the position of the first vertical line (percentage of frame width)."""
        nonlocal line1_x_percent
        line1_x_percent = pos

    def update_line2_percent(pos):
        """Update the position of the second vertical line (percentage of frame width)."""
        nonlocal line2_x_percent
        line2_x_percent = pos

    def update_horizontal_y_percent(pos):
        """Update the position of the horizontal line (percentage of frame height)."""
        nonlocal horizontal_y_percent
        horizontal_y_percent = pos

    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite. Use the sliders to adjust the lines.")
        print("Press 's' to save the positions or 'q' to quit without saving.")

        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        # Create a window with sliders to adjust the line positions
        cv2.namedWindow("Set Lines")
        cv2.createTrackbar("Line 1 Position (%)", "Set Lines", line1_x_percent, 100, update_line1_percent)
        cv2.createTrackbar("Line 2 Position (%)", "Set Lines", line2_x_percent, 100, update_line2_percent)
        cv2.createTrackbar("Horizontal Line (%)", "Set Lines", horizontal_y_percent, 100, update_horizontal_y_percent)

        try:
            while True:
                # Get the latest frame from the camera
                in_frame = rgb_queue.get()
                frame = in_frame.getCvFrame()

                # Calculate line positions in pixels
                line1_x = int(cv.CAMERA_RESOLUTION_WIDTH * line1_x_percent / 100)
                line2_x = int(cv.CAMERA_RESOLUTION_WIDTH * line2_x_percent / 100)
                horizontal_y = int(cv.CAMERA_RESOLUTION_HEIGHT * (1 - horizontal_y_percent / 100))

                # Draw the vertical and horizontal lines on the frame
                cv2.line(frame, (line1_x, 0), (line1_x, frame.shape[0]), (0, 255, 0), 2)
                cv2.line(frame, (line2_x, 0), (line2_x, frame.shape[0]), (0, 255, 0), 2)
                cv2.line(frame, (0, horizontal_y), (frame.shape[1], horizontal_y), (255, 0, 0), 2)

                # Show the frame with the lines
                cv2.imshow("Set Lines", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):  # Save the line positions
                    save_lines_to_control_vals(line1_x_percent, line2_x_percent, horizontal_y_percent)
                    print(
                        f"Lines saved: line1_x_percent={line1_x_percent}, "
                        f"line2_x_percent={line2_x_percent}, horizontal_y_percent={horizontal_y_percent}"
                    )
                    break
                elif key == ord('q'):  # Quit without saving
                    print("Exiting without saving.")
                    break

        except KeyboardInterrupt:
            print("\nShutting down...")

        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

