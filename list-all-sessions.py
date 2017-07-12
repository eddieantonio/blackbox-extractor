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


import argparse
import datetime
from contextlib import closing

import sys
from blackbox_connection import mysql_connection


def to_date(string):
    return datetime.date(*(int(s) for s in string.split('-')))


parser = argparse.ArgumentParser(description='List session IDs')
parser.add_argument('until', type=to_date,
                    help="Date to stop collecting sessions in ISO 8601 format")

if __name__ == '__main__':
    args = parser.parse_args()
    with mysql_connection() as cnx:
        with closing(cnx.cursor()) as cursor:
            cursor.execute('''
                SELECT session_id
                  FROM master_events
                 WHERE event_type = 'CompileEvent'
                   AND created_at < DATE(%s)
            ''', (args.until,))
            for session_id, in cursor:
                print(session_id)
