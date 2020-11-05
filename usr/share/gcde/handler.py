#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  handler.py
#
#  Copyright 2020 Thomas Castleman <contact@draugeros.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
"""Get Controller Support going"""
import time
import json
import sys
import subprocess
import multiprocessing
import pygame
import controller_support


class NoJoysticksError(Exception):
    """Error For No Joysticks. Made so special handling may be done"""
    pass


def initialize():
    """Setup for Controller Support"""
    pygame.init()
    joysticks = pygame.joystick.get_count()
    if joysticks < 1:
        raise NoJoysticksError("No Joysticks Found")
    # Search terms to determine which controller we are dealing with
    xbox = ["xbox", "x-box"]
    ps3 = ["ps3", "playstation 3"]
    ps4 = ["ps4", "playstation 4"]
    switch = ["switch"]
    j = pygame.joystick.Joystick(0)
    name = j.get_name().lower()
    for each in xbox:
        if each in name:
            return ["xbox", j]
    for each in ps3:
        if each in name:
            return ["ps3", j]
    for each in ps4:
        if each in name:
            return ["ps4", j]
    for each in switch:
        if each in name:
            return ["switch", j]
    return ["default", j]


def worker():
    """Worker Thread"""
    while True:
        data = None
        try:
            # Get appropriate config and object
            data = initialize()
        except NoJoysticksError:
            time.sleep(1)
            subprocess.Popen(sys.argv[0])
            exit()
        # Get appropriate config
        with open("/etc/gcde/controller-mapping.json", "r") as file:
            config = json.load(file)
        if data[0] == "default":
            config = config[config["default"]]
        elif ((data[0] == "switch") and ("switch" not in config)):
            config = config["ps4"]
            data[0] = "ps4"
        else:
            config = config[data[0]]
        button_process = multiprocessing.Process(target=controller_support.buttons.button_handler,
                                                 args=[data, config])
        button_process.start()
        analog_process = multiprocessing.Process(target=controller_support.analog.run, args=[])
        analog_process.start()


if __name__ == "__main__":
    worker()
