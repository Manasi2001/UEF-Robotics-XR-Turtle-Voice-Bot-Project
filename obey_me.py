#!/usr/bin/env python3

# Copyright 2022 Clearpath Robotics, Inc.
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
#
# @author Roni Kreinin (rkreinin@clearpathrobotics.com)

import rclpy
import requests
from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Directions, TurtleBot4Navigator
import joblib
import librosa
import soundfile as sf
import numpy as np
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import os
import warnings
warnings.filterwarnings("ignore")

path = '/home/std/ros2_ws/src/turtlebot4_tutorials/turtlebot4_python_tutorials/turtlebot4_python_tutorials/'

def get_commands():
    lines = []
    with open(os.path.join(path, 'commands.txt'), "r") as handler:
        lines = handler.readlines()
        if len(lines) == 0:
            return 'NOCOMMAND'
        else:
            command = lines[0]
    with open(os.path.join(path, 'commands.txt'), "w") as handler:
        if len(lines) != 0:
            handler.writelines(lines[1:])
        
    return command.strip()

def main():
    old_command = None
    rclpy.init()

    navigator = TurtleBot4Navigator()

    # Start on dock
    if not navigator.getDockedStatus():
        navigator.info('Docking before intialising pose')
        navigator.dock()
    

    initial_pose = navigator.getPoseStamped([2.0, 2.0], TurtleBot4Directions.NORTH)
    navigator.setInitialPose(initial_pose)
    navigator.undock()
    while True:
        command = get_commands()
        if command == 'NOCOMMAND':
            continue
        else:
            if command == 'go':
    	        goal_pose = navigator.getPoseStamped([1., 0.], TurtleBot4Directions.EAST)
            if command == 'left':
    	        goal_pose = navigator.getPoseStamped([0., -1.], TurtleBot4Directions.EAST)
            if command == 'right':
    	        goal_pose = navigator.getPoseStamped([0., 1.], TurtleBot4Directions.EAST)
            print('\n')
            print('Command to be executed:', command)
            print('\n')
            
        navigator.startToPose(goal_pose)

            
    rclpy.shutdown()


if __name__ == '__main__':

    main()
