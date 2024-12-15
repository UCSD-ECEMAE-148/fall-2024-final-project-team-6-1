# MAE 148 Fall 2024 Team 6 Final Project

## Table of Contents
- [Team Members](#team-members)
- [Overview](#overview)
- [Software](#software)
- [Hardware](#hardware)
- [Assembled Robot](#assembled-robot)
- [Final Project Demo](#final-project-demo)
- [Results](#results)
- [Program Structure](#program-structure)
- [File Descriptions](#file-descriptions)
- [How to Run the Program](#how-to-run-the-program)

---

## Team Members
- **Clayton Hoxworth** (MAE)  
- **Daniel Cruz** (ECE)  
- **Jonathan Cohen** (MAE)  
- **Lucca Frey** (MAE)  

---

## Overview
We want to create a **self-parking robot** that:  
1. **Follows a centerline** road path (using a specific color).  
2. With one input, can park in **3 different desired parking spots**.  
3. Continues traveling back and forth along the centerline until this input is given.  

The robot also performs **U-turns** at the ends of the centerline to remain on the path.

---

## Software
- **OpenCV**: Used to recognize lines while driving and detect specific colored parking spots.  
- **Custom Motion Control**: Predefined motions for entering and exiting parking spots.  
- **VESC**: Used to control RPM (speed) and servo values for precise movements.  

We trained parking maneuver motions to both **enter and exit** the parking spot. RPM and Servo values were tracked and normalized to ensure consistency.  

---

## Hardware
We used **Fusion360** to create CAD models to mount the robot's required electronics.  
The robot includes:  
- OAK-D Lite camera for video input and line detection.  
- VESC motor controller for movement.  
- Custom-designed mounts for electronics and sensors.  

---

## Assembled Robot
*(Add an image of the assembled robot here, if available.)*

---

## Final Project Demo
*(Add a link to a video demo or a description here.)*

---

## Results
The robot was able to:
- Successfully **travel back and forth** along the centerline.
- Perform **U-turns** at the ends of the line.
- Correctly **identify each parking spot** using color detection and perform parking maneuvers.

### Known Issues:
- The robot did not consistently fully enter the parking spots.
- The U-turn radius was slightly larger than desired.

---

## Program Structure
The program is modular and consists of:
1. **Main Script**:  
   - `parallel_park.py` – the primary entry point that runs the robot program.  
2. **Line Following**:  
   - `perform_line_following.py` – controls line following and integrates parking logic.  
3. **Color Detection**:  
   - `color_detection.py` – detects colored markers in specific regions of the camera frame.  
4. **Maneuver Scripts**:  
   - Found in the **motions/** directory (e.g., parking, U-turns).  
5. **Utilities**:  
   - Scripts for steering calculations, cropping frames, logging, and other helper functions.  

---

## File Descriptions

### Main Script
- **`parallel_park.py`**  
   The entry point for the program. It:  
   - Initializes the camera input.  
   - Starts the line-following process.  
   - Integrates color detection to trigger parking or maneuver actions.

---

### Core Scripts
- **`perform_line_following.py`**  
   - Handles the **line-following logic** by processing the camera feed and controlling robot steering.  
   - Detects colors using `color_detection.py` to determine when to pause or perform parking maneuvers.  
   - Executes motion scripts (e.g., U-turns, parking) when triggered.  

- **`color_detection.py`**  
   - Detects colors in specific regions (top, middle, and bottom rows) of the camera frame.  
   - Key functions:  
     - `detect_color_in_boxes`: Checks for color in specific grid regions.  
     - `is_color_present_in_row`: Determines if a color exists in a specific row.

- **`calculate_steering_offset.py`**  
   - Computes the steering offset based on the position of the detected line relative to the center of the frame.

- **`get_line_position.py`**  
   - Extracts the horizontal position of the detected line for steering adjustments.

- **`filter_yellow_line.py`**  
   - Filters yellow lines from the camera feed using HSV thresholds.

- **`crop_frame.py`**  
   - Crops the camera input to focus on relevant regions for line detection.

- **`detect_endpoint.py`**  
   - Detects endpoints in the line and triggers U-turn execution.

---

### Motions Directory
The **motions/** directory contains scripts for specific robot behaviors:
- **`U_Turn.py`**: Executes a U-turn when an endpoint is detected.  
- **`Left_Parking.py`** and **`Right_Parking.py`**: Handles left and right parking maneuvers.  
- **`Left_Exit.py`** and **`Right_Exit.py`**: Manages exiting maneuvers after parking.  

---

### Utilities and Configuration
- **`control_vals.py`**  
   Stores control constants for:  
   - Steering offsets  
   - RPM values  
   - Thresholds for detection logic.

- **`logger_config.py`**  
   Configures logging for debugging and program execution tracking.

- **`initialize_vesc.py`**  
   Initializes and configures the **VESC motor controller**.

---

### Testing and Adjustments
- **`test_color_detection.py`**  
   A testing script to validate color detection logic. It displays debug windows for:
   - Regions where color is detected.  
   - Adjustments to grid positions.

- **`adjust_centerline.py`**, **`adjust_spot_bars.py`**, and **`adjust_yellow_line_crop.py`**  
   Scripts to fine-tune:
   - Line detection accuracy.  
   - Grid positioning for color detection.

- **`filter_adj_test.py`** and **`filter_yellow_test.py`**  
   Scripts to test and adjust HSV thresholds for line and color detection.

---

### Logs and Outputs
- **Logs**:  
   - `line_following.log`: Logs details during line-following execution.  
   - `main.log`: General execution log.  
   - `test_color_detection.log`: Logs for testing color detection logic.  

- **Recordings**:  
   The **recordings/** directory stores outputs such as snapshots or test video recordings.

---

## How to Run the Program

1. Ensure all dependencies are installed:
   ```bash
   pip3 install depthai opencv-python numpy
