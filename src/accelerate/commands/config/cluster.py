#!/usr/bin/env python

# Copyright 2021 The HuggingFace Team. All rights reserved.
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

from accelerate.state import ComputeEnvironment, DistributedType

from .config_args import ClusterConfig
from .config_utils import _ask_field, _convert_distributed_mode, _convert_yes_no_to_bool


def get_cluster_input():
    distributed_type = _ask_field(
        "Which type of machine are you using? ([0] No distributed training, [1] multi-GPU, [2] TPU): ",
        _convert_distributed_mode,
        error_message="Please enter 0, 1 or 2.",
    )

    machine_rank = 0
    num_machines = 1
    main_process_ip = None
    main_process_port = None
    if distributed_type == DistributedType.MULTI_GPU:
        num_machines = _ask_field(
            "How many different machines will you use (use more than 1 for multi-node training)? [1]: ",
            lambda x: int(x),
            default=1,
        )
        if num_machines > 1:
            machine_rank = _ask_field(
                "What is the rank of this machine (from 0 to the number of machines - 1 )? [0]: ",
                lambda x: int(x),
                default=0,
            )
            main_process_ip = _ask_field(
                "What is the IP address of the machine that will host the main process? ",
            )
            main_process_port = _ask_field(
                "What is the port you will use to communicate with the main process? ",
                lambda x: int(x),
            )
    if distributed_type == DistributedType.TPU:
        main_training_function = _ask_field(
            "What is the name of the function in your script that should be launched in all parallel scripts? [main]: ",
            default="main",
        )
    else:
        main_training_function = "main"

    num_processes = _ask_field(
        "How many processes in total will you use? [1]: ",
        lambda x: int(x),
        default=1,
        error_message="Please enter an integer.",
    )

    if distributed_type != DistributedType.TPU:
        fp16 = _ask_field(
            "Do you wish to use FP16 (mixed precision)? [yes/NO]: ",
            _convert_yes_no_to_bool,
            default=False,
            error_message="Please enter yes or no.",
        )
    else:
        fp16 = False

    return ClusterConfig(
        compute_environment=ComputeEnvironment.LOCAL_MACHINE,
        distributed_type=distributed_type,
        num_processes=num_processes,
        fp16=fp16,
        machine_rank=machine_rank,
        num_machines=num_machines,
        main_process_ip=main_process_ip,
        main_process_port=main_process_port,
        main_training_function=main_training_function,
    )
