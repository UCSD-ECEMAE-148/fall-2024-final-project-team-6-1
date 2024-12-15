# vesc_record.py

import time
import csv
import argparse
import os
import sys

def monitor_and_record_vesc(motion_name, output_dir="/home/jetson/projects/final_project/recordings"):
    """
    Monitor and record VESC steering and RPM values for a specified motion.
    
    Args:
        motion_name (str): Name of the motion (e.g., "Right_Exit").
        output_dir (str): Directory where CSV files are stored.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the output CSV file path
    output_file = os.path.join(output_dir, f"{motion_name}.csv")
    
    # Delete the existing CSV file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"Existing file '{output_file}' removed.")
        except Exception as e:
            print(f"Error removing existing file '{output_file}': {e}")
            sys.exit(1)
    
    print(f"Recording {motion_name} motion to: {output_file}")
    print("Monitoring VESC steering and RPM. Press 'Ctrl+C' to stop.")
    
    # Open CSV file for recording
    try:
        with open(output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Steering", "RPM"])  # CSV header
    
            while True:
                try:
                    with open("/home/jetson/projects/final_project/vesc_values.txt", "r") as file:
                        data = file.read().strip()
                        if data:
                            steering, rpm = map(float, data.split(","))
                            timestamp = time.time()
                            print(f"Timestamp: {timestamp:.2f}, Steering: {steering:.2f}, RPM: {rpm}")
                            
                            # Write to CSV
                            writer.writerow([timestamp, steering, rpm])
                            csvfile.flush()  # Ensure data is saved immediately
                except FileNotFoundError:
                    print("Shared file 'vesc_values.txt' not found. Waiting for updates...")
                except ValueError:
                    print("Invalid data format in 'vesc_values.txt'. Expected 'steering,rpm'.")
                except Exception as e:
                    print(f"Error reading 'vesc_values.txt': {e}")
    
                time.sleep(0.05)  # Adjust polling rate as needed
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"Error opening CSV file '{output_file}': {e}")
    finally:
        print(f"Recording saved to {output_file}")

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Record VESC steering and RPM values for a specified motion.")
    parser.add_argument(
        "motion",
        type=str,
        choices=["Right_Parking", "Right_Exit", "Left_Parking", "Left_Exit", "U_Turn"],
        help="Name of the motion to record. Choices: Right_Parking, Right_Exit, Left_Parking, Left_Exit, U_Turn"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/home/jetson/projects/final_project/recordings",
        help="Directory to store CSV recordings. Default is 'recordings/'."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    monitor_and_record_vesc(args.motion, args.output_dir)

