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
Reads the index files with the format described in Section 9 of The BlueJ
Blackbox Data Collection Researchers' Handbook, Section 9.1.
"""

import struct
from collections import namedtuple
from contextlib import closing
from os import SEEK_END


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
    """
    Extract ALL the data from an index entry.
    """
    @classmethod
    def from_file(cls, index_file):
        """
        Extracts one entry from the index file.
        """
        return cls(*index_fmt.unpack(index_file.read(index_fmt.size)))


    @classmethod
    def entries_from_file(cls, index_file):
        """
        Yields all from an opened index file object. The file object MUST be
        opened with in a binary reading mode (e.g., "rb").
        """
        # Deternmine the size of the file by seeking to the end of it.
        index_file.seek(0, SEEK_END)
        file_size = index_file.tell()
        # There must be an whole number of structs in the file.
        assert file_size % index_fmt.size == 0
        # Return to the beginning of the file.
        index_file.seek(0)
        while True:
            try:
                yield IndexEntry.from_file(index_file)
            except struct.error:
                # We must have reached the end of the file.
                assert index_file.tell() == file_size
                break

    @property
    def key(self):
        return self.source_file_id, self.master_event_id


def date_of(master_event_id, cnx):
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
