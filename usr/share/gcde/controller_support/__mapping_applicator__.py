#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  __mapping_applicator__.py
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
"""Convert Analog Mappings to Keyboard events"""
import sys
import select
import gcde
from conversion import type_out


def apply_mapping():
    """Take Direction from Analog Mappings and Make Keyboard Events"""
    while True:
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline().lower()
            if line == "pausing!":
                continue
            else:
                type_out(line)

if __name__ == "__main__":
    gcde.common.set_procname("gcde-map-applyer")
    apply_mapping()
