import argparse
import logging
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus, SCS_SERIES_CONTROL_TABLE
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig
import time

def parse_id_list(id_str):
    return [int(x.strip()) for x in id_str.split(",") if x.strip()]

def main():
    parser = argparse.ArgumentParser(description="Write a value to a Feetech servo memory entry.")
    parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/ttyUSB0")
    parser.add_argument("--id", required=True, help="Comma-separated list of Servo IDs")
    parser.add_argument("--name", required=True, help="Name in control table (e.g. Goal_Position)")
    parser.add_argument("--value", type=int, required=True, help="Value to write")
    parser.add_argument("--model", default="sts3215", help="Servo model (default: sts3215)")
    args = parser.parse_args()

    id_list = parse_id_list(args.id)
    motors = {f"id{sid}": (sid, args.model) for sid in id_list}
    config = FeetechMotorsBusConfig(port=args.port, motors=motors)
    bus = FeetechMotorsBus(config)
    bus.connect()
    try:
        if args.name not in SCS_SERIES_CONTROL_TABLE:
            raise ValueError(f"{args.name} not in control table.")
        for sid in id_list:
            servo_name = f"id{sid}"
            prev_value = bus.read(args.name, servo_name)
            print(f"Previous value of {args.name} for servo {servo_name}: {prev_value}")
            print(f"Writing {args.value} to {args.name} for servo {servo_name} on port {args.port}")
            bus.write(args.name, args.value, servo_name)
            time.sleep(0.1)
            present_value = bus.read(args.name, servo_name)
            print(f"Present value of {args.name} for servo {servo_name}: {present_value}")
        print("Write successful.")
    except Exception as e:
        logging.error(f"Failed to write: {e}")
    finally:
        bus.disconnect()

if __name__ == "__main__":
    main()
