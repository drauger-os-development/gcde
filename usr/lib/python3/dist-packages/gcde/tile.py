#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  tile.py
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
"""Tile Object library to create tiles with different functions on GCDE"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from subprocess import Popen
import gcde.common as common


class Tile():
    """Tile object for GCDE"""
    def __init__(self):
        """Intialize the Tile"""
        self.settings = {"exec":[],
                         "icon":None,
                         "name":"Name",
                         "X":0,
                         "Y":0,
                         "width":0.1,
                         "height":0.1}
        self.obj = Gtk.Button.new()
        self.obj.set_always_show_image(True)

    def __set_settings__(self, new_settings: dict):
        """Set inital settings for a Tile object"""
        for each in new_settings:
            self.settings[each] = new_settings[each]
        print("Set settings for : %s " % (new_settings["name"]))

    def change_setting(self, setting_key: str, setting_value):
        """Change an individual setting for an indivdual tile"""
        self.settings[setting_key] = setting_value

    def get_settings(self):
        """Get settings for a specific tile

        This is useful for debugging, and for re-initializing Tiles."""
        return self.settings

    def make(self, global_settings, width, height):
        """Define Tile drawing properties"""
        if global_settings["names"] is True:
            self.obj.set_label(self.settings["name"])
        icon_theme = Gtk.IconTheme.get_default()
        icon_info = icon_theme.lookup_icon(self.settings["icon"], 48, 0)
        image = GdkPixbuf.Pixbuf()
        try:
            image = image.new_from_file_at_scale(icon_info.get_filename(),
                                                 global_settings["icon size"],
                                                 global_settings["icon size"],
                                                 False)
        except AttributeError:
            icon_theme = Gtk.IconTheme.get_default()
            icon_info = icon_theme.lookup_icon("unknown", 48, 0)
            image = GdkPixbuf.Pixbuf()
            image = image.new_from_file_at_scale(icon_info.get_filename(),
                                                 global_settings["icon size"],
                                                 global_settings["icon size"],
                                                 False)
        image = Gtk.Image.new_from_pixbuf(image)
        self.obj.set_image(image)
        self.obj.set_image_position(Gtk.PositionType.TOP)
        self.obj.set_margin_top(common.scale(0.0073, height))
        self.obj.set_margin_bottom(common.scale(0.0073, height))
        self.obj.set_margin_left(common.scale(0.006, width))
        self.obj.set_margin_right(common.scale(0.006, width))
        # This line below has been commented out because it just makes Tiles
        # transparent. It doesn't blur the background. We must wait until GTK 4
        # for that capability.
        # self.obj.set_opacity(global_settings["blur"])

    def __get_internal_obj__(self):
        """Get internal GTK Object for Tile

        FOR INTERNAL GCDE USE ONLY"""
        return (self.obj, self.settings["X"], self.settings["Y"],
                self.settings["width"], self.settings["height"])

    def run(self, widget):
        """Execute Click action"""
        Popen(self.settings["exec"])


def new(settings: dict):
    """Make a new tile with the settings in the `settings` list.

    This is meant to normally be used by the GCDE engine to initalize and
    configure a tile
    """
    obj = Tile()
    obj.__set_settings__(new_settings=settings)
    return obj


def reset_tile(tile):
    """Reset a tile by destroying it and making a new one."""
    settings = tile.get_settings()
    tile = new(settings)
    return tile
