import time
import inputs
from pyvesc import VESC
import control_vals as cv  # Import values from control_vals.py


def normalize(value, min_raw, max_raw, min_norm, max_norm):
    """Normalize raw input values to the desired range."""
    return (value - min_raw) / (max_raw - min_raw) * (max_norm - min_norm) + min_norm


def scale_within_range(value, min_val, max_val):
    """Scale a normalized value (0 to 1) within a specified range."""
    return value * (max_val - min_val) + min_val


def clamp(value, min_val, max_val):
    """Clamp a value to a specified range."""
    return max(min(value, max_val), min_val)


def connect_to_vesc(serial_port, baudrate, max_retries=5, retry_interval=2):
    """Attempt to connect to the VESC with retry logic."""
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


def log_values(servo_position, motor_rpm):
    """Log steering and RPM values to a shared file."""
    try:
        with open("vesc_values.txt", "w") as file:
            file.write(f"{servo_position},{motor_rpm}")
    except Exception as e:
        print(f"Failed to log values: {e}")


def main():
    # Replace with the correct serial port and baud rate for your setup.
    serial_port = "/dev/ttyACM0"
    baudrate = 115200

    # Attempt to connect to the VESC
    vesc = connect_to_vesc(serial_port, baudrate)
    print("Connected to VESC successfully!")

    print("Use the left thumbstick to control steering and RT/LT to control motor.")
    print(f"RT -> Forward direction ({cv.FORWARD_RPM_MIN} to {cv.FORWARD_RPM_MAX} RPM), "
          f"LT -> Reverse direction ({cv.REVERSE_RPM_MIN} to {cv.REVERSE_RPM_MAX} RPM).")
    print(f"Steering range: {cv.STEERING_LEFT_MAX} (left) to {cv.STEERING_RIGHT_MAX} (right), neutral at {cv.STEERING_NEUTRAL}.")
    print("Both RT and LT -> No throttle (0 RPM).")

    try:
        rt_pressed = 0.0  # Value for RT trigger
        lt_pressed = 0.0  # Value for LT trigger
        thumbstick_value = 0.0  # Value for the left thumbstick
        servo_position = cv.STEERING_NEUTRAL  # Initialize servo position to neutral
        last_input_time = time.time()  # Track the time of the last valid input

        while True:
            # Read gamepad inputs
            try:
                events = inputs.get_gamepad()
                for event in events:
                    print(f"Event detected: {event.code}, Value: {event.state}")
                    last_input_time = time.time()  # Reset the input timeout

                    # Left Thumbstick Horizontal Axis for Steering
                    if event.ev_type == "Absolute" and event.code == "ABS_X":
                        raw_thumbstick = event.state  # Read the raw thumbstick value
                        thumbstick_value = normalize(raw_thumbstick, -32768, 32767, -1, 1)

                        # Map to servo position range
                        servo_position = normalize(thumbstick_value, -1, 1, cv.STEERING_LEFT_MAX, cv.STEERING_RIGHT_MAX)
                        servo_position = clamp(servo_position, cv.STEERING_LEFT_MAX, cv.STEERING_RIGHT_MAX)

                        vesc.set_servo(servo_position)  # Send steering command to VESC
                        print(f"Sent steering command: {servo_position}")

                    # Right Trigger (RT) for Forward Motion
                    elif event.ev_type == "Absolute" and event.code == "ABS_RZ":
                        rt_pressed = normalize(event.state, 0, 255, 0, 1)  # Normalize RT to 0-1

                    # Left Trigger (LT) for Reverse Motion
                    elif event.ev_type == "Absolute" and event.code == "ABS_Z":
                        lt_pressed = normalize(event.state, 0, 255, 0, 1)

            except inputs.UnpluggedError:
                print("Controller disconnected.")

            # Check for safety timeout
            if time.time() - last_input_time > cv.SAFETY_TIMEOUT:
                rt_pressed = 0.0
                lt_pressed = 0.0

            # Determine motor RPM based on RT and LT triggers
            if rt_pressed > 0 and lt_pressed > 0:
                motor_rpm = 0  # No throttle if both triggers are pressed
            elif rt_pressed > 0:
                motor_rpm = 2700  # Forward RPM
            elif lt_pressed > 0:
                motor_rpm = -2200  # Reverse RPM
            else:
                motor_rpm = 0  # Default to 0 RPM

            vesc.set_rpm(int(motor_rpm))  # Send RPM command to VESC
            print(f"Sent RPM command: {motor_rpm}")

            # Log the current values to the shared file
            log_values(servo_position, motor_rpm)

    except KeyboardInterrupt:
        print("\nShutting down.")
        vesc.set_rpm(0)  # Stop the motor
        vesc.set_servo(cv.STEERING_NEUTRAL)  # Reset steering to neutral
    finally:
        if hasattr(vesc, 'serial') and vesc.serial:
            vesc.serial.close()

if __name__ == "__main__":
    main()

