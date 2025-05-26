#!/usr/bin/env python3
import time
import argparse
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig

def open_bus(port, ids, baud):
    motor_names = [f"id{i}" for i in ids]
    motors = {name: (idx, "sts3215") for name, idx in zip(motor_names, ids)}
    config = FeetechMotorsBusConfig(port=port, motors=motors)
    bus = FeetechMotorsBus(config)
    bus.connect()
    return bus, motor_names

def main():
    p = argparse.ArgumentParser(
        description="Read/write freq test: leader+follower arms"
    )
    p.add_argument("--port_leader", required=True,
                   help="Leader arm port, e.g. /dev/ttyUSB0")
    p.add_argument("--port_follower", required=True,
                   help="Follower arm port, e.g. /dev/ttyUSB1")
    p.add_argument("--ids", required=True,
                   help="Comma-separated servo IDs, e.g. 1,2,3")
    p.add_argument("--baud", type=int, default=1000000,
                   help="Bus speed in bps")
    p.add_argument("--increment", type=int, default=10,
                   help="Position increment per cycle")
    args = p.parse_args()

    ids = [int(x) for x in args.ids.split(',')]
    # Open both buses
    bus_leader, names = open_bus(args.port_leader, ids, args.baud)
    bus_follower, _     = open_bus(args.port_follower, ids, args.baud)

    last_read_time  = None
    last_write_time = None

    print(f"Reading IDs {ids} on LEADER({args.port_leader}) & FOLLOWER({args.port_follower})")
    print(" Time     |  L_pos...    F_pos...    ReadHz   WriteHz")
    print("-"*70)

    try:
        while True:
            # --- READ both arms ---
            t_read = time.time()
            poses_leader   = bus_leader.read("Present_Position", names)
            poses_follower = bus_follower.read("Present_Position", names)
            if last_read_time is None:
                read_hz = 0.0
            else:
                dt_read = t_read - last_read_time
                read_hz = 1.0 / dt_read if dt_read>0 else float('inf')
            last_read_time = t_read

            # --- WRITE to leader only ---
            # simple incr target = current + increment
            targets = [p + args.increment for p in poses_leader]
            t_write = time.time()
            print(f"Writing targets: {targets}")
            print(f"names: {names}")
            bus_leader.write("Goal_Position", targets , names)
            if last_write_time is None:
                write_hz = 0.0
            else:
                dt_write = t_write - last_write_time
                write_hz = 1.0 / dt_write if dt_write>0 else float('inf')
            last_write_time = t_write

            # --- print status ---
            ts = time.strftime("%H:%M:%S", time.localtime(t_read))
            Lpos = " ".join(f"{p:5d}" for p in poses_leader)
            Fpos = " ".join(f"{p:5d}" for p in poses_follower)
            print(f"{ts} | L[{Lpos}]  F[{Fpos}]  {read_hz:6.1f}Hz  {write_hz:6.1f}Hz")

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        bus_leader.disconnect()
        bus_follower.disconnect()

if __name__ == "__main__":
    main()
