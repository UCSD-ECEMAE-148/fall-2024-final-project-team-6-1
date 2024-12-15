# perform_line_following.py

import cv2
import depthai as dai
import numpy as np
import time
import logging
from logger_config import setup_logger

from crop_frame import crop_frame
from filter_yellow_line import filter_yellow_line
from detect_endpoint import detect_endpoint
from get_line_position import get_line_position
from calculate_steering_offset import calculate_steering_offset
from motions.U_Turn import execute_u_turn
import control_vals as cv
from controller_input import is_motion_paused, get_color_to_search, clear_color_to_search, set_motion_paused
from color_detection import detect_color_in_boxes, is_color_present_in_row
from motions.Left_Parking import execute_left_parking
from motions.Right_Parking import execute_right_parking
from motions.Left_Exit import execute_left_exit
from motions.Right_Exit import execute_right_exit

logger = setup_logger('LineFollowing', 'line_following.log')

# Define states for the robot
STATE_LINE_FOLLOWING = 0        # Normal operation, searching for color
STATE_COLOR_DETECTED = 1        # Color detected and resumed after pause, now monitoring disappearance
STATE_COLOR_DISAPPEARED = 2     # Color gone, paused indefinitely, waiting for Y press to do parking
STATE_PARKED = 3                # Finished parking, paused again, waiting for Y press to do exit

def perform_line_following(vesc, motion_data):
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(cv.CAMERA_RESOLUTION_WIDTH, cv.CAMERA_RESOLUTION_HEIGHT)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(cv.CAMERA_FPS)

    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    LINE_LOST_THRESHOLD = 3
    line_lost_frames = 0

    motion_paused = False
    following_line_logged = False

    color_detected = False
    in_pause = False
    pause_start_time = 0
    side_detected = None
    robot_state = STATE_LINE_FOLLOWING

    with dai.Device(pipeline) as device:
        logger.info("Connected to OAK-D Lite. Starting line-following with endpoint detection.")
        print("Connected to OAK-D Lite Device. Starting line-following")
        print("Select Y on remote to pause and resume motion")

        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            try:
                prev_motion_paused = motion_paused
                current_motion_paused = is_motion_paused()

                # Check if Y (motion_paused toggle) was pressed
                if current_motion_paused != motion_paused:
                    motion_paused = current_motion_paused
                    if prev_motion_paused == False and motion_paused == True:
                        # Just paused externally
                        logger.info("Motion paused externally.")
                        print("Motion paused externally.")
                        following_line_logged = False
                    elif prev_motion_paused == True and motion_paused == False:
                        # Just resumed externally (unpaused)
                        logger.info("Motion resumed externally.")
                        print("Motion resumed externally.")
                        # Handle state transitions on unpause
                        if robot_state == STATE_COLOR_DISAPPEARED:
                            # Unpausing from indefinite pause: run parking
                            print(f"Executing {side_detected} Parking...")
                            logger.info(f"Executing {side_detected} Parking...")
                            if side_detected == "Left":
                                execute_left_parking(vesc)
                            else:
                                execute_right_parking(vesc)
                            # After parking done, pause again for exit step
                            set_motion_paused(True)
                            robot_state = STATE_PARKED
                            print("Parking done, press Y again to execute exit.")
                            logger.info("Parking done, press Y again to execute exit.")
                        elif robot_state == STATE_PARKED:
                            # Unpausing from parked state: run exit
                            print(f"Executing {side_detected} Exit...")
                            logger.info(f"Executing {side_detected} Exit...")
                            if side_detected == "Left":
                                execute_left_exit(vesc)
                            else:
                                execute_right_exit(vesc)
                            # After exit done, clear color and resume line-following
                            clear_color_to_search()
                            side_detected = None
                            color_detected = False
                            robot_state = STATE_LINE_FOLLOWING
                            set_motion_paused(False)
                            print("Exit done, resuming normal line-following.")
                            logger.info("Exit done, resuming normal line-following.")

                # If motion_paused is True, just ensure robot is stopped and do nothing else
                if motion_paused:
                    vesc.set_servo(cv.STEERING_NEUTRAL)
                    vesc.set_rpm(0)
                    # Robot is paused, no line-following or color logic
                    time.sleep(0.01)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Received 'q' keypress. Exiting line-following loop.")
                        break
                    continue

                # If we are here, motion_paused is False, proceed with logic
                desired_color = get_color_to_search()
                color_search_active = (desired_color is not None)

                if color_search_active:
                    if robot_state == STATE_LINE_FOLLOWING and not color_detected and not in_pause:
                        # Try to detect color
                        detected_flag, side = detect_color_in_boxes(desired_color, device)
                        if detected_flag:
                            print(f"Detected {desired_color.capitalize()} spot on {side} side. Stopping motion.")
                            logger.info(f"Detected {desired_color.capitalize()} spot on {side} side. Stopping motion.")
                            vesc.set_servo(cv.STEERING_NEUTRAL)
                            vesc.set_rpm(0)
                            in_pause = True
                            pause_start_time = time.time()
                            side_detected = side

                    if in_pause and (time.time() - pause_start_time >= 2.5):
                        # Resume line-following after 2.5s pause
                        print("Resuming line-following after pause.")
                        logger.info("Resuming line-following after pause.")
                        vesc.set_servo(cv.STEERING_NEUTRAL)
                        vesc.set_rpm(cv.FORWARD_RPM_MIN)
                        in_pause = False
                        color_detected = True
                        robot_state = STATE_COLOR_DETECTED


                    if robot_state == STATE_COLOR_DETECTED and color_detected:
                        # Check if color still present
                        """
                         if not is_color_present_in_row(desired_color, device, row=1):
                            print(f"Color {desired_color.capitalize()} no longer present in top row. Pausing indefinitely.")
                            logger.info(f"Color {desired_color.capitalize()} no longer present in top row. Pausing indefinitely.")
                            vesc.set_servo(cv.STEERING_NEUTRAL)
                            vesc.set_rpm(0)
                            set_motion_paused(True)
                            robot_state = STATE_COLOR_DISAPPEARED
                        """
                        # Check if the color is only visible in the bottom row
                        color_in_top = is_color_present_in_row(desired_color, device, row=1)
                        color_in_bottom = is_color_present_in_row(desired_color, device, row=3)

                        # Stop when color is ONLY in bottom row (visible in bottom, not in top)
                        if color_in_bottom and not color_in_top:
                            print(f"Color {desired_color.capitalize()} now only visible in bottom row (row=3). Pausing indefinitely.")
                            logger.info(f"Color {desired_color.capitalize()} now only visible in bottom row (row=3). Pausing indefinitely.")
                            vesc.set_servo(cv.STEERING_NEUTRAL)
                            vesc.set_rpm(0)
                            set_motion_paused(True)
                            robot_state = STATE_COLOR_DISAPPEARED

                            # Parking and exit steps will occur on Y presses

                # Normal line-following if STATE_LINE_FOLLOWING or STATE_COLOR_DETECTED and not paused or in_pause
                if not in_pause and robot_state in [STATE_LINE_FOLLOWING, STATE_COLOR_DETECTED]:
                    in_frame = rgb_queue.get()
                    frame = in_frame.getCvFrame()
                    cropped_frame = crop_frame(frame, cv.LINES["horizontal_y_percent"])
                    yellow_mask = filter_yellow_line(cropped_frame)

                    # Check endpoint
                    if detect_endpoint(yellow_mask, cv.LINES, debug_frame=cropped_frame):
                        logger.info("🚨 Endpoint detected. Performing U-turn...")
                        print("Starting U-turn execution...")
                        execute_u_turn(vesc, motion_data)
                        print("U-turn completed.")
                        continue

                    cx = get_line_position(yellow_mask)
                    if cx is not None:
                        line_lost_frames = 0
                        offset = calculate_steering_offset(cx, cropped_frame.shape[1], cv.VERTICAL_CENTERLINE)
                        steering = cv.STEERING_NEUTRAL + offset * (cv.STEERING_RIGHT_MAX - cv.STEERING_NEUTRAL)
                        steering = np.clip(steering, cv.STEERING_LEFT_MAX, cv.STEERING_RIGHT_MAX)

                        if not following_line_logged:
                            logger.info("Following line.")
                            print("Following line")
                            following_line_logged = True
                        vesc.set_servo(steering)
                        vesc.set_rpm(cv.FORWARD_RPM_MIN)
                    else:
                        line_lost_frames += 1
                        logger.warning(f"Line lost. Consecutive lost frames: {line_lost_frames}")
                        if line_lost_frames > LINE_LOST_THRESHOLD:
                            logger.warning("Line lost beyond threshold. Stopping motor.")
                            print("Line lost beyond threshold. Stopping motor.")
                            vesc.set_servo(cv.STEERING_NEUTRAL)
                            vesc.set_rpm(0)
                        else:
                            logger.info("Line lost briefly. Reducing RPM to half speed.")
                            print("Line lost briefly. Reducing RPM to half speed.")
                            vesc.set_servo(cv.STEERING_NEUTRAL)
                            vesc.set_rpm(int(cv.FORWARD_RPM_MIN * 0.5))

                    if cv.DISPLAY_COLOR_MASK and color_search_active:
                        color_hsv = cv.HSV_VALUES.get(desired_color)
                        if color_hsv:
                            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                            lower = np.array([color_hsv["LOW_H"], color_hsv["LOW_S"], color_hsv["LOW_V"]])
                            upper = np.array([color_hsv["HIGH_H"], color_hsv["HIGH_S"], color_hsv["HIGH_V"]])
                            mask = cv2.inRange(hsv_frame, lower, upper)
                            cv2.imshow("Color Mask", mask)

                time.sleep(0.01)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Received 'q' keypress. Exiting line-following loop.")
                    break

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt detected. Shutting down line-following.")
                break
            except Exception as e:
                logger.error(f"Exception in line-following loop: {e}")
                break

