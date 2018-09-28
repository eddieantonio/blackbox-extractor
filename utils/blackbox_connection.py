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

from contextlib import closing

# import mysql.connector
# from mysql.connector import errorcode


raise ImportError("""

    Before using this, you must provide the username and password in
    blackbox_connection.py. Edit blackbox_connection.py, add the username and
    password, then delete these raise ImportError(...) lines.

""")

config = {
    'user': NotImplemented,  # <= CHANGE HERE
    'password': NotImplemented,  # <= CHANGE HERE
    'host': '127.0.0.1',
    'database': 'blackbox_production'
}


def mysql_connection():
    """
    MySQL connection.
    """
    return closing(mysql.connector.connect(**config))
