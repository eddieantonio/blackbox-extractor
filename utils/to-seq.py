#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2017  Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

"""
Squeeze multiple ascending integers into a few `seq` commands.
"""

import sys

def print_command(first, last):
    if first == last:
        print("echo %d" %(first,))
    else:
        print("seq %d %d" %(first, last))


first = None
print("#!/bin/sh")
for line in sys.stdin:
    line = line.strip()
    if not line:
        break
    num = int(line)

    if first is None:
        first = last = num
        continue

    if num == last + 1:
        last = num
    else:
        # This marks a new range. Output the last one.
        print_command(first, last)
        # And start the new range.
        first = last = num
