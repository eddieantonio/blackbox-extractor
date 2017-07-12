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

import os
import traceback
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from collections import namedtuple
from urlparse import urlparse, parse_qs

from blackbox_connection import mysql_connection
from section_9 import IndexEntry, date_of

Entry = namedtuple('Entry', 'date offset size')


class BlackBoxError(Exception):
    """
    Generic BlackBox error.
    """


class BigIndex(object):
    def __init__(self, path):
        self._table = {}
        self._meid2date = {}
        self.path = path

    def __getitem__(self, key):
        # Returns the source for the given source file at the revision
        # specified by its master_events ID.
        source_file_id, master_event_id = key
        # Load the index if we've don't know about this meID.
        if not self.has_seen_master_event_id(master_event_id):
            self._add_to_table(self.date_of(master_event_id))
        # By now, the table MUST have the entry, or else something went wrong.
        entry = self._table[key]
        return self.get_source(entry)

    def get_source(self, entry):
        """
        Opens up the payload file to reveal the precious data inside.
        """
        filename = self.path_to('payload-' + entry.date)
        with open(filename, "rb") as payload_file:
            # Seek to the offset and read the datums.
            payload_file.seek(entry.offset)
            return payload_file.read(entry.size)

    def path_to(self, item):
        return os.path.join(self.path, item)

    def has_seen_master_event_id(self, meid):
        return meid in self._meid2date

    def date_of(self, master_event_id):
        """
        Cached version of date retreival for a master_events id.
        """
        if master_event_id not in self._meid2date:
            self._meid2date[master_event_id] = date_of(master_event_id, cnx)
        return self._meid2date[master_event_id]

    def _add_to_table(self, datestr):
        """
        Once a date is requested for the first time, the index for the entire
        date is loaded.
        """
        table = self._table
        meid2date = self._meid2date
        filename = self.path_to('index-' + datestr)
        with open(filename, "rb") as index_file:
            for entry in IndexEntry.entries_from_file(index_file):
                table[entry.key] = Entry(offset=entry.start,
                                         size=entry.length,
                                         date=datestr)
                meid2date[entry.master_event_id] = datestr


class BlackBoxRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        "Get a source code file."
        url = urlparse(self.path)
        # Must be requested at root.
        if url.path != '/':
            return self.send_error(404)

        # Figure out arguments.
        args = parse_qs(url.query)
        if 'sfid' not in args or 'meid' not in args:
            return self.send_error(400, 'missing meid or sfid')
        try:
            source_file_id = int(args['sfid'][-1])
            master_event_id = int(args['meid'][-1])
        except ValueError:
            return self.send_error(400)

        try:
            contents = index[(source_file_id, master_event_id)]
        except BlackBoxError:
            return self.send_error(404)
        except:
            self.log_error(traceback.format_exc())
            return self.send_error(500)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(contents))
        self.end_headers()

        self.wfile.write(contents)


def run(path):
    "Run the HTTP server forever."
    global index
    index = BigIndex(path)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, BlackBoxRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    with mysql_connection() as cnx:
        run(os.path.abspath('.'))
