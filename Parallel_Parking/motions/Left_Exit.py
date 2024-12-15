# motions/Left_Parking.py

import csv
import time
import os
import sys
import logging
from pyvesc import VESC
import control_vals as cv

logger = logging.getLogger('LeftExit')

def load_parking_data(file_path):
    motion_data = []
    with open(file_path, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header if any
        for row in reader:
            if len(row) < 3:
                continue
            timestamp, steering, rpm = float(row[0]), float(row[1]), float(row[2])
            motion_data.append((timestamp, steering, rpm))
    logger.info(f"Loaded {len(motion_data)} Left Parking motion commands from {file_path}.")
    return motion_data

def execute_left_exit(vesc, parking_file="/home/jetson/projects/final_project/recordings/Left_Exit.csv"):
    logger.info("Starting Left Exit execution...")
    print("Starting Left Exit execution...")

    motion_data = load_parking_data(parking_file)
    start_time = time.time()

    for i in range(len(motion_data)-1):
        timestamp, steering, rpm = motion_data[i]
        next_timestamp, _, _ = motion_data[i+1]

        # Clamp steering and rpm to safe ranges
        steering = max(cv.STEERING_LEFT_MAX, min(cv.STEERING_RIGHT_MAX, steering))
        rpm = int(max(cv.REVERSE_RPM_MIN, min(cv.FORWARD_RPM_MAX, rpm)))

        vesc.set_servo(steering)
        vesc.set_rpm(rpm)

        logger.debug(f"Left Exit -> Steering: {steering:.2f}, RPM: {rpm}")
        time_to_wait = next_timestamp - timestamp
        if time_to_wait > 0:
            time.sleep(time_to_wait)

    vesc.set_rpm(0)
    vesc.set_servo(cv.STEERING_NEUTRAL)
    print("Left Exit Motion completed. Robot stopped.")
    logger.info("Left Exit Motion completed. Robot stopped.")

