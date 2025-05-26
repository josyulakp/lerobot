import time
import sys

from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig

# ---- USER CONFIG ----
PORT = "/dev/ttyUSB0"  # Change as needed
MOTOR_NAMES = ["arm1", "arm2", "arm3", "arm4", "arm5", "arm6"]  # Change as needed
MOTOR_IDS = [1, 2, 3, 4, 5, 7]  # Change as needed
MOTOR_MODELS = ["sts3215"] * len(MOTOR_IDS)  # Change as needed

def main():
    # Setup config and bus
    config = FeetechMotorsBusConfig(
        port=PORT,
        motors={name: (idx, model) for name, idx, model in zip(MOTOR_NAMES, MOTOR_IDS, MOTOR_MODELS)},
    )
    bus = FeetechMotorsBus(config)
    print("Connecting to bus...")
    bus.connect()

    poses = []
    for i in range(2):
        input(f"\nMove arms to desired pose {i+1} and press ENTER to capture...")
        # pos = []
        # for name, motor_id in zip(MOTOR_NAMES, MOTOR_IDS):
        #     pos_val, res, _ = bus.packet_handler.read2ByteTxRx(motor_id, 57)
        #     print(f"Motor {name} (ID {motor_id}) position: {pos_val}")
        #     print(f"Motor {name} (ID {motor_id}) error: {res}") 
        #     if res != 0:
        #         print(f"Error reading motor {name} (ID {motor_id}): {res}")
        #         sys.exit(1)
        #     pos.append(pos_val)
        pos = bus.read("Present_Position", MOTOR_NAMES)
        print(f"Captured pose {i+1}: {pos}")
        poses.append(pos)
        time.sleep(0.2)

    print("\nReady to write poses synchronously.")
    print("Press ENTER to write pose 1, ENTER again to write pose 2, Ctrl+C to exit.")

    try:
        while True:
            for idx, pose in enumerate(poses):
                input(f"\nPress ENTER to write pose {idx+1}...")
                t0 = time.perf_counter()
                bus.write("Goal_Position", pose, MOTOR_NAMES)
                t1 = time.perf_counter()
                print(f"Pose {idx+1} written in {(t1-t0)*1000:.2f} ms")
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        bus.disconnect()

if __name__ == "__main__":
    # from STservo_sdk import *

    # # 1) Open port and handler
    # ph = PortHandler("/dev/ttyUSB0")
    # if not ph.openPort():
    #     raise RuntimeError("Cannot open serial port")
    # pp = protocol_packet_handler(ph, protocol_end=0)

    # for sid in [1, 2, 3, 4, 5, 6]:
    #     # A) Clear any existing error by reading a status register
    #     _, _, err = pp.read1ByteTxRx(sid, STS_MODE)
    #     if err & ERRBIT_OVERHEAT:
    #         print(f"⚠️ Servo {sid} overheating flagged; ensure cool-down before writes")

    #     # B) Unlock EEPROM for writes
    #     res, err = pp.write1ByteTxRx(sid, STS_LOCK, 0)
    #     if res != COMM_SUCCESS:
    #         print(f"Servo {sid}: failed to unlock EEPROM (err={err})")

    #     # C) Set Mode = 0 (absolute-position)
    #     res, err = pp.write1ByteTxRx(sid, STS_MODE, 0)
    #     print(f"Servo {sid}: set MODE→0 (res={res}, err={err})")

    #     # D) Zero the multi-turn offset: write low and high bytes = 0
    #     res_l, err_l = pp.write1ByteTxRx(sid, STS_OFS_L, 0)
    #     res_h, err_h = pp.write1ByteTxRx(sid, STS_OFS_H, 0)
    #     print(f"Servo {sid}: offset low write (res={res_l}, err={err_l}); "
    #         f"high write (res={res_h}, err={err_h})")

    #     # E) Lock EEPROM back
    #     res, err = pp.write1ByteTxRx(sid, STS_LOCK, 1)
    #     print(f"Servo {sid}: EEPROM locked (res={res}, err={err})")

    # ph.closePort()


    main()