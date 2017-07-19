#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sqlite3
from typing import Iterable, Iterator, Tuple, NewType

from Levenshtein import distance  # type: ignore

from vocabulary import vocabulary
from lexical_analysis import Lexeme
from java import java, java2sensibility

SFID = NewType('SFID', int)
MEID = NewType('MEID', int)
Revision = Tuple[SFID, MEID]


# To work along side java-mistakes.sqlite3
SCHEMA = r"""
CREATE TABLE IF NOT EXISTS distance(
    source_file_id  INT,
    before_id       INT,
    levenshtein     INT,
    PRIMARY KEY (source_file_id, before_id)
);
"""


# Supplementary Private Use Area B
PUA_B_START = 0x100000


class Mistake:
    def __init__(self, sfid: SFID, meid: MEID, before: bytes, after: bytes) -> None:
        self.sfid = sfid
        self.meid = meid
        self.before = before
        self.after = after


# TODO: factor out with class from verify-pair?
class Mistakes(Iterable[Mistake]):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        #self.conn.executescript(SCHEMA)

    def __iter__(self) -> Iterator[Mistake]:
        query = '''SELECT source_file_id, before_id, before, after FROM mistake'''
        for row in self.conn.execute(query):
            yield Mistake(*row)


def tokens2seq(tokens: Iterable[Lexeme],
               to_index=vocabulary.to_index,
               to_entry=java2sensibility) -> str:
    """
    Converts a sequence of tokens into a special string
    """
    # Maps each vocabulary entry to a codepoint in the private use area.
    return ''.join(
        chr(PUA_B_START + to_index(to_entry(token)))
        for token in tokens
    )


def tokenwise_distance(file_a: bytes, file_b: bytes) -> int:
    seq_a = tokens2seq(java.tokenize(file_a))
    seq_b = tokens2seq(java.tokenize(file_b))
    # TODO: use editops as a post-processing step!
    return distance(seq_a, seq_b)


def test() -> None:
    assert 1 == tokenwise_distance(b'class Hello {',    b'class Hello {}')
    assert 1 == tokenwise_distance(b'class Hello {}',   b'class Hello }')
    assert 1 == tokenwise_distance(b'enum Hello {}',    b'class Hello {}')
    assert 0 == tokenwise_distance(b'class Hello {}',   b'class Hello {}')

    assert 2 >= tokenwise_distance(b'enum Hello {}',    b'class Hello {')


def test_get_source() -> None:
    m = Mistakes(sqlite3.connect('java-mistakes.sqlite3'))
    mistake = next(iter(m))
    assert 0 < tokenwise_distance(mistake.before, mistake.after)
