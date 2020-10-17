#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  engine.py
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
"""Engine for GCDE"""
import os
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import check_output
import gcde

# Define configuration location
home = os.getenv("HOME")
if home[-1] != "/":
    home = home + "/"
local_settings = home + ".config/gcde/global_settings.json"
local_tiles = home + ".config/gcde/tiles.json"
global_settings = "../../../etc/gcde/defaults-global.json"
global_tiles = "../../../etc/gcde/default-tiles.json"

# Get screen resolution for proper scaling
results = check_output(['xrandr']).decode().split("current")[1].split(",")[0]
width = results.split("x")[0].strip()
height = results.split("x")[1].strip()
width = int(width)
height = int(height)

class Matrix(Gtk.Window):
    """Matrix in which Tiles live"""
    def __init__(self):
        """Make the Matrix"""
        Gtk.Window.__init__(self, title="GTK+ Console Desktop Environment")
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.grid)

    def tile(self):
        """Get Tiles to place into Matrix, then place them"""
        tiles = get_tiles()
        tile_objs = []
        for each in tiles:
            self.__place_tile__(gcde.tile.new(tiles[each]))

    def __place_tile__(self, tile):
        """Place tile in matrix"""
        tile = tile.__get_internal_obj__()
        self.grid.attach(tile[0], gcde.common.scale(tile[1], width),
                         gcde.common.scale(tile[2], height),
                         gcde.common.scale(tile[3], width),
                         gcde.common.scale(tile[4], height))


def get_settings():
    """Get settings, global or local"""
    if os.path.exists(local_settings):
        with open(local_settings, "r") as file:
            return json.load(file)
    with open(global_settings, "r") as file:
        return json.load(file)


def get_tiles():
    """Get tile configurations, global or local"""
    if os.path.exists(local_tiles):
        with open(local_tiles, "r") as file:
            return json.load(file)
    with open(global_tiles, "r") as file:
        return json.load(file)


def main():
    """Set up the Matrix desktop wide, make it transparent"""
    matrix = Matrix()
    matrix.tile()
    matrix.set_decorated(False)
    matrix.set_resizable(False)
    matrix.set_position(Gtk.WindowPosition.CENTER)
    matrix.fullscreen()
    matrix.set_keep_below(True)
    matrix.set_opacity(0)
    matrix.show_all()

main()
