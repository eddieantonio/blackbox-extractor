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

import sys
from contextlib import closing
from collections import namedtuple

from blackbox_connection import mysql_connection


Result = namedtuple('Result', 'master_event_id source_file_id success')


def find_pairs_in_session(session_id):
    with closing(cnx.cursor(buffered=True)) as cursor:
        cursor.execute('''
            SELECT master_events.id, source_file_id, success
              FROM master_events
                JOIN compile_events ON event_id = compile_events.id
                JOIN compile_inputs ON event_id = compile_event_id
             WHERE event_type = 'CompileEvent'
               AND session_id = %s
             ORDER BY sequence_num ASC
        ''', (session_id,))

        for pair in yield_pairs(tuple(Result(*row) for row in cursor)):
            yield pair


def yield_pairs(events):
    """
    Yield pairs of compile events where the preceeding one failed,
    but the next one succeeded.

    NOTE: You must still check BOTH for syntax errors, as the error maybe an
    issue with the classpath.
    """
    for a, b in zip(events, events[1:]):
        if a.source_file_id == b.source_file_id and not a.success and b.success:
            yield a.source_file_id, a.master_event_id, b.master_event_id


def sessions():
    for line in sys.stdin.readlines():
        line = line.strip()
        if line == '':
            continue
        yield int(line)


if __name__ == '__main__':
    with mysql_connection() as cnx:
        for session_id in sessions():
            # Prints source file, and TWO master_events IDs.
            for source_file, before, after in find_pairs_in_session(session_id):
                print('%d,%d,%d' % (source_file, before, after))
