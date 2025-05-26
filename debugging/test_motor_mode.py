from STservo_sdk import *  # Import the STservo SDK

# ==== Configuration ====
DEVICENAME = "/dev/ttyUSB0"     # Adjust as per your setup
BAUDRATE = 115200              # 1 Mbps is default for ST3215-HS
PROTOCOL_VERSION = 1.0          # Confirm if ST3215 uses Protocol 1.0

# ==== Registers ====
ADDR_MODE = 33                # Operating Mode register
ADDR_GOAL_SPEED = 47       # Goal Speed (2 bytes)
ADDR_PRESENT_SPEED = 58       # Present Speed
ADDR_GOAL_POSITION = 43
# ==== Initialize Communication ====
portHandler = PortHandler(DEVICENAME)
packetHandler = protocol_packet_handler(portHandler, PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    print("❌ Failed to open port")
    exit()

# Set port baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("❌ Failed to set baudrate")
    exit()

# ==== Function to Set Motor Mode ====
def set_motor_mode(servo_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(servo_id, ADDR_MODE, 0)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"❌ Servo {servo_id}: Comm error -", packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print(f"⚠️ Servo {servo_id}: Error -", packetHandler.getRxPacketError(dxl_error))
    else:
        print(f"✅ Servo {servo_id} set to Motor Mode")

# ==== Function to Set Speed ====
def set_motor_speed(servo_id, speed_val):
    # speed_val: 0 (stop), 1-1023 (forward), 1025-2047 (reverse)
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(servo_id, ADDR_GOAL_SPEED, speed_val)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"❌ Speed Set Failed for Servo {servo_id} -", packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print(f"⚠️ Error while setting speed on Servo {servo_id} -", packetHandler.getRxPacketError(dxl_error))
    else:
        print(f"⚙️ Servo {servo_id} speed set to {speed_val}")

def set_motor_position(servo_id, position_val):
    # position_val: 0-4095 (for 12-bit resolution)
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(servo_id, ADDR_GOAL_POSITION, position_val)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"❌ Position Set Failed for Servo {servo_id} -", packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print(f"⚠️ Error while setting position on Servo {servo_id} -", packetHandler.getRxPacketError(dxl_error))
    else:
        print(f"🔄 Servo {servo_id} position set to {position_val}")
# ==== Main Logic ====
servo_ids = [1]

for sid in servo_ids:
    set_motor_mode(sid)

# Example: set servo 1 forward at half speed
set_motor_speed(1, 1024)

set_motor_position(1, 2048)  # Set to mid-position (2048 for 12-bit resolution)

# Example: stop all
# for sid in servo_ids:
#     set_motor_speed(sid, 0)

# ==== Clean up ====
portHandler.closePort()
