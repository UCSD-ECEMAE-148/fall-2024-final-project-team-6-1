# parallel_park.py

import logging
from logger_config import setup_logger

from initialize_vesc import initialize_vesc
from motions.U_Turn import load_u_turn_data
from controller_input import wait_for_start_signal, is_motion_paused, get_color_to_search, set_motion_paused
from perform_line_following import perform_line_following

# Setup logger for main script
logger = setup_logger('Main', 'main.log')

def main():
    serial_port = "/dev/ttyACM0"  # Update with your VESC's serial port
    baudrate = 115200
    u_turn_file = "/home/jetson/projects/final_project/recordings/U_Turn.csv"  # U-turn motion data file

    try:
        # Wait for the Y button to be pressed before starting
        wait_for_start_signal()

        logger.info("Initializing VESC...")
        print("Initializing VESC")
        # Initialize the VESC
        vesc = initialize_vesc(serial_port, baudrate)
        logger.info("VESC initialized successfully.")
        print("VESC initialized successfully on attempt 1.")

        print("Connected to OAK-D Lite Device. Starting line-following")
        print("Select Y on remote to pause and resume motion")

        # Load U-turn motion data
        logger.info("Loading U-turn motion data...")
        motion_data = load_u_turn_data(u_turn_file)
        logger.info("U-turn motion data loaded.")

        # Perform line following with U-turn detection and motion control
        logger.info("Starting line-following routine.")
        perform_line_following(vesc, motion_data)

    except KeyboardInterrupt:
        print("\nStopped and reset vehicle")
        logger.info("KeyboardInterrupt detected. Shutting down.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
    finally:
        # Ensure controller polling thread is stopped
        from controller_input import _controller_instance
        _controller_instance.stop()
        logger.info("Controller polling thread stopped.")

if __name__ == "__main__":
    main()

