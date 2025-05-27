#!/usr/bin/env python3

import time
import sys
import traceback
from pathlib import Path
import scservo_sdk as scs

import ipdb
# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus, FeetechMotorsBusConfig
from lerobot.common.robot_devices.utils import RobotDeviceNotConnectedError

def test_motor_feedback(port: str, motor_name: str, motor_id: int, motor_model: str):
    """
    Test if we can get feedback from a Feetech motor without hitting timeout.
    
    Args:
        port: Serial port for the motor bus
        motor_name: Name of the motor to test
        motor_id: ID of the motor to test
        motor_model: Model of the motor (e.g. 'sts3215')
    """
    print(f"\nTesting motor feedback on port {port}")
    print(f"Motor: {motor_name} (ID: {motor_id}, Model: {motor_model})")
    
    # Create motor bus configuration
    config = FeetechMotorsBusConfig(
        port=port,
        motors={motor_name: (motor_id, motor_model)},
    )
    
    motors_bus = None
    try:
        # Initialize and connect to motor bus
        motors_bus = FeetechMotorsBus(config)
        print("Connecting to motor bus...")
        motors_bus.connect()
        print("setting baud rate ")
        motors_bus.set_bus_baudrate(115200)
        
        # Test reading position multiple times
        num_tests = 10
        print(f"\nRunning {num_tests} position read tests...")
        # Example usage:
        motors_bus = FeetechMotorsBus(config)
        motors_bus.connect()

        # When reading from motors
        try:
            # ipdb.set_trace
            comm_result = motors_bus.read("Present_Position")
            # ipdb.set_trace()
            print(comm_result)
            # if comm_result != scs.COMM_SUCCESS:
            #     error_message = motors_bus.get_comm_result(comm_result)
            #     print(f"Communication error: {error_message}")
        except Exception as e:
            print(f"Error: {e}")

        # When handling packet errors
        # try:
        #     # Some operation that might return an error
        #     error_code = some_operation()
        #     if error_code != 0:
        #         error_message = motors_bus.get_rx_packet_error(error_code)
        #         print(f"Packet error: {error_message}")
        # except Exception as e:
        #     print(f"Error: {e}")

        # for i in range(num_tests):
        #     try:
        #         # Read current position
        #         position = motors_bus.read("Present_Position", motor_name)
        #         print(f"Test {i+1}/{num_tests}: Successfully read position: {position}")
                
        #         # Small delay between reads
        #         time.sleep(0.1)
                
        #     except Exception as e:
        #         print(f"Test {i+1}/{num_tests}: Error reading position: {str(e)}")
        #         if "COMM_RX_TIMEOUT" in str(e):
        #             print("WARNING: Received timeout error - motor may not be responding properly")
        #         traceback.print_exc()
                
    except Exception as e:
        print(f"Error during test: {str(e)}")
        traceback.print_exc()
        
    finally:
        # Cleanup
        if motors_bus is not None and motors_bus.is_connected:
            print("\nDisconnecting from motor bus...")
            motors_bus.disconnect()

def main():
    # Example usage - replace these values with your actual motor configuration
    PORT = "/dev/ttyUSB0"  # Replace with your actual port
    MOTOR_NAME = "Present_position"
    MOTOR_ID = [1,2,3,4,5,6]
    MOTOR_MODEL = "sts3215"
    for i in range(6):
        test_motor_feedback(PORT, MOTOR_NAME, MOTOR_ID[i], MOTOR_MODEL) 
    

if __name__ == "__main__":
    main()