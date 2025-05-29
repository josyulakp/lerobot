#!/usr/bin/env python

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from pprint import pformat

import torch
import torchvision.transforms as transforms

from lerobot.common.datasets.lerobot_dataset import (
    LeRobotDataset,
    LeRobotDatasetMetadata,
    MultiLeRobotDataset,
)
from lerobot.common.datasets.transforms import ImageTransforms
from lerobot.configs.policies import PreTrainedConfig
from lerobot.configs.train import TrainPipelineConfig

IMAGENET_STATS = {
    "mean": [[[0.485]], [[0.456]], [[0.406]]],  # (c,1,1)
    "std": [[[0.229]], [[0.224]], [[0.225]]],  # (c,1,1)
}


def resolve_delta_timestamps(
    cfg: PreTrainedConfig, ds_meta: LeRobotDatasetMetadata
) -> dict[str, list] | None:
    """Resolves delta_timestamps by reading from the 'delta_indices' properties of the PreTrainedConfig.

    Args:
        cfg (PreTrainedConfig): The PreTrainedConfig to read delta_indices from.
        ds_meta (LeRobotDatasetMetadata): The dataset from which features and fps are used to build
            delta_timestamps against.

    Returns:
        dict[str, list] | None: A dictionary of delta_timestamps, e.g.:
            {
                "observation.state": [-0.04, -0.02, 0]
                "observation.action": [-0.02, 0, 0.02]
            }
            returns `None` if the the resulting dict is empty.
    """
    delta_timestamps = {}
    for key in ds_meta.features:
        if key == "next.reward" and cfg.reward_delta_indices is not None:
            delta_timestamps[key] = [i / ds_meta.fps for i in cfg.reward_delta_indices]
        if key == "action" and cfg.action_delta_indices is not None:
            delta_timestamps[key] = [i / ds_meta.fps for i in cfg.action_delta_indices]
        if key.startswith("observation.") and cfg.observation_delta_indices is not None:
            delta_timestamps[key] = [i / ds_meta.fps for i in cfg.observation_delta_indices]

    if len(delta_timestamps) == 0:
        delta_timestamps = None

    return delta_timestamps


def make_dataset(cfg: TrainPipelineConfig) -> LeRobotDataset | MultiLeRobotDataset:
    """Handles the logic of setting up delta timestamps and image transforms before creating a dataset.

    Args:
        cfg (TrainPipelineConfig): A TrainPipelineConfig config which contains a DatasetConfig and a PreTrainedConfig.

    Raises:
        NotImplementedError: The MultiLeRobotDataset is currently deactivated.

    Returns:
        LeRobotDataset | MultiLeRobotDataset
    """
    if isinstance(cfg.dataset.repo_id, str):
        ds_meta = LeRobotDatasetMetadata(
            cfg.dataset.repo_id, root=cfg.dataset.root, revision=cfg.dataset.revision
        )
        
        logging.info(f"Loading dataset: {cfg.dataset.repo_id}")
        
        # Check if we need to add resize transforms for camera images with different shapes
        camera_shapes = {}
        for key, feature in ds_meta.features.items():
            if feature.get("dtype") in ["video", "image"] and key.startswith("observation.images."):
                camera_shapes[key] = feature["shape"]
                logging.info(f"Found camera '{key}' with shape: {feature['shape']}")
        
        # If we have multiple cameras with different shapes, find the common size (use the smallest)
        if len(camera_shapes) > 1:
            shapes = list(camera_shapes.values())
            logging.info(f"Detected {len(shapes)} camera views with shapes: {shapes}")
            
            if not all(shape == shapes[0] for shape in shapes):
                logging.info("Camera shapes are different, need to resize to common dimensions")
                
                # Find the smallest dimensions (only consider height and width, not channels)
                min_height = min(shape[0] for shape in shapes)  # height is first dimension
                min_width = min(shape[1] for shape in shapes)   # width is second dimension
                target_size = (min_height, min_width)
                
                logging.info(f"Resizing all cameras to smallest dimensions: {target_size}")
                
                # Create resize transforms
                additional_transforms = [transforms.Resize(target_size)]
                
                if cfg.dataset.image_transforms.enable:
                    logging.info("Adding resize transform to existing image transforms")
                    # Prepend resize to existing transforms
                    existing_transforms = ImageTransforms(cfg.dataset.image_transforms)
                    image_transforms = transforms.Compose([
                        transforms.Resize(target_size),
                        existing_transforms
                    ])
                else:
                    logging.info("Creating new resize transform (no existing transforms)")
                    image_transforms = transforms.Compose(additional_transforms)
            else:
                logging.info("All camera shapes are the same, no resizing needed")
                image_transforms = (
                    ImageTransforms(cfg.dataset.image_transforms) if cfg.dataset.image_transforms.enable else None
                )
        else:
            logging.info(f"Single camera detected or no cameras found. Camera count: {len(camera_shapes)}")
            image_transforms = (
                ImageTransforms(cfg.dataset.image_transforms) if cfg.dataset.image_transforms.enable else None
            )
        
        logging.info(f"Final image transforms: {image_transforms}")
        
        delta_timestamps = resolve_delta_timestamps(cfg.policy, ds_meta)
        dataset = LeRobotDataset(
            cfg.dataset.repo_id,
            root=cfg.dataset.root,
            episodes=cfg.dataset.episodes,
            delta_timestamps=delta_timestamps,
            image_transforms=image_transforms,
            revision=cfg.dataset.revision,
            video_backend=cfg.dataset.video_backend,
        )
    else:
        raise NotImplementedError("The MultiLeRobotDataset isn't supported for now.")
        dataset = MultiLeRobotDataset(
            cfg.dataset.repo_id,
            # TODO(aliberts): add proper support for multi dataset
            # delta_timestamps=delta_timestamps,
            image_transforms=image_transforms,
            video_backend=cfg.dataset.video_backend,
        )
        logging.info(
            "Multiple datasets were provided. Applied the following index mapping to the provided datasets: "
            f"{pformat(dataset.repo_id_to_index, indent=2)}"
        )

    if cfg.dataset.use_imagenet_stats:
        for key in dataset.meta.camera_keys:
            for stats_type, stats in IMAGENET_STATS.items():
                dataset.meta.stats[key][stats_type] = torch.tensor(stats, dtype=torch.float32)
    
    return dataset
