# controller_input.py

import inputs
import threading
import time
import logging
from logger_config import setup_logger
import control_vals as cv  # Import control_vals for HSV values

# Setup logger for controller_input
logger = setup_logger('ControllerInput', 'controller_input.log')

class Controller:
    def __init__(self):
        self.motion_paused = False
        self.color_to_search = None  # Initialize color_to_search
        self._lock = threading.Lock()
        self._color_lock = threading.Lock()  # Lock for color_to_search
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._poll_controller, daemon=True)
        self._thread.start()
        self._last_press_time = 0
        self._debounce_delay = 0.3  # 300 ms debounce delay
        logger.info("Controller polling thread initialized.")

    def _poll_controller(self):
        """
        Background thread that polls the gamepad and toggles the motion_paused state
        or sets the color_to_search based on button presses.
        """
        logger.debug("Controller polling thread started.")
        while not self._stop_event.is_set():
            try:
                events = inputs.get_gamepad()
                for event in events:
                    if event.ev_type == "Key":
                        current_time = time.time()
                        # Handle Y button for pausing/resuming motion
                        if event.code == "BTN_WEST":  # Y button mapped to BTN_WEST
                            if event.state == 1:  # Button pressed
                                if current_time - self._last_press_time > self._debounce_delay:
                                    with self._lock:
                                        self.motion_paused = not self.motion_paused
                                        if self.motion_paused:
                                            logger.info("Motion paused.")
                                            print("Motion paused")
                                        else:
                                            logger.info("Motion resumed.")
                                            print("Motion resumed")
                                    self._last_press_time = current_time
                        # Handle X, A, B buttons for color search
                        elif event.code == "BTN_NORTH" and event.state == 1:  # X button
                            with self._color_lock:
                                self.color_to_search = 'blue'
                                logger.info("Color search initiated for Blue.")
                                print("Color search initiated for Blue.")
                        elif event.code == "BTN_SOUTH" and event.state == 1:  # A button
                            with self._color_lock:
                                self.color_to_search = 'green'
                                logger.info("Color search initiated for Green.")
                                print("Color search initiated for Green.")
                        elif event.code == "BTN_EAST" and event.state == 1:  # B button
                            with self._color_lock:
                                self.color_to_search = 'red'
                                logger.info("Color search initiated for Red.")
                                print("Color search initiated for Red.")
            except inputs.UnpluggedError:
                logger.warning("Controller disconnected. Waiting for reconnection...")
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                logger.error(f"Error polling controller: {e}")
                time.sleep(0.1)  # Brief pause before retrying

    def get_motion_paused(self):
        """
        Safely retrieve the current motion_paused state.
        """
        with self._lock:
            return self.motion_paused

    def get_color_to_search(self):
        """
        Safely retrieve the current color_to_search.
        Returns the color if set, otherwise None.
        """
        with self._color_lock:
            return self.color_to_search

    def clear_color_to_search(self):
        """
        Safely reset the current color_to_search.
        """
        with self._color_lock:
            self.color_to_search = None

    def set_motion_paused(self, state: bool):
        """
        Safely set the motion_paused state externally.
        """
        with self._lock:
            self.motion_paused = state
            if self.motion_paused:
                logger.info("Motion paused externally.")
                print("Motion paused externally.")
            else:
                logger.info("Motion resumed externally.")
                print("Motion resumed externally.")

    def wait_for_start_signal(self):
        """
        Wait until the user presses the 'Y' button to start.
        """
        logger.info("Waiting for 'Y' button press to start...")
        print("Press Y to start program")
        while not self._stop_event.is_set():
            with self._lock:
                if self.motion_paused:
                    self.motion_paused = False  # Reset for future toggles
                    logger.info("Y button pressed. Starting now...")
                    return
            time.sleep(0.01)  # Small delay to prevent high CPU usage

    def stop(self):
        """
        Stop the controller polling thread.
        """
        logger.info("Stopping controller polling thread...")
        self._stop_event.set()
        self._thread.join()
        logger.info("Controller polling thread stopped.")

# Create a singleton controller instance
_controller_instance = Controller()

def wait_for_start_signal():
    return _controller_instance.wait_for_start_signal()

def is_motion_paused():
    return _controller_instance.get_motion_paused()

def get_color_to_search():
    return _controller_instance.get_color_to_search()

def clear_color_to_search():
    _controller_instance.clear_color_to_search()

def set_motion_paused(state: bool):
    _controller_instance.set_motion_paused(state)

