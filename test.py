from lerobot.common.policies.pi0.modeling_pi0 import PI0Policy
from lerobot.common.robot_devices.robots.utils import Robot
from lerobot.common.robot_devices.robots.configs import So101RobotConfig
from lerobot.common.robot_devices.robots.manipulator import ManipulatorRobot


import time
from lerobot.common.robot_devices.utils import (
    RobotDeviceAlreadyConnectedError,
    RobotDeviceNotConnectedError,
    busy_wait,
)
import torch 
from lerobot.common.robot_devices.robots.utils import Robot, make_robot_from_config

inference_time_s = 60
fps = 30
device = "cuda"  # TODO: On Mac, use "mps" or "cpu"

# ckpt_path = "outputs/train/act_koch_test/checkpoints/last/pretrained_model"
print("1")

# robot = make_robot_from_config(S101)

robot_config = So101RobotConfig(
    leader_arms={},
)

robot = ManipulatorRobot(robot_config)
# import ipdb
robot.connect()
# ipdb.set_trace()

follower_pos = robot.follower_arms["main"].read("Present_Position")
print("leader pos ", follower_pos)

# print("2")
# policy = PI0Policy.from_pretrained("lerobot/pi0")
# policy.to(device)
# print("3")
# robot.connect()
# print("connected")
# for _ in range(inference_time_s * fps):
#     print("4")
#     start_time = time.perf_counter()

#     # Read the follower state and access the frames from the cameras
#     observation = robot.capture_observation()

#     # Convert to pytorch format: channel first and float32 in [0,1]
#     # with batch dimension
#     for name in observation:
#         if "image" in name:
#             observation[name] = observation[name].type(torch.float32) / 255
#             observation[name] = observation[name].permute(2, 0, 1).contiguous()
#         observation[name] = observation[name].unsqueeze(0)
#         observation[name] = observation[name].to(device)

#     # Compute the next action with the policy
#     # based on the current observation
#     action = policy.select_action(observation)
#     # Remove batch dimension
#     action = action.squeeze(0)
#     # Move to cpu, if not already the case
#     action = action.to("cpu")
#     print("action ", action)
#     # Order the robot to move
#     robot.send_action(action)

#     dt_s = time.perf_counter() - start_time
#     busy_wait(1 / fps - dt_s)



