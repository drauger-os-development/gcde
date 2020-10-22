#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  sys_info.py
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
"""System Info Display"""
import gcde
import psutil
import subprocess
import copy
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk

PLUGIN_TYPE=0

class sys_info_display(gcde.tile.Tile):
    """Placeholder class"""
    def __init__(self):
        """replacement init"""
        print("INIT!")
        self.settings = {"exec":[],
                         "icon":None,
                         "name":"Name",
                         "X":0,
                         "Y":0,
                         "width":0.1,
                         "height":0.1}
        self.obj = Gtk.Label()

    def make(self, global_settings, width, height):
        """Make Sys Info Panel"""
        mem = list(str(psutil.virtual_memory().total / (1.074 * 10 ** 9)))
        points = 0
        for each in enumerate(mem):
            if mem[each[0] - points] == ".":
                points += 1
                if points == 3:
                    mem = "".join(mem)[:each[0] + 1]
                    break
        with open("/proc/cpuinfo", "r") as file:
            cpu = file.read().split("\n")
        for each in cpu:
            if "model name" in each:
                cpu = each.split(":")[1]
                break
        os = subprocess.check_output(["lsb_release", "-sd"]).decode()[:-1]
        cpu = "".join(cpu.split("(R)"))
        cpu = "".join(cpu.split("(TM)"))
        cpu = "".join(cpu.split("CPU "))
        # version = subprocess.check_output(["lsb_release", "-sr"]).decode()[:-1]
        user = subprocess.check_output(["whoami"]).decode()[:-1]
        disk = subprocess.check_output("df -h -x aufs -x tmpfs -x overlay -x drvfs --total 2>/dev/null | tail -1",
                                       shell=True).decode()[:-3].split(" ")
        disk_output = ""
        count = 0
        for each in disk:
            if each != "":
                count += 1
                if count == 2:
                    disk_output = each
                elif count == 3:
                    disk_output = each + " / " + disk_output
                    break

        info = """Welcome, %s!
OS: %s
CPU: %s
RAM: %s GiB
DISK USAGE: %s""" % (user, os, cpu, mem, disk_output)

        self.obj.set_label(info)
        self.obj.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(0.015,
                                                                  height))))
        self.obj.set_line_wrap(True)
        self.obj.set_margin_top(gcde.common.scale(0.0073, height))
        self.obj.set_margin_bottom(gcde.common.scale(0.0073, height))
        self.obj.set_margin_left(gcde.common.scale(0.006, width))
        self.obj.set_margin_right(gcde.common.scale(0.006, width))

        color = gcde.tile.Tile()
        color = color.__get_internal_obj__()[0].props.style.background[0].get_rgba()
        color = Gdk.Color.from_floats(color[0], color[1], color[2])
        color = Gdk.RGBA.from_color(color)
        self.obj.override_background_color(Gtk.StateFlags.NORMAL, color)



        # Remember to clean up after yourselves boys and girls!
        del cpu,os,user,mem,disk,disk_output,points,count,each,info,color


    def run(self, widget):
        """run whatever command needed"""
        pass


def plugin_setup(settings):
    """Setup Plugin"""
    # Minimal set up. Must be generated on demand
    settings["exec"] = [""]
    settings["icon"] = ""
    settings["name"] = ""
    mod = sys_info_display()
    mod.__set_settings__(new_settings=settings)
    return mod
