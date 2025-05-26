import time
import logging
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig
from tabulate import tabulate
import argparse

# data_name: (address, size_byte)
SCS_SERIES_CONTROL_TABLE = {
    "Model": (3, 2),
    "ID": (5, 1),
    "Baud_Rate": (6, 1),
    "Return_Delay": (7, 1),
    "Response_Status_Level": (8, 1),
    "Min_Angle_Limit": (9, 2),
    "Max_Angle_Limit": (11, 2),
    "Max_Temperature_Limit": (13, 1),
    "Max_Voltage_Limit": (14, 1),
    "Min_Voltage_Limit": (15, 1),
    "Max_Torque_Limit": (16, 2),
    "Phase": (18, 1),
    "Unloading_Condition": (19, 1),
    "LED_Alarm_Condition": (20, 1),
    "P_Coefficient": (21, 1),
    "D_Coefficient": (22, 1),
    "I_Coefficient": (23, 1),
    "Minimum_Startup_Force": (24, 2),
    "CW_Dead_Zone": (26, 1),
    "CCW_Dead_Zone": (27, 1),
    "Protection_Current": (28, 2),
    "Angular_Resolution": (30, 1),
    "Offset": (31, 2),
    "Mode": (33, 1),
    "Protective_Torque": (34, 1),
    "Protection_Time": (35, 1),
    "Overload_Torque": (36, 1),
    "Speed_closed_loop_P_proportional_coefficient": (37, 1),
    "Over_Current_Protection_Time": (38, 1),
    "Velocity_closed_loop_I_integral_coefficient": (39, 1),
    "Torque_Enable": (40, 1),
    "Acceleration": (41, 1),
    "Goal_Position": (42, 2),
    "Goal_Time": (44, 2),
    "Goal_Speed": (46, 2),
    "Torque_Limit": (48, 2),
    "Lock": (55, 1),
    "Present_Position": (56, 2),
    "Present_Speed": (58, 2),
    "Present_Load": (60, 2),
    "Present_Voltage": (62, 1),
    "Present_Temperature": (63, 1),
    "Status": (65, 1),
    "Moving": (66, 1),
    "Present_Current": (69, 2),
    # Not in the Memory Table
    "Maximum_Acceleration": (85, 2),
}



def read_whole_memory(bus, servo_id):
    """
    Read the entire memory of a servo motor.

    Args:
        bus: The bus object to communicate with the servo.
        servo_id: The ID of the servo motor.

    Returns:
        A dictionary containing the memory addresses and their values.
    """
    memory = {}
    for name, (address, size) in SCS_SERIES_CONTROL_TABLE.items():
        try:
            # print(f"Calling bus.read({name!r}, {servo_id})")  # Debug: show args
            value_arr = bus.read(name, f"id{servo_id}")
            # print(f"Result from bus.read: {value_arr}")         # Debug: show result
            value = value_arr[0]
            memory[name] = value
        except Exception as e:
            logging.error(f"Failed to read {name} from servo {servo_id}: {e}")
            memory[name] = None  # Store None if read fails
    return memory

def main():
    # Set your port and motor configuration here
    parser = argparse.ArgumentParser(description="Read whole memory of Feetech servos.")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--ids", type=int, nargs="+", default=[1,2,3,4,5,6,7], help="Servo IDs (default: 1 2 3 4 5 6 7)")
    args = parser.parse_args()

    port = args.port
    ids = args.ids

    # Build the motors dictionary: name -> (id, model)
    motors = {f"id{sid}": (sid, "sts3215") for sid in ids}
    config = FeetechMotorsBusConfig(port=port, motors=motors)
    bus = FeetechMotorsBus(config)
    bus.connect()
    try:
        for servo_id in ids:
            memory = read_whole_memory(bus, servo_id)
            print(f"\nMemory for Servo ID {servo_id}:")
            table = [(name, value) for name, value in memory.items()]
            print(tabulate(table, headers=["Name", "Value"], tablefmt="fancy_grid"))
            print("-" * 40)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        bus.disconnect()

if __name__ == "__main__":
    main()