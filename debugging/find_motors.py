import argparse
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus, SCS_SERIES_BAUDRATE_TABLE
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Scan for Feetech motors on all baudrates and IDs.")
    parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/ttyUSB0")
    parser.add_argument("--min_id", type=int, default=1, help="Minimum ID to scan (default: 1)")
    parser.add_argument("--max_id", type=int, default=20, help="Maximum ID to scan (default: 20)")
    args = parser.parse_args()

    ids = list(range(args.min_id, args.max_id + 1))
    # Use a dummy config, will update baudrate in loop
    motors = {f"id{sid}": (sid, "sts3215") for sid in ids}
    config = FeetechMotorsBusConfig(port=args.port, motors=motors)
    bus = FeetechMotorsBus(config)

    found = []
    print(f"Scanning port {args.port} for IDs {ids} on all supported baudrates...")
    try:
        bus.connect()
        for baud in SCS_SERIES_BAUDRATE_TABLE.values():
            try:
                bus.set_bus_baudrate(baud)
                print(f"\nTrying baudrate: {baud}")
                present_ids = []
                for sid in tqdm(ids):
                    try:
                        # Try to read the ID register for this ID
                        val = bus.read("ID", f"id{sid}")
                        if val[0] == sid:
                            present_ids.append(sid)
                    except Exception:
                        continue
                if present_ids:
                    print(f"Found motors at baudrate {baud}: IDs {present_ids}")
                    found.extend([(baud, sid) for sid in present_ids])
                else:
                    print("No motors found at this baudrate.")
            except Exception as e:
                print(f"Error at baudrate {baud}: {e}")
    finally:
        bus.disconnect()
        print("\nScan complete.")
        if found:
            print("Summary of found motors:")
            for baud, sid in found:
                print(f"  ID {sid} at baudrate {baud}")
        else:
            print("No motors found.")

if __name__ == "__main__":
    main()
