# test_color_detection.py

import cv2
import depthai as dai
import numpy as np
import time
import threading
import inputs
import logging
from logger_config import setup_logger
import control_vals as cv  # Ensure control_vals.py is in the same directory

# Setup logger for the test script
logger = setup_logger('TestColorDetection', 'test_color_detection.log')

class ControllerTest:
    def __init__(self):
        self.selected_color = None  # 'blue', 'green', 'red'
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._poll_controller, daemon=True)
        self._thread.start()
        self._last_press_time = 0
        self._debounce_delay = 0.3  # 300 ms debounce delay
        logger.info("Controller polling thread initialized for test script.")
    
    def _poll_controller(self):
        """
        Background thread to poll the controller for color selection.
        """
        logger.debug("Controller polling thread started for test script.")
        while not self._stop_event.is_set():
            try:
                events = inputs.get_gamepad()
                for event in events:
                    if event.ev_type == "Key" and event.state == 1:  # Button pressed
                        current_time = time.time()
                        if current_time - self._last_press_time < self._debounce_delay:
                            continue  # Ignore if within debounce delay
                        if event.code == "BTN_NORTH":  # X Button - Blue
                            with self._lock:
                                self.selected_color = 'blue'
                                print("Selected Color: Blue")
                                logger.info("Controller: Selected Blue")
                            self._last_press_time = current_time
                        elif event.code == "BTN_SOUTH":  # A Button - Green
                            with self._lock:
                                self.selected_color = 'green'
                                print("Selected Color: Green")
                                logger.info("Controller: Selected Green")
                            self._last_press_time = current_time
                        elif event.code == "BTN_EAST":  # B Button - Red
                            with self._lock:
                                self.selected_color = 'red'
                                print("Selected Color: Red")
                                logger.info("Controller: Selected Red")
                            self._last_press_time = current_time
                        elif event.code == "BTN_WEST":  # Y Button - Reset Selection
                            # For this test script, Y Button can reset the selection
                            with self._lock:
                                self.selected_color = None
                                print("Color Selection Reset")
                                logger.info("Controller: Color selection reset")
                            self._last_press_time = current_time
            except inputs.UnpluggedError:
                logger.warning("Controller disconnected. Waiting for reconnection...")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                logger.error(f"Error polling controller in test script: {e}")
                time.sleep(0.1)  # Brief pause before retrying
    
    def get_selected_color(self):
        """
        Retrieve the currently selected color.
        """
        with self._lock:
            return self.selected_color
    
    def stop(self):
        """
        Stop the controller polling thread.
        """
        logger.info("Stopping controller polling thread for test script...")
        self._stop_event.set()
        self._thread.join()
        logger.info("Controller polling thread stopped for test script.")

def draw_bars(frame, bars):
    """
    Draw horizontal and vertical bars on the frame based on the positions defined in bars.
    
    Args:
        frame (np.ndarray): The image frame.
        bars (dict): Dictionary containing bar positions as percentages.
    
    Returns:
        np.ndarray: The frame with bars drawn.
    """
    height, width, _ = frame.shape
    # Draw horizontal bars from the bottom
    h1_percent = bars["horizontal1"]  # Percentage from bottom
    h2_percent = bars["horizontal2"]  # Percentage from bottom
    h1 = height - int(height * h1_percent / 100)
    h2 = height - int(height * h2_percent / 100)
    cv2.line(frame, (0, h1), (width, h1), (0, 255, 0), 2)  # Green line
    cv2.line(frame, (0, h2), (width, h2), (0, 255, 0), 2)  # Green line
    
    # Draw vertical bars
    v1 = int(width * bars["vertical1"] / 100)
    v2 = int(width * bars["vertical2"] / 100)
    v3 = int(width * bars["vertical3"] / 100)
    v4 = int(width * bars["vertical4"] / 100)
    cv2.line(frame, (v1, 0), (v1, height), (255, 0, 0), 2)  # Blue line
    cv2.line(frame, (v2, 0), (v2, height), (255, 0, 0), 2)  # Blue line
    cv2.line(frame, (v3, 0), (v3, height), (255, 0, 0), 2)  # Blue line
    cv2.line(frame, (v4, 0), (v4, height), (255, 0, 0), 2)  # Blue line
    
    return frame

def filter_color(frame, color):
    """
    Apply HSV filtering to isolate the specified color in the frame.
    
    Args:
        frame (np.ndarray): The image frame.
        color (str): The color to filter ('blue', 'green', 'red').
    
    Returns:
        np.ndarray: The mask image where the color is white and the rest is black.
    """
    hsv_values = cv.HSV_VALUES.get(color)
    if not hsv_values:
        logger.error(f"No HSV values found for color: {color}")
        return np.zeros(frame.shape[:2], dtype=np.uint8)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv_values["LOW_H"], hsv_values["LOW_S"], hsv_values["LOW_V"]])
    upper = np.array([hsv_values["HIGH_H"], hsv_values["HIGH_S"], hsv_values["HIGH_V"]])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

def main():
    # Initialize Controller Test
    controller = ControllerTest()
    
    # Create pipeline for OAK-D Lite
    pipeline = dai.Pipeline()
    
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)
    
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)
    
    with dai.Device(pipeline) as device:
        print("Connected to OAK-D Lite Device. Press X, A, or B on the controller to select a color.")
        print("Press Y to reset color selection. Press 'q' in any window to exit.")
        logger.info("Starting test script: Live Feed with Bars and Color Filtering.")
        
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        
        while True:
            try:
                in_frame = rgb_queue.get()
                frame = in_frame.getCvFrame()
                
                # Draw bars on the live frame
                frame_with_bars = draw_bars(frame.copy(), cv.BAR_POSITIONS)
                
                # Get the selected color from the controller
                selected_color = controller.get_selected_color()
                
                if selected_color:
                    # Apply color filtering
                    color_mask = filter_color(frame, selected_color)
                    color_filtered = cv2.bitwise_and(frame, frame, mask=color_mask)
                    
                    # Display selected color
                    cv2.putText(color_filtered, f"Color: {selected_color.capitalize()}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    # If no color is selected, display a black image with text
                    color_filtered = np.zeros(frame.shape, dtype=np.uint8)
                    cv2.putText(color_filtered, "No Color Selected", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                
                # Show the live feed with bars
                cv2.imshow("Live Feed with Bars", frame_with_bars)
                
                # Show the color-filtered view
                cv2.imshow("Color Filtered View", color_filtered)
                
                # Exit if 'q' is pressed in any window
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting test script...")
                    logger.info("User initiated exit via 'q' key.")
                    break
            
            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting test script...")
                logger.info("Test script interrupted by user via KeyboardInterrupt.")
                break
            except Exception as e:
                logger.error(f"Exception in test script: {e}")
                break
    
    # Cleanup
    controller.stop()
    cv2.destroyAllWindows()
    logger.info("Test script terminated gracefully.")

if __name__ == "__main__":
    main()

