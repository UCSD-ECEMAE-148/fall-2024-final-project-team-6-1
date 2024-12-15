import time
from pyvesc import VESC

def initialize_vesc(serial_port, baudrate, max_retries=5):
    """Initialize the VESC with retry logic."""
    print("Connecting to Vesc")
    for attempt in range(max_retries):
        try:
            vesc = VESC(serial_port=serial_port, baudrate=baudrate)
            print(f"VESC initialized successfully on attempt {attempt + 1}.")
            return vesc
        except ValueError as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in 2 seconds...")
            time.sleep(2)
    raise RuntimeError("Failed to initialize VESC after multiple attempts.")

