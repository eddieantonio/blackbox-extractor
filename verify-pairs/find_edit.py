#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2017 Eddie Antonio Santos <easantos@ualberta.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Finds edits and inserts them into the database.
"""

import sqlite3
import logging

# Use tqdm only if it's installed.
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    def tqdm(it, *_args, **_kwargs):
        yield from it

from mistakes import Mistakes, Mistake
from mistakes import Edit, EditType, Insertion, Deletion, Substitution
from distance import determine_edit


if __name__ == '__main__':
    logger = logging.getLogger('find_edit')
    conn = sqlite3.connect('java-mistakes.sqlite3')
    # HACK! Make writes super speedy by disregarding durability.
    conn.execute('PRAGMA synchronous = OFF')
    mistakes = Mistakes(conn)
    for mistake in tqdm(mistakes.eligible_mistakes):
        try:
            edit = determine_edit(mistake.before, mistake.after)
        except:
            logger.exception('Error determining distance of %s', mistake)
        mistakes.insert_edit(mistake, edit)
