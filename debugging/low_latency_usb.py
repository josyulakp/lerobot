import os, fcntl, array
import sys

# Ioctl constants from <linux/serial.h>
TIOCGSERIAL       = 0x541E
TIOCSSERIAL       = 0x541F
ASYNC_LOW_LATENCY = 0x2000  # the low-latency flag

def check_and_set_low_latency(port="/dev/ttyUSB0"):
    # 1. Open the port
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    buf = array.array('i', [0]*7)   # struct serial_struct (7 ints)
    # 2. Get current settings
    fcntl.ioctl(fd, TIOCGSERIAL, buf, True)
    flags = buf[4]
    is_low = bool(flags & ASYNC_LOW_LATENCY)
    print(f"Before: Low-latency = {is_low}")
    # 3. Try to set the flag if not already set
    if not is_low:
        buf[4] = flags | ASYNC_LOW_LATENCY
        if fcntl.ioctl(fd, TIOCSSERIAL, buf) < 0:
            print("Failed to apply ASYNC_LOW_LATENCY")
        else:
            print("Applied ASYNC_LOW_LATENCY via ioctl")
        # Re-fetch to confirm
        fcntl.ioctl(fd, TIOCGSERIAL, buf, True)
        is_low = bool(buf[4] & ASYNC_LOW_LATENCY)
        print(f"After: Low-latency = {is_low}")
    os.close(fd)

if __name__ == "__main__":
    # Usage: python low_latency_usb.py [port]
    # Example: python low_latency_usb.py /dev/ttyUSB1
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    check_and_set_low_latency(port=port)
    