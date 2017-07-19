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

import os
import token
import tokenize
from io import BytesIO
from keyword import iskeyword
from pathlib import Path
from typing import (
    Any, AnyStr, Callable, IO, Iterable, Optional, Tuple, Union,
    overload,
)

import javalang  # type: ignore
from javalang.parser import JavaSyntaxError  # type: ignore
from javalang.tokenizer import LexerError  # type: ignore

from lexical_analysis import Lexeme, Location, Position, Token


here = Path(__file__).parent


class Java:
    """
    Defines the Java 8 programming language.
    """

    def tokenize(self, source: Union[str, bytes, IO[bytes]]) -> Iterable[Token]:
        tokens = javalang.tokenizer.tokenize(source)
        for token in tokens:
            loc = Location.from_string(token.value,
                                       line=token.position[0],
                                       column=token.position[1])
            yield Token(name=type(token).__name__,
                        value=token.value,
                        start=loc.start, end=loc.end)

    def check_syntax(self, source: Union[str, bytes]) -> bool:
        try:
            javalang.parse.parse(source)
            return True
        except (JavaSyntaxError, LexerError):
            return False


RESERVED_WORDS = {
    'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
    'char', 'class', 'const', 'continue', 'default', 'do', 'double',
    'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto',
    'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long',
    'native', 'new', 'package', 'private', 'protected', 'public', 'return',
    'short', 'static', 'strictfp', 'super', 'switch', 'synchronized',
    'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile',
    'while', 'abstract', 'default', 'final', 'native', 'private',
    'protected', 'public', 'static', 'strictfp', 'synchronized',
    'transient', 'volatile', 'boolean', 'byte', 'char', 'double', 'float',
    'int', 'long', 'short', 'true', 'false', 'null'
}
SYMBOLS = {
    '>>>=', '>>=', '<<=',  '%=', '^=', '|=', '&=', '/=',
    '*=', '-=', '+=', '<<', '--', '++', '||', '&&', '!=',
    '>=', '<=', '==', '%', '^', '|', '&', '/', '*', '-',
    '+', ':', '?', '~', '!', '<', '>', '=', '...', '->', '::',
    '(', ')', '{', '}', '[', ']', ';', ',', '.', '@'
}
CLOSED_CLASSES = {
    'Keyword', 'Modifier', 'BasicType', 'Boolean', 'Null',
    'Separator', 'Operator', 'Annotation', 'EndOfInput'
}

INTEGER_LITERALS = {
    'Integer',
    'DecimalInteger', 'OctalInteger', 'BinaryInteger', 'HexInteger',
}
FLOATING_POINT_LITERALS = {
    'FloatingPoint',
    'DecimalFloatingPoint', 'HexFloatingPoint',
}
STRING_LITERALS = {
    'Character', 'String',
}
OPEN_CLASSES = (
    INTEGER_LITERALS | FLOATING_POINT_LITERALS | STRING_LITERALS |
    {'Identifier'}
)


def java2sensibility(lex: Lexeme) -> str:
    # > Except for comments (§3.7), identifiers, and the contents of character
    # > and string literals (§3.10.4, §3.10.5), all input elements (§3.5) in a
    # > program are formed only from ASCII characters (or Unicode escapes (§3.3)
    # > which result in ASCII characters).
    # https://docs.oracle.com/javase/specs/jls/se7/html/jls-3.html
    if lex.name == 'EndOfInput':
        return '</s>'
    if lex.name in CLOSED_CLASSES:
        assert lex.value in RESERVED_WORDS | SYMBOLS
        return lex.value
    else:
        assert lex.name in OPEN_CLASSES
        if lex.name in INTEGER_LITERALS | FLOATING_POINT_LITERALS:
            return '<NUMBER>'
        elif lex.name in STRING_LITERALS:
            return '<STRING>'
        else:
            assert lex.name == 'Identifier'
            return '<IDENTIFIER>'


java = Java()
