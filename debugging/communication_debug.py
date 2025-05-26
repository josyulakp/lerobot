# #!/usr/bin/env python3
# import serial
# import time
# import logging
# from struct import pack

# # === Configuration ===
# PORT       = '/dev/ttyUSB0'
# BAUDRATE   = 115200                # 115200 bps to ESP32
# SERVO_ID   = 3                        # ID to query
# ADDR_POS   = 56                       # Present position address (ST3215)
# DATA_LEN   = 2                        # Bytes to read
# TIMEOUT    = 0                        # Non-blocking
# INTER_BYTE = 0                        # No inter-byte delay

# # === Setup logging ===
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     datefmt="%H:%M:%S"
# )

# def make_read_packet(servo_id, addr, length):
#     """Builds an 8-byte SCServo/ST packet: [FF FF ID LEN INST P0 P1 CHK]."""
#     INST_READ = 0x02
#     length_byte = 4                   # INST + P0 + P1 + CHK
#     pkt = bytearray(8)
#     pkt[0:2] = b'\xFF\xFF'
#     pkt[2]   = servo_id & 0xFF
#     pkt[3]   = length_byte
#     pkt[4]   = INST_READ
#     pkt[5]   = addr & 0xFF
#     pkt[6]   = length & 0xFF
#     # checksum = ~(ID + LEN + INST + P0 + P1) & 0xFF
#     chk = ~(sum(pkt[2:7])) & 0xFF
#     pkt[7] = chk
#     return pkt

# def main():
#     # Open serial port non‐blocking
#     ser = serial.Serial(
#         PORT,
#         baudrate=BAUDRATE,
#         timeout=TIMEOUT,
#         inter_byte_timeout=INTER_BYTE
#     )                               # :contentReference[oaicite:2]{index=2}
#     ser.reset_input_buffer()

#     packet = make_read_packet(SERVO_ID, ADDR_POS, DATA_LEN)
#     pkt_len = len(packet)

#     logging.info(f"Starting latency test on {PORT} at {BAUDRATE} baud")

#     for cycle in range(10):
#         # 1. Write packet
#         t1 = time.perf_counter()     # :contentReference[oaicite:3]{index=3}
#         n_written = ser.write(packet)
#         t2 = time.perf_counter()

#         if n_written != pkt_len:
#             logging.error(f"Write incomplete: {n_written}/{pkt_len} bytes")

#         # 2. Wait for first response byte
#         first_byte = None
#         while True:
#             available = ser.in_waiting
#             if available > 0:
#                 t3 = time.perf_counter()
#                 first_byte = ser.read(1)
#                 break
#             # Optional: timeout protection
#             if time.perf_counter() - t1 > 0.1:  
#                 logging.warning("Timeout waiting for first byte")
#                 break

#         # 3. Read rest of packet
#         resp = bytearray(first_byte) if first_byte else bytearray()
#         expected_len = 6 + DATA_LEN  # FF FF ID LEN ERR P0... + CHK
#         while len(resp) < expected_len:
#             chunk = ser.read(expected_len - len(resp))
#             resp.extend(chunk)

#         t4 = time.perf_counter()

#         # 4. Log timings and buffer stats
#         write_dur   = (t2 - t1)*1e3       # ms
#         toff1       = (t3 - t1)*1e3       # ms to first byte
#         full_rt     = (t4 - t1)*1e3       # ms to full pkt
#         buf_after   = ser.in_waiting

#         logging.info(f"Cycle {cycle+1}: write={write_dur:.3f} ms, "
#                      f"to1st={toff1:.3f} ms, roundtrip={full_rt:.3f} ms, "
#                      f"buf_remaining={buf_after} bytes, resp={resp.hex()}")

#         time.sleep(0.1)  # avoid bus congestion

#     ser.close()

# if __name__ == "__main__":
#     main()
# import serial
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# # Serial port configuration
# PORT = '/dev/ttyUSB0'
# BAUDRATE = 115200
# TIMEOUT = 0  # Non-blocking mode

# def log_serial_data():
#     try:
#         with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
#             logging.info(f"Opened serial port {PORT} at {BAUDRATE} baud.")
#             buffer = bytearray()
#             last_time = time.perf_counter()

#             while True:
#                 if ser.in_waiting:
#                     byte = ser.read(1)
#                     current_time = time.perf_counter()
#                     time_diff = (current_time - last_time) * 1000  # Convert to milliseconds
#                     last_time = current_time

#                     buffer += byte
#                     logging.info(f"Received byte: {byte.hex()} | Time since last byte: {time_diff:.3f} ms")

#                     # Example: Check for end of packet (e.g., newline character)
#                     if byte == b'\n':
#                         logging.info(f"Complete packet: {buffer.hex()}")
#                         buffer.clear()
#                 else:
#                     time.sleep(0.001)  # Sleep briefly to prevent high CPU usage
#     except serial.SerialException as e:
#         logging.error(f"Serial exception: {e}")
#     except KeyboardInterrupt:
#         logging.info("Serial logging stopped by user.")

# if __name__ == "__main__":
#     log_serial_data()


# import serial
# import time
# import binascii
# import struct
# from datetime import datetime
# import sys

# class ServoDebugger:
#     """
#     A debugging tool for ST3215 servo communication through ESP32
#     """
    
#     # Protocol constants
#     HEADER = bytes([0xFF, 0xFF])  # Standard header for most servo protocols
#     READ_POSITION_CMD = 0x02      # Command code for reading position
#     POSITION_REGISTER = 0x38      # Register address for position (may vary, check documentation)
#     POSITION_LENGTH = 0x02        # Number of bytes in position value
    
#     def __init__(self, port, baudrate=115200, timeout=1.0):
#         """Initialize with serial port parameters"""
#         self.port = port
#         self.baudrate = baudrate
#         self.timeout = timeout
#         self.ser = None
#         self.log_file = None
    
#     def open_connection(self):
#         """Open serial connection to ESP32"""
#         try:
#             self.ser = serial.Serial(
#                 port=self.port,
#                 baudrate=self.baudrate,
#                 timeout=self.timeout,
#                 bytesize=serial.EIGHTBITS,
#                 parity=serial.PARITY_NONE,
#                 stopbits=serial.STOPBITS_ONE
#             )
#             print(f"Connection opened on {self.port} at {self.baudrate} baud")
            
#             # Create log file with timestamp
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             self.log_file = open(f"servo_debug_{timestamp}.log", "w")
#             self.log_file.write(f"=== Servo Communication Debug Log ===\n")
#             self.log_file.write(f"Started: {datetime.now()}\n")
#             self.log_file.write(f"Port: {self.port}, Baudrate: {self.baudrate}\n\n")
            
#             return True
#         except serial.SerialException as e:
#             print(f"Failed to open connection: {e}")
#             return False
    
#     def close_connection(self):
#         """Close the serial connection and log file"""
#         if self.ser and self.ser.is_open:
#             self.ser.close()
#             print("Serial connection closed")
        
#         if self.log_file:
#             self.log_file.write(f"\nSession ended: {datetime.now()}\n")
#             self.log_file.close()
#             print("Log file closed")
    
#     def calculate_checksum(self, packet_bytes):
#         """Calculate checksum for packet verification"""
#         # Common checksum method for servo protocols (adjust if necessary)
#         return (~sum(packet_bytes) & 0xFF)
    
#     def create_position_read_packet(self, servo_id):
#         """Create a packet to read position from a specified servo"""
#         # Length is: ID (1) + Length (1) + CMD (1) + Params (2) + Checksum (1) = 6
#         packet_length = 4  # Command byte + 2 parameter bytes + checksum
        
#         # Create packet without checksum first
#         packet = bytearray([
#             servo_id,
#             packet_length,
#             self.READ_POSITION_CMD,
#             self.POSITION_REGISTER,
#             self.POSITION_LENGTH
#         ])
        
#         # Calculate and append checksum
#         checksum = self.calculate_checksum(packet)
#         packet.append(checksum)
        
#         # Add header at the beginning
#         full_packet = self.HEADER + packet
        
#         return full_packet
    
#     def read_response(self, expected_length=None, timeout_override=None):
#         """
#         Read and parse the response from the servo
#         Returns (success, data, raw_bytes)
#         """
#         old_timeout = None
#         if timeout_override is not None:
#             old_timeout = self.ser.timeout
#             self.ser.timeout = timeout_override
        
#         try:
#             # Wait for header (0xFF 0xFF)
#             header = self.ser.read(2)
            
#             if len(header) < 2 or header != self.HEADER:
#                 self.log(f"Header not found or incorrect: {binascii.hexlify(header)}")
#                 return False, None, header
            
#             # Read ID and Length
#             id_length = self.ser.read(2)
#             if len(id_length) < 2:
#                 self.log(f"Failed to read ID and Length: {binascii.hexlify(id_length)}")
#                 return False, None, header + id_length
            
#             servo_id = id_length[0]
#             length = id_length[1]
            
#             # Read the rest of the packet based on length
#             remaining = self.ser.read(length)
#             if len(remaining) < length:
#                 self.log(f"Incomplete packet: expected {length} bytes, got {len(remaining)}")
#                 return False, None, header + id_length + remaining
            
#             # Full packet received, now validate
#             full_packet = header + id_length + remaining
            
#             # Extract command, data, and checksum
#             command = remaining[0]
#             data = remaining[1:-1]  # All bytes except command and checksum
#             received_checksum = remaining[-1]
            
#             # Verify checksum
#             calculated_checksum = self.calculate_checksum(id_length + remaining[:-1])
#             if calculated_checksum != received_checksum:
#                 self.log(f"Checksum mismatch: calculated {calculated_checksum:02X}, received {received_checksum:02X}")
#                 return False, None, full_packet
            
#             # Parse position data if it's a position response
#             if len(data) >= 2:
#                 position = struct.unpack('<H', data[:2])[0] if len(data) >= 2 else None
#                 return True, position, full_packet
#             else:
#                 return True, data, full_packet
                
#         except Exception as e:
#             self.log(f"Error reading response: {e}")
#             return False, None, b''
#         finally:
#             # Restore original timeout if changed
#             if old_timeout is not None:
#                 self.ser.timeout = old_timeout
    
#     def read_all_servo_positions(self, servo_ids=[1, 2, 3, 4, 5, 6], retry_count=3, inter_query_delay=0.05):
#         """Read positions from all specified servos with retry mechanism"""
#         positions = {}
        
#         print("\nReading positions from all servos...")
#         self.log("\n--- Starting batch position read ---")
        
#         start_time = time.time()
        
#         for servo_id in servo_ids:
#             position = None
#             attempts = 0
            
#             while position is None and attempts < retry_count:
#                 attempts += 1
                
#                 query_start = time.time()
#                 self.log(f"\nQuerying servo {servo_id} (attempt {attempts})")
                
#                 # Clear any pending data before sending new command
#                 self.ser.reset_input_buffer()
                
#                 # Create and send the read position packet
#                 packet = self.create_position_read_packet(servo_id)
#                 self.log(f"TX: {binascii.hexlify(packet).decode()}")
                
#                 send_time = time.time()
#                 self.ser.write(packet)
#                 self.ser.flush()
                
#                 # Read the response with progressively longer timeouts on retries
#                 timeout = self.timeout * (attempts * 0.5 + 1)
#                 success, pos_data, raw_data = self.read_response(timeout_override=timeout)
                
#                 receive_time = time.time()
#                 response_time = receive_time - send_time
                
#                 if raw_data:
#                     self.log(f"RX: {binascii.hexlify(raw_data).decode()}")
#                 else:
#                     self.log("RX: No data received")
                
#                 self.log(f"Response time: {response_time*1000:.2f} ms")
                
#                 if success and pos_data is not None:
#                     position = pos_data
#                     positions[servo_id] = position
#                     print(f"Servo {servo_id} position: {position} (response time: {response_time*1000:.2f} ms)")
#                 else:
#                     self.log(f"Failed to read position from servo {servo_id}")
#                     # Wait before retry
#                     time.sleep(0.1)
            
#             if position is None:
#                 print(f"⚠️ Failed to read position from servo {servo_id} after {retry_count} attempts")
            
#             # Wait between queries to different servos
#             time.sleep(inter_query_delay)
        
#         total_time = time.time() - start_time
#         self.log(f"\n--- Batch position read completed in {total_time*1000:.2f} ms ---")
#         print(f"Total time: {total_time*1000:.2f} ms")
        
#         return positions
    
#     def analyze_response_times(self, num_iterations=5):
#         """Analyze response times across multiple iterations"""
#         print("\n=== Response Time Analysis ===")
#         self.log("\n=== Response Time Analysis ===")
        
#         all_times = {}
#         for servo_id in range(1, 7):
#             all_times[servo_id] = []
        
#         for i in range(num_iterations):
#             print(f"\nIteration {i+1}/{num_iterations}")
#             self.log(f"\n--- Iteration {i+1}/{num_iterations} ---")
            
#             for servo_id in range(1, 7):
#                 # Clear buffers
#                 self.ser.reset_input_buffer()
                
#                 # Create and send packet
#                 packet = self.create_position_read_packet(servo_id)
                
#                 send_time = time.time()
#                 self.ser.write(packet)
#                 self.ser.flush()
                
#                 # Read response
#                 success, pos_data, raw_data = self.read_response()
#                 receive_time = time.time()
                
#                 response_time = receive_time - send_time
#                 all_times[servo_id].append(response_time)
                
#                 if success:
#                     print(f"Servo {servo_id}: {response_time*1000:.2f} ms")
#                 else:
#                     print(f"Servo {servo_id}: Failed")
                
#                 # Wait between queries
#                 time.sleep(0.05)
            
#             # Wait between iterations
#             time.sleep(0.5)
        
#         # Print analysis
#         print("\n=== Analysis Results ===")
#         self.log("\n=== Analysis Results ===")
        
#         for servo_id in range(1, 7):
#             times = [t*1000 for t in all_times[servo_id] if t > 0]  # Convert to ms
#             if times:
#                 avg_time = sum(times) / len(times)
#                 max_time = max(times)
#                 min_time = min(times)
#                 success_rate = len(times) / num_iterations * 100
                
#                 print(f"Servo {servo_id}: Avg={avg_time:.2f}ms, Min={min_time:.2f}ms, Max={max_time:.2f}ms, Success={success_rate:.1f}%")
#                 self.log(f"Servo {servo_id}: Avg={avg_time:.2f}ms, Min={min_time:.2f}ms, Max={max_time:.2f}ms, Success={success_rate:.1f}%")
#             else:
#                 print(f"Servo {servo_id}: No successful responses")
#                 self.log(f"Servo {servo_id}: No successful responses")
    
#     def test_communication_parameters(self):
#         """Test different communication parameters to find optimal settings"""
#         print("\n=== Testing Communication Parameters ===")
#         self.log("\n=== Testing Communication Parameters ===")
        
#         # Test different timeout values
#         timeouts = [0.1, 0.3, 0.5, 1.0]
#         best_timeout = None
#         best_success = 0
        
#         for timeout in timeouts:
#             self.ser.timeout = timeout
#             print(f"\nTesting timeout: {timeout}s")
#             self.log(f"\n--- Testing timeout: {timeout}s ---")
            
#             success_count = 0
#             for servo_id in range(1, 7):
#                 packet = self.create_position_read_packet(servo_id)
#                 self.ser.write(packet)
#                 success, pos_data, _ = self.read_response()
#                 if success:
#                     success_count += 1
#                 time.sleep(0.05)
            
#             success_rate = success_count / 6 * 100
#             print(f"Success rate with timeout={timeout}s: {success_rate:.1f}%")
#             self.log(f"Success rate with timeout={timeout}s: {success_rate:.1f}%")
            
#             if success_rate > best_success:
#                 best_success = success_rate
#                 best_timeout = timeout
        
#         print(f"\nRecommended timeout: {best_timeout}s (Success rate: {best_success:.1f}%)")
#         self.log(f"\nRecommended timeout: {best_timeout}s (Success rate: {best_success:.1f}%)")
        
#         # Restore default timeout
#         self.ser.timeout = self.timeout
    
#     def log(self, message):
#         """Write message to log file with timestamp"""
#         if self.log_file:
#             timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
#             self.log_file.write(f"[{timestamp}] {message}\n")
#             self.log_file.flush()  # Ensure data is written immediately


# def main():
#     """Main program entry point"""
#     # Default port names by platform
#     default_port = 'COM3' if sys.platform == 'win32' else '/dev/ttyUSB0'
    
#     # Get port from command line if provided
#     port = sys.argv[1] if len(sys.argv) > 1 else default_port
    
#     print("=== ST3215 Servo Communication Debugger ===")
#     print(f"Using port: {port}")
    
#     # Create debugger instance
#     debugger = ServoDebugger(port=port, baudrate=115200, timeout=0.5)
    
#     if not debugger.open_connection():
#         print("Failed to open serial connection. Exiting.")
#         return
    
#     try:
#         # Main menu loop
#         while True:
#             print("\n=== Servo Debug Menu ===")
#             print("1. Read all servo positions")
#             print("2. Analyze response times")
#             print("3. Test different timeout values")
#             print("4. Exit")
            
#             choice = input("Select an option (1-4): ")
            
#             if choice == '1':
#                 debugger.read_all_servo_positions()
#             elif choice == '2':
#                 debugger.analyze_response_times()
#             elif choice == '3':
#                 debugger.test_communication_parameters()
#             elif choice == '4':
#                 print("Exiting...")
#                 break
#             else:
#                 print("Invalid option. Please try again.")
    
#     finally:
#         # Ensure connection is closed properly
#         debugger.close_connection()


# if __name__ == "__main__":
#     main()

# import serial
# import time
# import struct
# import binascii
# from datetime import datetime

# SERVO_IDS = [1, 2, 3, 4, 5, 6]  # Update as per your setup

# PORT = "/dev/ttyUSB0"
# BAUDRATE = 115200
# TIMEOUT = 0.3  # Slightly tight for real-time test

# HEADER = bytes([0xFF, 0xFF])
# CMD_READ = 0x02
# POS_REG = 0x38
# POS_LEN = 0x02

# def checksum(data):
#     return (~sum(data) & 0xFF)

# def make_read_packet(servo_id):
#     packet = bytearray([servo_id, 4, CMD_READ, POS_REG, POS_LEN])
#     packet.append(checksum(packet))
#     return HEADER + packet

# def parse_response(resp):
#     if len(resp) < 8 or resp[:2] != HEADER:
#         return None, "Invalid header"
    
#     data = resp[5:-1]
#     if len(data) != 2:
#         return None, "Invalid data length"

#     position = struct.unpack('<H', data)[0]
#     return position, None

# def log_packet(label, raw):
#     print(f"{label}: {binascii.hexlify(raw).decode()}")

# def main():
#     print(f"[INFO] Opening serial on {PORT} @ {BAUDRATE}")
#     with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
#         print("\n[INFO] Starting synchronous servo read...\n")

#         start = time.time()

#         for servo_id in SERVO_IDS:
#             ser.reset_input_buffer()
#             packet = make_read_packet(servo_id)

#             log_packet(f"TX (ID={servo_id})", packet)
#             t_send = time.time()
#             ser.write(packet)

#             # Expected 2 header + 2 (ID,Len) + 1 cmd + 2 data + 1 checksum = 8 bytes
#             response = ser.read(8)
#             t_recv = time.time()

#             log_packet(f"RX (ID={servo_id})", response)

#             position, error = parse_response(response)
#             if error:
#                 print(f"[FAIL] Servo {servo_id}: {error}")
#             else:
#                 rtt = (t_recv - t_send) * 1000
#                 print(f"[OK] Servo {servo_id}: Pos={position}  | RTT={rtt:.2f} ms")

#             print("-" * 50)
#             time.sleep(0.03)  # Small inter-packet gap

#         total = (time.time() - start) * 1000
#         print(f"\n✅ All synchronous reads complete in {total:.2f} ms")

# if __name__ == "__main__":
#     main()

import threading
import serial
import time
import binascii
from datetime import datetime

PORT      = '/dev/ttyUSB0'
BAUDRATE  = 115200
LOG_FILE  = 'serial_sniff.log'

def sniffer_thread(ser):
    """Background thread that logs all incoming bytes."""
    with open(LOG_FILE, 'a') as log:
        log.write(f"\n=== Sniffer Started at {datetime.now()} ===\n")
        last_time = time.time()
        while ser.is_open:
            n = ser.in_waiting  # number of bytes ready to read :contentReference[oaicite:0]{index=0}
            if n:
                data = ser.read(n)  # non-blocking read :contentReference[oaicite:1]{index=1}
                now = time.time()
                delta = (now - last_time) * 1000
                last_time = now

                hex_data = binascii.hexlify(data).decode('ascii')
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                entry = f"[{timestamp}] (+{delta:.2f} ms): {hex_data}\n"
                
                print(entry, end='')       # print to console
                log.write(entry)           # append to log file
            else:
                time.sleep(0.001)  # small sleep to avoid busy-loop :contentReference[oaicite:2]{index=2}

def main():
    # Open port in non-blocking mode
    ser = serial.Serial(PORT, BAUDRATE, timeout=0)  # timeout=0 for non-blocking reads :contentReference[oaicite:3]{index=3}
    
    # Start sniffer thread
    t = threading.Thread(target=sniffer_thread, args=(ser,), daemon=True)
    t.start()
    
    print(f"Sniffer running on {PORT} at {BAUDRATE} baud. Type commands below:\n")
    
    try:
        # Main loop: user can send commands
        while True:
            cmd = input("> ")
            if cmd.lower() in ('exit', 'quit'):
                break
            ser.write((cmd + '\r\n').encode('ascii'))  # send user input :contentReference[oaicite:4]{index=4}
    finally:
        ser.close()
        print("\nSerial port closed. Sniffer stopped.")

if __name__ == "__main__":
    main()
