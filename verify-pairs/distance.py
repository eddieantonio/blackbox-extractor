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
Determines the Levenshtein distance between two source files.
"""

import sqlite3
from typing import Iterable, Iterator, NewType, Optional, Tuple, cast

from Levenshtein import distance, editops  # type: ignore

# Use tqdm only if it's installed.
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    def tqdm(it, *_args, **_kwargs):
        yield from it

from java import java, java2sensibility
from lexical_analysis import Lexeme
from vocabulary import vocabulary, Vind
from mistakes import Mistakes, Mistake
from mistakes import Edit, EditType, Insertion, Deletion, Substitution


# Supplementary Private Use Area B
PUA_B_START = 0x100000


def to_edit_type(name: str) -> EditType:
    """
    Convert a string returned from Levenshtein.editops into a constant.
    """
    return {
        'replace': Substitution,
        'insert': Insertion,
        'delete': Deletion
    }[name]


def tokens2seq(tokens: Iterable[Lexeme],
               to_index=vocabulary.to_index,
               to_entry=java2sensibility) -> str:
    """
    Converts a sequence of tokens into an encoded string, that preserves
    distinctness between tokens. This string can be operated by the
    Levenshtein module.
    """
    # Injective maps of each vocabulary entry to a codepoint in the private
    # use area.
    # distance() works on codepoints, so this effectively makes distance()
    # work on token classes.
    return ''.join(
        chr(PUA_B_START + to_index(to_entry(token)))
        for token in tokens
    )


def tokenwise_distance(file_a: bytes, file_b: bytes) -> int:
    """
    Calculates the token-wise Levenshtein distance between two source files.
    """
    seq_a = tokens2seq(java.tokenize(file_a))
    seq_b = tokens2seq(java.tokenize(file_b))
    # TODO: use editops as a post-processing step!
    return distance(seq_a, seq_b)


class FixEvent:
    """
    A fix event is a collection of the edit that converts a file from good
    syntax to syntax error (the edit); from bad syntax to good syntax (the
    fix); and the line number of the token affected.
    """
    def __init__(self, edit: Edit, fix: Edit, line_no: int) -> None:
        self.edit = edit
        self.fix = fix
        self.line_no = line_no


def determine_edit(file_a: bytes, file_b: bytes) -> Edit:
    return determine_fix_event(file_a, file_b).edit


def determine_fix_event(file_a: bytes, file_b: bytes) -> FixEvent:
    """
    For two source files with Levenshtein distance of one, this returns the
    edit that converts the first file into the second file.
    """
    src = tokens2seq(java.tokenize(file_a))
    dest = tokens2seq(java.tokenize(file_b))
    ops = editops(src, dest)
    # This only works for files with one edit!
    assert len(ops) == 1

    # Decode editop's format.
    (type_name, src_pos, dest_pos), = ops
    edit_type = to_edit_type(type_name)
    new_token = None if edit_type is Deletion else from_pua(dest[dest_pos])
    edit = Edit(edit_type, dest_pos, new_token)

    return FixEvent(edit, edit, 0)


def index_of(token: str) -> Vind:
    """
    Given a token in the vocabulary, returns its vocabulary index.
    """
    return vocabulary.to_index(token)


def from_pua(char: str) -> Vind:
    """
    Undoes the injective mapping between vocabulary IDs and Private Use Area
    code poiunts.
    """
    assert ord(char) >= 0x100000
    return cast(Vind, ord(char) & 0xFFFF)


def test() -> None:
    assert 1 == tokenwise_distance(b'class Hello {',    b'class Hello {}')
    assert 1 == tokenwise_distance(b'class Hello {}',   b'class Hello }')
    assert 1 == tokenwise_distance(b'enum Hello {}',    b'class Hello {}')
    assert 0 == tokenwise_distance(b'class Hello {}',   b'class Hello {}')

    assert 2 >= tokenwise_distance(b'enum Hello {}',    b'class Hello {')


def test_extra() -> None:
    # Regression: Lexer should be able to handle const and goto keywords,
    # even though Java does not use them.
    # https://docs.oracle.com/javase/tutorial/java/nutsandbolts/_keywords.html
    assert 1 == tokenwise_distance(b'const int hello;', b'final int hello;')
    assert 1 == tokenwise_distance(b'goto label;', b'int label;')


def _test_get_source() -> None:
    m = Mistakes(sqlite3.connect('java-mistakes.sqlite3'))
    mistake = next(iter(m))
    assert 0 < tokenwise_distance(mistake.before, mistake.after)


def test_get_edit() -> None:
    ins = determine_edit(b'class Hello {',    b'class Hello {}')
    assert ins.type is Insertion
    assert ins.new_token == index_of('}')
    assert ins.position == 3

    delt = determine_edit(b'class Hello {{}',   b'class Hello {}')
    assert delt.type is Deletion
    assert delt.new_token is None
    assert delt.position in {2, 3}  # Can be either curly brace

    sub = determine_edit(b'goto label;', b'int label;')
    assert sub.type is Substitution
    assert sub.position == 0
    assert sub.new_token == index_of('int')


if __name__ == '__main__':
    conn = sqlite3.connect('java-mistakes.sqlite3')
    # HACK! Make writes super speedy by disregarding durability.
    conn.execute('PRAGMA synchronous = OFF')
    mistakes = Mistakes(conn)
    for mistake in tqdm(mistakes):
        dist = tokenwise_distance(mistake.before, mistake.after)
        mistakes.insert_distance(mistake, dist)
