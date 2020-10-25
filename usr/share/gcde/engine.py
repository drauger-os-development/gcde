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
import inspect
import copy
import shlex
import multiprocessing
import gcde
import plugins

gcde.common.set_procname("gcde")

# Define configuration location
home = os.getenv("HOME")
if home[-1] != "/":
    home = home + "/"
local_settings = home + ".config/gcde/global_settings.json"
local_tiles = home + ".config/gcde/tiles.json"
global_settings = "../../../etc/gcde/defaults-global.json"
global_tiles = "../../../etc/gcde/default-tiles.json"
themes_file = home + ".config/gtk-3.0/settings.ini"

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


def launch_autostarters():
    """Launch Autostart apps"""
    prefix = home + ".config/autostart/"
    file_list = os.listdir(prefix)
    for each in file_list:
        skip = False
        with open(prefix + each, "r") as file:
            data = file.read().split("\n")
        for each1 in data:
            if "X-GNOME-Autostart-enabled=false" == each1:
                skip = True
                break
        if skip:
            continue
        for each1 in data:
            if each1[:5] == "Exec=":
                execute = shlex.split(each1[5:])
                break
        subprocess.Popen(execute)
    for each in file_list:
        skip = False
        with open(prefix + each, "r") as file:
            data = file.read()
        if "X-GNOME-Autostart-enabled=" not in data:
            data = data.split("\n")
            data.append("X-GNOME-Autostart-enabled=false")
            data = "\n".join(data)
        os.remove(prefix + each)
        with open(prefix + each, "w") as file:
            file.write(data)


def autostart_enabled(file):
    """Get whether autostart is enabled for a file"""
    with open(path, "r") as file:
        data = file.read().split("\n")
    for each in enumerate(data):
        if "X-GNOME-Autostart-enabled" in data[each[0]]:
            data[each[0]] = data[each[0]].split("=")
            if data[each[0]][1] == "false":
                return False
            else:
                return True
    data.append("X-GNOME-Autostart-enabled=false")
    data = "\n".join(data)
    os.remove(path)
    with open(path, "w") as file:
        file.write(data)
    return False



def toggle_autostart(path):
    """Toggle Autostart setting"""
    with open(path, "r") as file:
        data = file.read().split("\n")
    for each in enumerate(data):
        if "X-GNOME-Autostart-enabled" in data[each[0]]:
            data[each[0]] = data[each[0]].split("=")
            if data[each[0]][1] == "false":
                data[each[0]][1] = "true"
            else:
                data[each[0]][1] = "false"
            data[each[0]] = "=".join(data[each[0]])
    data = "\n".join(data)
    os.remove(path)
    with open(path, "w") as file:
        file.write(data)


def desktop_to_json(path, x, y, w, h, extra_key="Hidden="):
    """Convert Desktop file to GCDE Tile Json"""
    hidden = (extra_key, len(extra_key))
    with open(path, "r") as file:
        data = file.read().split("\n")
    for each in range(len(data) - 1, -1, -1):
        if data[each] == "":
            del data[each]
    if len(data) < 4:
        return {}
    tile_settings = {}
    for each in data:
        if each[:5] == "Name=":
            tile_settings["name"] = each[5:]
        elif each[:5] == "Icon=":
            tile_settings["icon"] = each[5:]
        elif each[:hidden[1]] == hidden[0]:
            if each[hidden[1]:] == "true":
                tile_settings["hidden"] = True
            else:
                tile_settings["hidden"] = False
        elif each[:5] == "Exec=":
            tile_settings["execute"] = shlex.split(each[5:])
    if "hidden" not in tile_settings:
        tile_settings["hidden"] = False
    tile_settings["X"] = x
    tile_settings["Y"] = y
    tile_settings["width"] = w
    tile_settings["height"] = h
    return tile_settings


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
        self.background_launched = False

        self.reboot = {"exec":["reboot"],
    			"icon":"system-reboot",
    			"name":"Reboot",
    			"X":0,
    			"Y":2,
    			"width":int(width / 4),
    			"height":1}
        self.log_out = {"exec":["./logout.py"],
    			"icon":"system-log-out",
    			"name":"Log Out",
    			"X":int(width / 4),
    			"Y":2,
    			"width":int(width / 4),
    			"height":1}
        self.shutdown = {"exec":["poweroff"],
    			"icon":"gnome-shutdown",
    			"name":"Shutdown",
    			"X":int(width / 4) * 2,
    			"Y":2,
    			"width":int(width / 4),
    			"height":1}
        self.back = {"exec":["main"],
    			"icon":"application-exit",
    			"name":"Back",
    			"X":int(width / 4) * 3,
    			"Y":2,
    			"width":int(width / 4),
    			"height":1}
        self.back = gcde.tile.new(self.back)
        self.reboot = gcde.tile.new(self.reboot)
        self.poweroff = gcde.tile.new(self.shutdown)
        self.log_out = gcde.tile.new(self.log_out)

        subprocess.Popen(["/usr/bin/wmctrl", "-n", "1"])
        proc = multiprocessing.Process(target=launch_autostarters)
        proc.start()

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

    def session_manager(self, widget):
        """Basic Session Manager"""
        self.clear_window()

        title = Gtk.Label()
        title.set_markup("\n\tAre you sure?\t\n")
        title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(0.05,
                                                                    height))))
        self.grid.attach(title, 0, 0, width, 2)

        self.__place_tile__(self.log_out, scale=False)
        self.__place_tile__(self.reboot, scale=False)
        self.__place_tile__(self.poweroff, scale=False)
        self.__place_tile__(self.back, scale=False)

        self.show_all()

    def draw(self, widget, context):
        context.set_source_rgba(0, 0, 0, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)


    def tile(self, widget):
        """Get Tiles to place into Matrix, then place them"""
        self.clear_window()

        plugin_list = dir(plugins)
        for each in range(len(plugin_list) - 1, -1, -1):
            if plugin_list[each][0] == "_":
                del plugin_list[each]
            elif plugin_list[each] == "example":
                del plugin_list[each]
        plug_objs = []
        for each in plugin_list:
            plug_new = getattr(plugins, each)
            try:
                if plug_new.PLUGIN_TYPE == 0:
                    plug_objs.append(plug_new.plugin_setup(copy.deepcopy(self.tiles[each])))
                elif plug_new.PLUGIN_TYPE == 1:
                    plug_objs.append(plug_new.plugin_setup(copy.deepcopy(self.settings)))
                elif plug_new.PLUGIN_TYPE >= 2:
                    plug_objs.append(plug_new.plugin_setup({"loc":copy.deepcopy(self.tiles[each]),
                                                    "global":copy.deepcopy(self.settings)}))
            except KeyError:
                continue


        for each in self.tiles:
            if ("tile" in each.lower()) or (each in ("session_manager", "menu", "settings")):
                self.__place_tile__(gcde.tile.new(self.tiles[each]), scale=False)
        for each in plug_objs:
            self.__place_tile__(each, scale=False)

        del plug_objs,plugin_list,each

        self.show_all()

    def __place_tile__(self, tile, scale=True):
        """Place tile in matrix"""
        tile.make(copy.deepcopy(self.settings), width, height)
        tile_obj = tile.__get_internal_obj__()
        tile_settings = tile.get_settings()
        try:
            if tile_settings["exec"][0].lower() == "settings":
                tile_obj[0].connect("clicked", self.settings_window)
            elif tile_settings["exec"][0].lower() == "menu":
                tile_obj[0].connect("clicked", self.menu)
            elif tile_settings["exec"][0].lower() == "main":
                tile_obj[0].connect("clicked", self.tile)
            elif tile_settings["exec"][0].lower() == "session_manager":
                tile_obj[0].connect("clicked", self.session_manager)
            elif tile_settings["exec"][0].lower() == "restart":
                tile_obj[0].connect("clicked", self.restart)
            elif tile_settings["exec"][0].lower() == "autostart-settings":
                tile_obj[0].connect("clicked", self.autostart_settings)
            else:
                tile_obj[0].connect("clicked", tile.run)
        except TypeError:
            pass
        if scale:
            self.grid.attach(tile_obj[0],
                             gcde.common.scale(tile_obj[1], width),
                             gcde.common.scale(tile_obj[2], height),
                             gcde.common.scale(tile_obj[3], width),
                             gcde.common.scale(tile_obj[4], height))
        else:
            self.grid.attach(tile_obj[0], tile_obj[1], tile_obj[2], tile_obj[3],
                             tile_obj[4])

    def autostart_settings(self, widget):
        """Window to define which files should be autostart and which shouldn't"""
        self.clear_window()

        self.make_scrolling("clicked")
        prefix = home + ".config/autostart/"
        w = 1
        h = 1
        x = 0
        y = 2
        file_list = os.listdir(prefix)

        title = Gtk.Label()
        title.set_markup("\n\tAutostart Applications\t\n")
        title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(0.03,
                                                                    height))))
        self.grid.attach(title, 0, 0, 1, 2)

        for each in file_list:
            data = desktop_to_json(prefix + each, x, y, w, h,
                                   extra_key="X-GNOME-Autostart-enabled=")
            if len(data) == 0:
                continue
            check_box = Gtk.CheckButton.new_with_label(data["name"])
            check_box.set_active(data["hidden"])
            check_box.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(0.02,
                                                                        height))))
            self.grid.attach(check_box, data["X"], data["Y"], data["width"],
                             data["height"])
            y += 1

        back_button = {"exec":["settings"],
    				"icon":"application-exit",
    				"name":"Back",
    				"X":0,
    				"Y":y,
    				"width":1,
    				"height":1}
        back_button = gcde.tile.new(back_button)
        self.__place_tile__(back_button, scale=False)

        del w,h,x,y,file_list,prefix,check_box,each,data,title,back_button
        self.show_all()

    def settings_window(self, widget):
        """Settings Window"""
        self.clear_window()

        self.make_scrolling("clicked")

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

        self.X_scaler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1,
                                               10, 1)
        self.X_scaler.set_draw_value(True)
        self.X_scaler.set_value(self.settings["menu"]["width"])
        self.X_scaler.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(self.X_scaler, 0, 5, width, 2)

        self.Y_scaler = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1,
                                               10, 1)
        self.Y_scaler.set_draw_value(True)
        self.Y_scaler.set_value(self.settings["menu"]["height"])
        self.Y_scaler.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(self.Y_scaler, 0, 7, width, 2)

        theming_defaults = get_theming_defaults()
        gtk_themes = list_gtk_themes()
        icon_themes = list_icon_themes()

        theming_title = Gtk.Label()
        theming_title.set_markup("\n\tTheming\t\n")
        theming_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(sub_heading,
                                                                    height))))
        self.grid.attach(theming_title, 0, 9, width, 2)

        gtk_theming_title = Gtk.Label()
        gtk_theming_title.set_markup("\n\tGtk Theme\t\n")
        gtk_theming_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))
        self.grid.attach(gtk_theming_title, 0, 11, width, 2)

        self.gtk_theme_chooser = Gtk.ComboBoxText.new()
        for each in gtk_themes:
            self.gtk_theme_chooser.append(each, each)
        self.gtk_theme_chooser.set_active_id(theming_defaults["gtk-theme-name"])
        self.gtk_theme_chooser.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))

        self.grid.attach(self.gtk_theme_chooser, 0, 13, width, 2)

        icon_theming_title = Gtk.Label()
        icon_theming_title.set_markup("\n\tIcon Theme\t\n")
        icon_theming_title.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))
        self.grid.attach(icon_theming_title, 0, 15, width, 2)

        self.icon_theme_chooser = Gtk.ComboBoxText.new()
        for each in icon_themes:
            self.icon_theme_chooser.append(each.lower(), each)
        self.icon_theme_chooser.set_active_id(theming_defaults["gtk-icon-theme-name"])
        self.icon_theme_chooser.override_font(Pango.FontDescription("Open Sans %s" % (gcde.common.scale(label,
                                                                    height))))

        self.grid.attach(self.icon_theme_chooser, 0, 17, width, 2)

        sars = {"exec":["restart"],
    			"icon":"system-reboot",
    			"name":"Save and Restart GCDE",
    			"X":0,
    			"Y":19,
    			"width":int(width / 3),
    			"height":1}
        autolaunch = {"exec":["autostart-settings"],
                      "icon":"xfce4-session",
                      "name":"Autostart Applications",
                      "X":int(width / 3),
                      "Y":19,
                      "width":int(width / 3),
                      "height":1}
        quit = {"exec":["main"],
    			"icon":"application-exit",
    			"name":"Exit",
    			"X":int(width / 3) * 2,
    			"Y":19,
    			"width":int(width / 3),
    			"height":1}
        sars = gcde.tile.new(sars)
        quit = gcde.tile.new(quit)
        autolaunch = gcde.tile.new(autolaunch)
        self.__place_tile__(sars, scale=False)
        self.__place_tile__(autolaunch, scale=False)
        self.__place_tile__(quit, scale=False)

        del theming_defaults,gtk_themes,icon_themes,sub_heading,label

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
        with open(themes_file, "r") as file:
            data = file.read().split("\n")
        for each in range(len(data) - 1, -1, -1):
            data[each] = data[each].split("=")
        for each in data:
            if each[0] == "gtk-theme-name":
                each[1] = self.gtk_theme_chooser.get_active_id()
            elif each[0] == "gtk-icon-theme-name":
                each[1] = self.icon_theme_chooser.get_active_id()
        for each in enumerate(data):
            data[each[0]] = "=".join(data[each[0]])
        data = "\n".join(data)
        os.remove(themes_file)
        with open(themes_file, "w") as file:
            file.write(data)

    def menu(self, widget):
        """Application Menu"""
        self.clear_window()

        self.make_scrolling("clicked")

        prefix = "/usr/share/applications/"
        file_list = sorted(os.listdir(prefix))
        for each in range(len(file_list) - 1, -1, -1):
            if os.path.isdir(prefix + file_list[each]):
                del file_list[each]
        print(len(file_list))
        w = self.settings["menu"]["width"]
        h = self.settings["menu"]["height"]
        x = 0
        y = 0
        width_max = 7
        tiles = []
        back = {"exec":["main"],
                "icon":"application-exit",
                "name":"Back to Matrix",
                "X":x,
                "Y":y,
                "width":w,
                "height":h}
        tiles.append(gcde.tile.new(back))
        x += 1
        for each in file_list:
            skip = False
            with open(prefix + each, "r") as file:
                data = file.read().split("\n")
            for each1 in data:
                if "NoDisplay" in each1:
                    if each1[-4:].lower() == "true":
                        skip = True
                        break
                elif "OnlyShowIn" in each1:
                    trash = each1.split("=")
                    if "gcde" not in each1.lower():
                        skip = True
                        break
                elif "Terminal" in each1:
                    if each1[-4:].lower() == "true":
                        skip = True
                        break
                elif "" == each1:
                    break
            if skip:
                continue
            for each1 in data:
                if each1[:5] == "Name=":
                    name = each1[5:]
                elif each1[:5] == "Icon=":
                    icon = each1[5:]
                elif each1[:5] == "Exec=":
                    execute = shlex.split(each1[5:])
            tile_settings = {"exec":execute,
                             "icon":icon, "name":name,
                             "X":x, "Y":y, "width":w, "height":h}
            tiles.append(gcde.tile.new(tile_settings))
            if x >= width_max:
                x = 0
                y += 1
            else:
                x += 1
        for each in tiles:
            self.__place_tile__(each, scale=False)
        # Try to free some memeory
        del tiles
        del file_list

        self.show_all()

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


def list_icon_themes():
    """List Icon Themes"""
    themes = os.listdir("/usr/share/icons")
    for each in range(len(themes) - 1, -1, -1):
        if "default" in themes[each].lower():
            del themes[each]
    return themes


def list_gtk_themes(version=GTK_VERSION):
    """List GTK themes for a specific version"""
    themes_dir = "/usr/share/themes/"
    themes = os.listdir(themes_dir)
    for each in range(len(themes) - 1, -1, -1):
        sub = os.listdir(themes_dir + themes[each])
        if ("gtk-" + version) not in sub:
            del themes[each]
        elif "default" in themes[each].lower():
            del themes[each]
    return themes


def get_theming_defaults():
    """Get theming defaults"""
    with open(themes_file, "r") as file:
        defaults = file.read()
    defaults = defaults.split("\n")[1:]
    output = {}
    for each in range(len(defaults) - 1, -1, -1):
        defaults[each] = defaults[each].split("=")
        try:
            if defaults[each][0] == "gtk-application-prefer-dark-theme":
                del defaults[each]
                continue
            output[defaults[each][0]] = defaults[each][1]
        except IndexError:
            pass
    return output


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
