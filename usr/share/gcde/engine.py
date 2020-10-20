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
GTK_VERSION = "3.0"
import os
import shutil
import json
import gi
gi.require_version('Gtk', GTK_VERSION)
from gi.repository import Gtk, Gdk, Pango
import cairo
from subprocess import check_output, Popen
import gcde

gcde.common.set_procname("gcde")

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

# Make config dir
try:
    os.mkdir(home + ".config/gcde")
except FileExistsError:
    pass


def get_settings():
    """Get settings, global or local"""
    if os.path.exists(local_settings):
        with open(local_settings, "r") as file:
            return json.load(file)
    with open(global_settings, "r") as file:
        # shutil.copy(global_settings, local_settings)
        return json.load(file)


def get_tiles():
    """Get tile configurations, global or local"""
    if os.path.exists(local_tiles):
        with open(local_tiles, "r") as file:
            return json.load(file)
    with open(global_tiles, "r") as file:
        # shutil.copy(global_tiles, local_tiles)
        return json.load(file)


class Matrix(Gtk.Window):
    """Matrix in which Tiles live"""
    def __init__(self):
        """Make the Matrix"""
        Gtk.Window.__init__(self, title="GTK+ Console Desktop Environment")
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_spacing(1)
        self.grid.set_row_spacing(1)
        self.add(self.grid)
        self.settings = get_settings()

        self.tiles = get_tiles()

        self.scrolling = False

        self.main("clicked")

    def make_scrolling(self, widget):
        """Make current window scroll"""
        self.scrolling = True

        self.remove(self.grid)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC -
        # only if needed
        # - or NEVER)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC,
                                        Gtk.PolicyType.AUTOMATIC)
        self.add(self.scrolled_window)
        # self.scrolled_window.add_with_viewport(self.grid)
        self.scrolled_window.add(self.grid)

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


    def tile(self, widget):
        """Get Tiles to place into Matrix, then place them"""
        for each in self.tiles:
            self.__place_tile__(gcde.tile.new(self.tiles[each]))

    def __place_tile__(self, tile):
        """Place tile in matrix"""
        tile.make(self.settings, width, height)
        tile_obj = tile.__get_internal_obj__()
        tile_settings = tile.get_settings()
        if tile_settings["exec"][0].lower() == "settings":
            tile_obj[0].connect("clicked", self.settings_window)
        elif tile_settings["exec"][0].lower() == "menu":
            tile_obj[0].connect("clicked", self.tile)
        elif tile_settings["exec"][0].lower() == "main":
            tile_obj[0].connect("clicked", self.main)
        elif tile_settings["exec"][0].lower() == "restart":
            tile_obj[0].connect("clicked", self.restart)
        else:
            tile_obj[0].connect("clicked", tile.run)
        self.grid.attach(tile_obj[0],
                         gcde.common.scale(tile_obj[1], width),
                         gcde.common.scale(tile_obj[2], height),
                         gcde.common.scale(tile_obj[3], width),
                         gcde.common.scale(tile_obj[4], height))

    def settings_window(self, widget):
        """Settings Window"""
        self.clear_window()

        sub_heading = 0.025
        label = 0.015

        title = Gtk.Label()
        title.set_markup("\n\tSettings\t\n")
        title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(0.05,
                                                                    height))))
        self.grid.attach(title, 0, 0, width, 2)

        icon_title = Gtk.Label()
        icon_title.set_markup("\n\tIcon Size\t\n")
        icon_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(icon_title, 0, 1, width, 2)

        self.icon_scaler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 4,
                                               200, 2)
        self.icon_scaler.set_draw_value(True)
        self.icon_scaler.set_value(self.settings["icon size"])
        self.icon_scaler.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(self.icon_scaler, 0, 2, width, 2)

        menu_title = Gtk.Label()
        menu_title.set_markup("\n\tApplication Menu Tile Size\t\n")
        menu_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(menu_title, 0, 3, width, 2)

        X_title = Gtk.Label()
        X_title.set_markup("\n\tWidth\t\n")
        X_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))
        self.grid.attach(X_title, 0, 4, width, 2)

        Y_title = Gtk.Label()
        Y_title.set_markup("\n\tHeight\t\n")
        Y_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))
        self.grid.attach(Y_title, 0, 6, width, 2)

        self.X_scaler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.002,
                                               0.999, 2)
        self.X_scaler.set_digits(3)
        self.X_scaler.set_draw_value(True)
        self.X_scaler.set_value(self.settings["menu"]["width"])
        self.X_scaler.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(self.X_scaler, 0, 5, width, 2)

        self.Y_scaler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.002,
                                               0.999, 2)
        self.Y_scaler.set_digits(3)
        self.Y_scaler.set_draw_value(True)
        self.Y_scaler.set_value(self.settings["menu"]["height"])
        self.Y_scaler.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(self.Y_scaler, 0, 7, width, 2)

        sars = {"exec":["restart"],
    			"icon":"system-reboot",
    			"name":"Save and Restart GCDE",
    			"X":0,
    			"Y":8,
    			"width":0.05,
    			"height":0.05}
        quit = {"exec":["main"],
    			"icon":"application-exit",
    			"name":"Exit",
    			"X":100,
    			"Y":8,
    			"width":0.05,
    			"height":0.05}
        sars = gcde.tile.new(sars)
        #quit = gcde.tile.new(quit)
        self.__place_tile__(sars)
        #self.__place_tile__(quit)

        self.show_all()

    def restart(self, widget):
        """Restart GCDE"""
        self.save_settings("clicked")
        try:
            Popen(["/usr/share/gcde/restart.py"])
        except FileNotFoundError:
            Popen(["./restart.py"])

    def save_settings(self, widget):
        """Save settings to file"""
        try:
            os.remove(local_settings)
        except FileNotFoundError:
            pass
        self.settings["icon size"] = self.icon_scaler.get_value()
        self.settings["menu"]["width"] = self.X_scaler.get_value()
        self.settings["menu"]["height"] = self.Y_scaler.get_value()
        with open(local_settings, "w") as file:
            json.dump(self.settings, file, indent=1)




    def menu(self, widget):
        """Application Menu"""
        self.clear_window()

        prefix = "/usr/share/applications/"
        file_list = sorted(os.listdir(prefix))
        for each in range(len(file_list) - 1, -1, -1):
            if os.path.isdir(prefix + file_list[each]):
                del file_list[each]
        print(len(file_list))
        w = gcde.common.scale(self.settings["menu"]["width"], width)
        h = gcde.common.scale(self.settings["menu"]["height"], height)
        x = 0
        y = 0
        width_max = int(width / w)
        tiles = []
        for each in file_list:
            skip = False
            with open(prefix + each, "r") as file:
                data = file.read().split("\n")
            for each in data:
                if "NoDisplay" in each:
                    if each[-4:].lower() == "true":
                        skip = True
                        break
                elif "OnlyShowIn" in each:
                    trash = each.split("=")
                    if "gcde" not in each.lower():
                        skip = True
                        break
                elif "Terminal" in each:
                    if each[-4:].lower() == "true":
                        skip = True
                        break
                elif "" == each:
                    break
            if skip:
                continue
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
            else:
                x = x + 1
        print(len(tiles))
        tile_count = 1
        for each in tiles:
            self.__place_tile__(each)
            print("Tiles: %s" % (tile_count))
            break
            tile_count += 1

        #self.show_all()


    def clear_window(self):
        """Clear Window"""
        children = self.grid.get_children()
        for each in children:
            self.grid.remove(each)
        if self.scrolling:
            self.scrolled_window.remove(self.grid)
            self.remove(self.scrolled_window)
            self.add(self.grid)
            self.scrolling = False


def main():
    """Set up the Matrix desktop wide, make it transparent"""
    matrix = Matrix()
    matrix.tile("clicked")
    matrix.set_decorated(False)
    matrix.set_resizable(False)
    matrix.move(0, 0)
    matrix.set_size_request(width, height)
    matrix.set_keep_below(True)
    matrix.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
