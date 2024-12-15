import csv
import time
from pyvesc import VESC
import os
import sys

# Add the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Import control_vals
import control_vals as cv

def connect_to_vesc(serial_port, baudrate, max_retries=5, retry_interval=2):
    """Connect to the VESC with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to VESC (Attempt {attempt + 1}/{max_retries})...")
            return VESC(serial_port=serial_port, baudrate=baudrate)
        except Exception as e:
            print(f"Failed to connect to VESC: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Max retries reached. Exiting program.")
                exit(1)


def load_u_turn_data(file_path):
    """Load Parking Training"""
    motion_data = []
    try:
        with open(file_path, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                timestamp, steering, rpm = float(row[0]), float(row[1]), float(row[2])
                motion_data.append((timestamp, steering, rpm))
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    return motion_data


def execute_u_turn(vesc, motion_data):
    """Execute the motion based on the trained data."""
    print("Starting Parking execution...")
    start_time = time.time()

    for i in range(len(motion_data) - 1):
        timestamp, steering, rpm = motion_data[i]
        next_timestamp, _, _ = motion_data[i + 1]

        # Ensure commands are within safe ranges
        steering = max(cv.STEERING_LEFT_MAX, min(cv.STEERING_RIGHT_MAX, steering))
        rpm = int(max(cv.REVERSE_RPM_MIN, min(cv.FORWARD_RPM_MAX, rpm)))

        # Send the steering and RPM commands to the VESC
        vesc.set_servo(steering)
        vesc.set_rpm(rpm)

        # Log values being sent
#        print(f"Sending to VESC -> Steering: {steering:.2f}, RPM: {rpm}")

        # Wait for the time difference between the current and next command
        time_to_wait = next_timestamp - timestamp
        if time_to_wait > 0:
            time.sleep(time_to_wait)

    # Stop the robot after executing the motion
    vesc.set_rpm(0)
    vesc.set_servo(cv.STEERING_NEUTRAL)
    print("Motion completed. Robot stopped.")


def main():
    # Replace with the correct serial port and baud rate for your setup
    serial_port = "/dev/ttyACM0"
    baudrate = 115200
    u_turn_file = "/home/jetson/projects/final_project/recordings/U_Turn.csv"  # Recorded motion file

    # Connect to the VESC
    vesc = connect_to_vesc(serial_port, baudrate)

    # Load the U-turn data
    motion_data = load_u_turn_data(u_turn_file)

    # Execute the U-turn
    execute_u_turn(vesc, motion_data)


if __name__ == "__main__":
    main()

