#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  buttons.py
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
"""Button Handler"""
import pygame
import sys
import subprocess
from conversion import type_out


def __get_button_count__(joystick):
    """Get Button Count"""
    if not joystick.get_init():
        joystick.init()
    return joystick.get_numbuttons()


def button_handler(data, config):
    """Determine which function to use, then use it"""
    if data[0] == "xbox":
        xbox_handler(data[1], config)
    elif data[0] == "ps3":
        ps3_handler(data[1], config)
    elif data[0] in ("ps4", "switch"):
        switch_ps4_handler(data[1], config)


def xbox_handler(j, config):
    """Map Xbox Controllers"""
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                button = 0
                while button <= 12:
					try:
						j.get_button(button)
					except:
						continue
					if j.get_button(button):
						if button == 0:
							print(button)
							#button = "a"
							# type_out("space")
							break
						elif button == 1:
							print(button)
							#button = "b"
							break
						elif button == 2:
							#button = "x"
							print(button)
							# type_out("enter")
							break
						elif button == 3:
							print(button)
							#button = "y"
							# type_out("tab")
							break
						elif button == 4:
							print(button)
							#button = "left_bumper"
							# type_out("left")
							break
						elif button == 5:
							print(button)
							#button = "right_bumper"
							# type_out("right")
							break
						elif button == 6:
							print(button)
							#button = "back"
							break
						elif button == 7:
							print(button)
							#button = "start"
							break
						elif button == 8:
							print(button)
							#button = "menu""
							break
						elif button == 9:
							print(button)
							#left analog button
							#type_out("backspace")
							break
						elif button == 10:
							#right analog button
							print(button)
							break
						else:
							print(button)
							break
					else:
						button += 1

def switch_ps4_handler(j, config):
    """Map PS4/Switch Controllers"""
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                button = 0
                while button <= 12:
					try:
						j.get_button(button)
					except:
						continue
					if j.get_button(button):
						if button == 0:
							print(button)
							#SWITCH: Y
							type_out("tab")
							break
						elif button == 1:
							print(button)
							#SWITCH: B
							break
						elif button == 2:
							#SWITCH: A
							print(button)
							# type_out("space")
							break
						elif button == 3:
							print(button)
							#SWITCH: X
							# type_out("enter")
							break
						elif button == 4:
							print(button)
							#SWITCH: LEFT BUMPER
							# type_out("left")
							break
						elif button == 5:
							print(button)
							#SWITCH: RIGHT BUMPER
							# type_out("right")
							break
						elif button == 6:
							print(button)
							#SWITCH: LEFT TRIGGER
							# type_out("backspace")
							break
						elif button == 7:
							print(button)
							#SWITCH: RIGHT TRIGGER
							break
						elif button == 8:
							print(button)
							#SWITCH: -
							break
						elif button == 9:
							print(button)
							#SWITCH: +
							break
						else:
							print(button)
							break
					else:
						button = button+1

def ps3_handler():
    """Map PS3 Controllers"""
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                button = 0
                while button <= 12:
					try:
						j.get_button(button)
					except:
						continue
					if j.get_button(button):
						if button == 0:
							print(button)
							#PS3: Triangle
							# type_out("enter")
							break
						elif button == 1:
							print(button)
							#PS3: Circle
							# type_out("space")
							exit(0)
							break
						elif button == 2:
							#PS3: X
							print(button)
							# type_out("space")
							break
						elif button == 3:
							print(button)
							#SWITCH: X
							break
						elif button == 4:
							print(button)
							#PS3 LEFT BUMPER
							# type_out("left")
							break
						elif button == 5:
							print(button)
							#PS3: RIGHT BUMPER
							# type_out("right")
							break
						elif button == 6:
							print(button)
							#PS3: LEFT TRIGGER
							# type_out("backspace")
							break
						elif button == 7:
							print(button)
							#PS3: RIGHT TRIGGER
							break
						elif button == 8:
							print(button)
							#PS3: Select
							break
						elif button == 9:
							print(button)
							#PS3: Start
							break
						else:
							print(button)
							break
					else:
						button = button+1
