#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  _plugin_example.py
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
"""Plugin Example Code"""
# There are 3 types of plugins:
#     * Foreground Plugins
#     * Background Plugins
#     * Multi-threaded Plugins
#
# Foreground Plugins are basic Tiles that provide basic functionality and run in the main thread.
# These plugins are easiest to make if you overwrite the Tile.run() function.
#
# Background Plugins do not need to use the Tile library.
# They allow more advanced functionality, but have no GUI component.
# These plugins CAN be multithreaded, but if no GUI component is present,
# it is still considered a Background Plugin.
#
# Multi-threaded Plugins have both a background and foreground component.
# They will have a GUI Tile that provides much more advanced functionality, such as
# system, memory, or network usage; app indicators; messaging clients built into Tiles;
# and more!

# This plugin will be a Foreground Plugin, which allows a user to update their
# system from a single click

# We need this to update a user's system correctly
import subprocess
# All Foreground Plugins NEED to import the gcde.Tile class
import gcde

# plugin_type defines what type of Plugin this is for GCDE.
# 0 = Foreground Plugin
# 1 = Background Plugin
# >= 2 = Multi-Threaded Plugin
# This also lets GCDE know how many threads to make. GCDE will pass the thread
# number to run() so that you can determine which thread does what.
PLUGIN_TYPE = 0

# This could be named run(), but just in case we avoided naming it that
# GCDE will know this is a Foreground Plugin, and thus will expect to get a modified
# Tile back, that's it
def _replacement_run(widget):
    """Function to overwrite Tile.run() with"""
    subprocess.Popen(["notify-send", "Updating apt cache . . ."])
    subprocess.check_output(["pkexec", "apt", "update"])
    subprocess.Popen(["notify-send", "Upgrading System . . ."])
    subprocess.check_output(["pkexec", "apt", "-y", "upgrade"])


def run(thread_number):
    """Demo run() function for Background and Multi-threaded Plugins"""
    print("I am Thread %s!" % (thread_number))


def plugin_setup(settings):
    """Setup plugin for GCDE"""
    # You can start by simply defining a Tile
    # Do NOT hard-code your plugin's location in the Matrix
    # This could overwrite a pre-existing Tile
    # The `settings` variable contains either location settings, or global settings,
    # or both. If both, location settings will be under settings["loc"]
    # global settings will be under settings["global"]
    #
    # Settings are passed to plugin_setup() by value, not by reference. So, attempting
    # to edit global settings from within a plugin will not affect a running GCDE
    # instance.
    #
    # If you plan to overwrite TIle.run(), leave "exec" blank, but it still must be defined.
    updater_settings = {"exec":[""],
                        "icon":"steam",
                        "name":"Update System",
                        "X":settings["X"],
                        "Y":settings["Y"],
                        "width":settings["width"],
                        "height":settings["height"]}
    # Make our tile
    updater = gcde.tile.new(updater_settings)
    # Redefine run()
    updater.run = _replacement_run
    # return our modified Tile
    return updater
