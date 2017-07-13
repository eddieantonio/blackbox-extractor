#!/usr/bin/env python3
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

import logging
import sqlite3
import sys
from typing import Iterable, Tuple, NewType

import requests

from java import java

SFID = NewType('SFID', int)
MEID = NewType('MEID', int)
Revision = Tuple[SFID, MEID]


SCHEMA = """
-- Insert "valid" mistakes here.
CREATE TABLE IF NOT EXISTS mistake (
    source_file_id  INT,
    master_event_id INT,
    before          BLOB,
    after           BLOB,
    PRIMARY KEY (source_file_id, master_event_id)
);
"""


class Pair:
    __slots__ = 'source_file_id', 'before_id', 'after_id'
    def __init__(self, sfid: SFID, before: MEID, after: MEID) -> None:
        self.source_file_id = sfid
        self.before_id = before
        self.after_id = after

    @property
    def before(self) -> Revision:
        return self.source_file_id, self.before_id

    @property
    def after(self) -> Revision:
        return self.source_file_id, self.after_id

    @property
    def key(self) -> Revision:
        return self.before

    def __repr__(self) -> str:
        return "<sfid={:d} before={:d} after={:d}>".format(
            self.source_file_id, self.before_id, self.after_id
        )


class Mistakes:
    """
    Stores mistakes in a database.
    """
    def __init__(self) -> None:
        self.conn = sqlite3.connect("java-mistakes.sqlite3")
        self.conn.executescript(SCHEMA)
        self.logger = logging.getLogger(type(self).__name__)

    def pair_exists(self, pair: Pair) -> bool:
        """
        Return True if the pair was already found in the database.
        """
        cursor = self.conn.execute('''
            SELECT COUNT(*)
              FROM mistake
             WHERE source_file_id = ? AND master_event_id = ?
        ''', pair.key)
        answer, = cursor.fetchone()
        return answer > 0

    def try_pair(self, pair: Pair) -> None:
        """
        Try to download and verify a before/after pair.
        """
        if self.pair_exists(pair):
            self.logger.info("Pair exists: %r", pair)
            return

        try:
            source_before = fetch_source(pair.before)
            source_after = fetch_source(pair.after)
        except requests.exceptions.HTTPError:
            self.logger.warn("Not found: %r", pair)
            return

        self.logger.info("Checking %r", pair)
        if good_pair(source_before, source_after):
            self.logger.info("Inserting: %r", pair)
            self.insert(pair, source_before, source_after)

    def insert(self, pair: Pair, before: bytes, after: bytes) -> None:
        """
        Insert the before/after source code into the database.
        """
        with self.conn:
            sfid, meid = pair.key  # type: Tuple[SFID, MEID]
            self.conn.execute("""
                INSERT INTO mistake
                (source_file_id, master_event_id, before, after)
                VALUES (?, ?, ?, ?)
            """, (sfid, meid, before, after))


def fetch_source(revision: Revision) -> bytes:
    """
    Get a source code file at a particular revision.
    """
    sfid, meid = revision  # type: Tuple[SFID, MEID]
    r = requests.get('http://localhost:8080/',
                     params=dict(sfid=sfid, meid=meid))
    r.raise_for_status()
    return r.content


def good_pair(before: bytes, after: bytes) -> bool:
    """
    Return True if a pair of source files makes for a valid example.
    """
    try:
        return _good_pair(before, after)
    except Exception:
        # Javalang has bugs and will throw on some valid inputs, so just
        # reject the pair if this is the case.
        return False


def _good_pair(before: bytes, after: bytes) -> bool:
    logger = logging.getLogger('good_pair')
    if java.check_syntax(before) is True:
        logger.info("Rejecting: before has valid syntax")
        return False

    if java.check_syntax(after) is False:
        logger.info("Rejecting: after has invalid syntax")
        return False

    tokens_before = count(java.tokenize(before))
    tokens_after = count(java.tokenize(after))

    if tokens_before - tokens_after not in {-1, 0, 1}:
        logger.info("Rejecting: difference too large")
        return False

    return True


def count(it: Iterable) -> int:
    i = 0
    for _ in it:
        i += 1
    return i


def pairs() -> Iterable[Pair]:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            sfid, before_id, after_id = line.split()
            yield Pair(SFID(int(sfid)), MEID(int(before_id)), MEID(int(after_id)))
        except ValueError:
            logging.warn("Invalid pair: %r", line)
            continue


def test():
    bad_source = """
    class Hello {
    """
    good_source = """
    class Hello {
    }
    """

    assert good_pair(bad_source, good_source)
    assert not good_pair(bad_source, bad_source)
    assert not good_pair(good_source, good_source)
    assert not good_pair(good_source, bad_source)
    good_source_too_different = """
    class Hello {
        public static void main (String args[]) {
        }
    }
    """
    assert java.check_syntax(good_source_too_different)
    assert not good_pair(bad_source, good_source_too_different)

    # Try insertion.
    bad_source = """
    class Hello {
    }}
    """
    assert good_pair(bad_source, good_source)
    assert not good_pair(bad_source, bad_source)
    assert not good_pair(good_source, good_source)
    assert not good_pair(good_source, bad_source)

    # Try substitution.
    bad_source = """
    class Hello {
    ]
    """
    assert good_pair(bad_source, good_source)
    assert not good_pair(bad_source, bad_source)
    assert not good_pair(good_source, good_source)
    assert not good_pair(good_source, bad_source)


def main():
    mistakes = Mistakes()
    for pair in pairs():
        mistakes.try_pair(pair)


if __name__ == '__main__':
    if '--test' in sys.argv[1:]:
        test()
    else:
        logging.basicConfig(level=logging.INFO)
        main()
