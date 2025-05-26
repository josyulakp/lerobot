# import serial
# for rate in [115200, 230400, 460800, 921600, 1000000, 1500000, 2000000 , 2500000 , 3000000 , 3500000 , 4000000 , 4500000 , 5000000 , 12000000]:
#     try:
#         with serial.Serial('/dev/ttyUSB1', rate, timeout=1) as s:
#             print(f"✓ {rate} baud works")
#     except Exception as e:
#         print(f"✗ {rate} baud failed: {e}")
import serial
import time

# Test list of baudrates you want to try
baudrates_to_test = [
    115200, 230400, 460800, 921600, 1000000,
    1500000, 2000000, 2500000, 3000000, 3500000,
    4000000, 4500000, 5000000
]

def test_baudrate(port, initial_baud, target_baud):
    try:
        # Open port at initial baud
        ser = serial.Serial(port, initial_baud, timeout=1)
        time.sleep(2)  # Wait for ESP32 to be ready
        
        # Send command to change baudrate on ESP32
        cmd = f"SET_BAUD:{target_baud}\n"
        ser.write(cmd.encode())
        time.sleep(0.2)
        
        # Read response after baud change command
        response = ser.readline().decode(errors='ignore').strip()
        print(f"ESP32 response: {response}")

        ser.close()
        time.sleep(0.1)
        
        # Reopen port with new baudrate
        ser = serial.Serial(port, target_baud, timeout=1)
        time.sleep(0.5)
        
        # Send a test message
        ser.write(b"HELLO\n")
        time.sleep(0.2)
        
        # Read echo back
        echo = ser.readline().decode(errors='ignore').strip()
        if echo == "ECHO: HELLO":
            print(f"✓ {target_baud} baud works")
            success = True
        else:
            print(f"✗ {target_baud} baud failed or no echo")
            success = False
        
        ser.close()
        return success
        
    except Exception as e:
        print(f"✗ {target_baud} baud error: {e}")
        return False

def main():
    port = "/dev/ttyUSB1"  # Change to your serial port
    initial_baud = 115200
    
    print(f"Starting baud rate test on port {port} from {initial_baud} baud")
    
    for baud in baudrates_to_test:
        print(f"Testing baud: {baud}")
        if not test_baudrate(port, initial_baud, baud):
            print(f"Stopping test at {baud} baud due to failure.")
            break
        initial_baud = baud  # Update for next iteration

if __name__ == "__main__":
    main()
