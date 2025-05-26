#!/usr/bin/env python3
import os
import pty
import sys
import threading
import serial
import binascii
import time
from datetime import datetime

# CONFIGURATION
REAL_PORT   = '/dev/ttyUSB0'
BAUDRATE    = 115200
LOG_FILE    = None         # e.g. 'port_sniffer.log' or None for stdout
READ_CHUNK  = 1024         # bytes to read per os.read()
MAX_BAR     = 50           # max width of the spike bar
# the delta (in seconds) that maps to MAX_BAR; adjust if you expect >100ms gaps
BAR_SCALE_S = 0.1          

def timestamp():
    return datetime.now().strftime('%H:%M:%S.%f')[:-3]

def relay(src_fd, dst_fd, label):
    """Read from src_fd, write to dst_fd, and log with spike bars."""
    last_time = time.time()
    while True:
        try:
            data = os.read(src_fd, READ_CHUNK)
            if not data:
                time.sleep(0.001)
                continue

            now = time.time()
            delta = now - last_time
            last_time = now

            # forward the data
            os.write(dst_fd, data)

            # build the spike bar
            bar_len = min(int((delta / BAR_SCALE_S) * MAX_BAR), MAX_BAR)
            bar = '█' * bar_len

            # hex-encode the data chunk
            hexstr = binascii.hexlify(data).decode('ascii')
            entry = f"[{timestamp()}] {label} +{delta*1000:6.2f} ms {bar} {hexstr}"
            
            # print and optionally log
            print(entry)
            if LOG_FILE:
                with open(LOG_FILE, 'a') as f:
                    f.write(entry + "\n")
        except OSError:
            break

def main():
    # 1) Create a virtual PTY pair
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)
    print(f"[INFO] Virtual port created: {slave_name}")

    # 2) Open the real USB port
    real = serial.Serial(REAL_PORT, BAUDRATE, timeout=0)  # non-blocking reads

    print(f"[INFO] Forwarding {REAL_PORT} ↔ {slave_name}")
    print(f"[INFO] Spike bar scale: {BAR_SCALE_S*1000:.0f} ms → {MAX_BAR} chars")
    if LOG_FILE:
        print(f"[INFO] Logging to {LOG_FILE}")
    else:
        print("[INFO] Logging to stdout")

    # 3) Start relay threads for both directions
    t_rx = threading.Thread(
        target=relay,
        args=(real.fileno(), master_fd, 'RX:')
    )
    t_tx = threading.Thread(
        target=relay,
        args=(master_fd, real.fileno(), 'TX:')
    )
    t_rx.daemon = t_tx.daemon = True
    t_rx.start()
    t_tx.start()

    # 4) Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping sniffer.")
    finally:
        real.close()

if __name__ == "__main__":
    main()
