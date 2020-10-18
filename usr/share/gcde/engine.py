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
from gi.repository import Gtk, Gdk
import cairo
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


class Matrix(Gtk.Window):
    """Matrix in which Tiles live"""
    def __init__(self):
        """Make the Matrix"""
        Gtk.Window.__init__(self, title="GTK+ Console Desktop Environment")
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.grid)
        self.settings = get_settings()

        self.main("clicked")

    def main(self, widget):
        self.clear_window()

        self.connect('destroy', Gtk.main_quit)
        self.connect('draw', self.draw)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)

        self.show_all()

    def draw(self, widget, context):
        context.set_source_rgba(0, 0, 0, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)


    def tile(self):
        """Get Tiles to place into Matrix, then place them"""
        tiles = get_tiles()
        for each in tiles:
            self.__place_tile__(gcde.tile.new(tiles[each]))

    def __place_tile__(self, tile):
        """Place tile in matrix"""
        tile.make(self.settings)
        tile_obj = tile.__get_internal_obj__()
        tile_settings = tile.get_settings()
        if tile_settings["exec"][0].lower() != "menu":
            tile_obj[0].connect("clicked", tile.run)
        else:
            tile_obj[0].connect("clicked", self.menu)
        self.grid.attach(tile_obj[0],
                         gcde.common.scale(tile_obj[1], width),
                         gcde.common.scale(tile_obj[2], height),
                         gcde.common.scale(tile_obj[3], width),
                         gcde.common.scale(tile_obj[4], height))

        self.show_all()

    def menu(self, widget):
        """Application Menu"""
        self.clear_window()

        prefix = "/usr/share/applications/"
        file_list = os.listdir(prefix)
        for each in range(len(file_list) - 1, -1, -1):
            if os.path.isdir(prefix + file_list[each]):
                del file_list[each]

        w = gcde.common.scale(self.settings["menu"]["width"], width)
        h = gcde.common.scale(self.settings["menu"]["height"], height)
        x = 0
        y = 0
        width_max = int(width / w)
        tiles = []
        for each in file_list:
            with open(prefix + each, "r") as file:
                data = file.read().split("\n")
            for each in data:
                if each[:5] == "Name=":
                    name = each[5:]
                elif each[:5] == "Icon=":
                    icon = each[5:]
            tile_settings = {"exec":["xdg-open", prefix + each],
                             "icon":icon, "name":name,
                             "X":x, "Y":y, "width":w, "height":h}
            tiles.append(gcde.tile.new(tile_settings))
            if x >= width_max:
                x = 0
                y = y + 1
        for each in tiles:
            self.__place_tile__(each)

    def clear_window(self):
        """Clear Window"""
        children = self.grid.get_children()
        for each in children:
            self.grid.remove(each)


def main():
    """Set up the Matrix desktop wide, make it transparent"""
    matrix = Matrix()
    matrix.tile()
    matrix.set_decorated(False)
    matrix.set_resizable(False)
    matrix.move(0, 0)
    matrix.set_size_request(width, height)
    matrix.set_keep_below(True)
    matrix.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
