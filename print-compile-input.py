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
Prints source code at a particular revision.

A reimplementation of /tools/ncc/bin/print-compile-input.
"""

import argparse
import os
import platform
import struct
import sys
from collections import namedtuple
from contextlib import closing

from blackbox_connection import mysql_connection


# From the BlueJ Blackbox Data Collection Researchers' Handbook, Section 9.1.
# • 64-bit integer for source file id. (Corresponds to “id” column in
#   source_files table (see Section 3.7 on page 27).)
# • 64-bit integer for master event id for the compilation event. (Corresponds
#   to “id” column in master_events table (see chapter 2 on page 11).)
# • 64-bit integer for the starting position within the payload file. (Byte
#   position in file, not character position in UTF8 string.)
# • 32-bit integer for the length within the payload file. (Again, byte
#   length, not character length.)
# • 32-bit integer that is 1 if the compile was successful, 0 if it was an
#   error. (Copied from database for easy reference.)
index_fmt = struct.Struct('>QQQII')
assert index_fmt.size == 32


_IndexEntry = namedtuple('_IndexEntry', 'source_file_id master_event_id start length success')

class IndexEntry(_IndexEntry):
    @classmethod
    def from_file(cls, index_file):
        return cls(*index_fmt.unpack(index_file.read(index_fmt.size)))

    @property
    def key(self):
        return self.source_file_id, self.master_event_id


class Index(object):
    def __init__(self, datestr):
        self.datestr = datestr
        table = self.table = {}
        with open_index(datestr) as index_file:
            while True:
                try:
                    entry = IndexEntry.from_file(index_file)
                except struct.error:
                    break
                table[entry.key] = entry

    def __getitem__(self, key):
        entry = self.table[key]
        with open_payload(self.datestr) as payload_file:
            payload_file.seek(entry.start)
            return payload_file.read(entry.length)

    def __len__(self):
        return len(self.table)


def lookup(source_file_id, master_event_id):
    index = get_index(master_event_id)
    return index[source_file_id, master_event_id]


def date_of(master_event_id):
    """
    >>> date_of(35238)
    '2013-06-12'
    """
    with closing(cnx.cursor()) as cur:
        cur.execute("""
            SELECT DATE(created_at)
              FROM master_events
             WHERE id = %s
        """, [master_event_id])
        row, = cur.fetchall()
        return str(row[0])


def path_of(name):
    return os.path.join(base_directory, name)


def open_index(datestr):
    return open(path_of('index-' + datestr), 'rb')


def open_payload(datestr):
    return open(path_of('payload-' + datestr), 'rb')


def get_index(master_event_id):
    return Index(date_of(master_event_id))


def test():
    global cnx
    with mysql_connection() as cnx:
        index = get_index(35238)
        assert len(index) == 174752 / 32
        source_code = lookup(1246, 35238)
        assert len(source_code) == 9734


def main(source_file_id, master_event_id):
    global cnx
    with mysql_connection() as cnx:
        source_code = lookup(source_file_id, master_event_id)
    # Reopen output in binary mode to prevent pipes from breaking from weird
    # implict encoding conversion.
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb')
    sys.stdout.write(source_code)


# Set up the argument parser
if platform.node() == 'mbp.local':
    default_directory = os.path.dirname(os.path.abspath(__file__))
else:
    default_directory = '/data/compile-inputs'

parser = argparse.ArgumentParser(
    description='Prints source code at a particular revision'
)
parser.add_argument('directory', nargs='?', default=default_directory,
                    help='Location of the index- and payload- files')
parser.add_argument('source_file_id', type=int,
                    help='ID in the source_files table')
parser.add_argument('master_event_id', type=int,
                    help='ID in the master_events table')


if __name__ == '__main__':
    # Bypass the argument parser for simplicity.
    if '--test' in sys.argv:
        base_directory = default_directory
        test()
    else:
        args = parser.parse_args()
        base_directory = args.directory
        main(args.source_file_id, args.master_event_id)