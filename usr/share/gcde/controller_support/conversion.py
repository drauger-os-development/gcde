#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conversion.py
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
# TODO: Fix error from "backspace" and "caps_lock": throws some sort of error from pynput
"""Convert Human-Readable Input to Machine-Readable Output"""
from pynput.keyboard import Key, Controller

def type_out(output_key):
	keyboard=Controller()
	#output_key=sys.argv[1]
	output_key=str(output_key)
	output_key=output_key.lower()
	if output_key == "backspace":
		keyboard.press(Key.backspace)
		keyboard.release(Key.backspace)
	elif output_key == "caps_lock" or output_key == "shift":
		keyboard.press(Key.caps_lock)
		keyboard.release(Key.caps_lock)
	elif output_key == "space":
		keyboard.press(Key.space)
		keyboard.release(Key.space)
	elif output_key == "left":
		keyboard.press(Key.left)
		keyboard.release(Key.left)
	elif output_key == "right":
		keyboard.press(Key.right)
		keyboard.release(Key.right)
	elif output_key == "up":
		keyboard.press(Key.up)
		keyboard.release(Key.up)
	elif output_key == "down":
		keyboard.press(Key.down)
		keyboard.release(Key.down)
	elif output_key == "enter":
		keyboard.press(Key.enter)
		keyboard.release(Key.enter)
	elif output_key == "tab":
		keyboard.press(Key.tab)
		keyboard.release(Key.tab)
	else:
		keyboard.press(output_key)
		keyboard.release(output_key)
		keyboard.release(Key.caps_lock)
