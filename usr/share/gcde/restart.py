#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  restart.py
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
"""Restart GCDE"""
import gcde
import os
import psutil
import signal
import subprocess

gcde.common.set_procname("gcde-re")

pid = None
process_name = "gcde"

for proc in psutil.process_iter():
    if process_name == proc.name():
       pid = proc.pid

os.kill(pid, signal.SIGTERM)
try:
    subprocess.Popen(["/usr/share/gcde/engine.py"])
except FileNotFoundError:
    subprocess.Popen(["./engine.py"])
