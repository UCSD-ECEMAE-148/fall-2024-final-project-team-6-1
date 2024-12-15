import cv2
import numpy as np
import depthai as dai
import control_vals as cv
import sys
import json
import ast

CONTROL_VALS_FILE = "control_vals.py"

def empty(a):
    """Dummy function for trackbar callback."""
    pass

def create_trackbars(color_hsv):
    """Create trackbars for adjusting HSV values of the specified color."""
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 400, 300)

    # Create trackbars initialized with current HSV values for the color
    cv2.createTrackbar("Low H", "Trackbars", color_hsv["LOW_H"], 179, empty)
    cv2.createTrackbar("High H", "Trackbars", color_hsv["HIGH_H"], 179, empty)
    cv2.createTrackbar("Low S", "Trackbars", color_hsv["LOW_S"], 255, empty)
    cv2.createTrackbar("High S", "Trackbars", color_hsv["HIGH_S"], 255, empty)
    cv2.createTrackbar("Low V", "Trackbars", color_hsv["LOW_V"], 255, empty)
    cv2.createTrackbar("High V", "Trackbars", color_hsv["HIGH_V"], 255, empty)

def get_hsv_values():
    """Get current HSV values from trackbars."""
    low_h = cv2.getTrackbarPos("Low H", "Trackbars")
    high_h = cv2.getTrackbarPos("High H", "Trackbars")
    low_s = cv2.getTrackbarPos("Low S", "Trackbars")
    high_s = cv2.getTrackbarPos("High S", "Trackbars")
    low_v = cv2.getTrackbarPos("Low V", "Trackbars")
    high_v = cv2.getTrackbarPos("High V", "Trackbars")
    return {
        "LOW_H": low_h,
        "HIGH_H": high_h,
        "LOW_S": low_s,
        "HIGH_S": high_s,
        "LOW_V": low_v,
        "HIGH_V": high_v
    }

def save_hsv_values(color, hsv_values):
    """Save HSV values for the specified color to control_vals.py."""
    with open(CONTROL_VALS_FILE, "r") as file:
        lines = file.readlines()

    # Locate the HSV_VALUES dictionary start line
    hsv_start_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith("HSV_VALUES = {"):
            hsv_start_line = i
            break

    if hsv_start_line is None:
        print("Error: HSV_VALUES dictionary not found in control_vals.py")
        return

    # Reconstruct the HSV_VALUES dictionary from the lines
    hsv_dict_lines = []
    open_braces = 0
    for line in lines[hsv_start_line:]:
        hsv_dict_lines.append(line)
        open_braces += line.count("{") - line.count("}")
        if open_braces == 0:
            break

    try:
        hsv_dict = ast.literal_eval("".join(hsv_dict_lines).split("=", 1)[1].strip())
    except SyntaxError as e:
        print("Error parsing HSV_VALUES dictionary:", e)
        return

    # Update the specified color's HSV values
    hsv_dict[color] = hsv_values

    # Replace the HSV_VALUES dictionary in the file
    new_hsv_dict = f"HSV_VALUES = {json.dumps(hsv_dict, indent=4)}\n"
    lines[hsv_start_line:hsv_start_line + len(hsv_dict_lines)] = [new_hsv_dict]

    # Save the updated file
    with open(CONTROL_VALS_FILE, "w") as file:
        file.writelines(lines)

#    print(f"HSV values saved for {color}.")


def filter_color(frame, hsv_values):
    """Apply color filtering to isolate the specified color."""
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the selected HSV range
    lower_bound = np.array([hsv_values["LOW_H"], hsv_values["LOW_S"], hsv_values["LOW_V"]])
    upper_bound = np.array([hsv_values["HIGH_H"], hsv_values["HIGH_S"], hsv_values["HIGH_V"]])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply the mask to the original frame
    color_filtered = cv2.bitwise_and(frame, frame, mask=mask)

    return color_filtered

def main():
    # Parse the color argument
    if len(sys.argv) != 2:
        print("Usage: python3 filter_adj_test.py <color>")
        print("Available colors: yellow, red, blue, green")
        exit(1)

    color = sys.argv[1].lower()
    if color not in cv.HSV_VALUES:
        print(f"Error: Invalid color '{color}'. Choose from yellow, red, blue, green.")
        exit(1)

    print(f"Adjusting HSV values for {color}...")

    # Get the initial HSV values for the specified color
    color_hsv = cv.HSV_VALUES[color]

    # Create the pipeline
    pipeline = dai.Pipeline()

    # Define a color camera node
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)

    # Create an XLinkOut node for RGB preview
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")

    # Link the camera to the XLinkOut
    cam_rgb.preview.link(xout_rgb.input)

    # Create trackbars for HSV adjustment
    create_trackbars(color_hsv)

    # Connect to the device and start the pipeline
    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite. Starting live view...")

        # Get the output queue for the RGB stream
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        try:
            while True:
                # Get the latest frame from the camera
                in_frame = rgb_queue.get()
                frame = in_frame.getCvFrame()  # Convert to OpenCV format

                # Get current HSV values from trackbars
                hsv_values = get_hsv_values()

                # Save HSV values after each adjustment
                save_hsv_values(color, hsv_values)

                # Filter the selected color using the adjusted HSV range
                color_filtered = filter_color(frame, hsv_values)

                # Display the original frame and the filtered color
                cv2.imshow("Original Live View", frame)
                cv2.imshow(f"Filtered {color.capitalize()} Color", color_filtered)

                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting...")
                    break

        except KeyboardInterrupt:
            print("\nShutting down...")

        finally:
            # Save the final HSV values on exit
            save_hsv_values(color, get_hsv_values())
            print(f"Final HSV values saved for {color}.")
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

