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
import sys
import token
from io import BytesIO
from keyword import iskeyword
from pathlib import Path
from typing import (
    Any, AnyStr, Callable, IO, Iterable, Optional, Tuple, Union,
    overload,
)

from lexical_analysis import Lexeme, Location, Position, Token

import javac_parser


class Java:
    """
    Defines the Java 8 programming language.
    """

    extensions = {'.java'}

    @property
    def java(self):
        """
        Lazily start up the Java server. This decreases the chances of things
        going horribly wrong when two seperate process initialize
        the Java language instance around the same time.
        """
        if not hasattr(self, '_java_server'):
            # Start the finicky server.
            self._java_server = javac_parser.Java()

        return self._java_server

    def tokenize(self, source: Union[str, bytes, IO[bytes]]) -> Iterable[Token]:
        tokens = self.java.lex(to_str(source))
        # Each token is a tuple with the following structure
        # (reproduced from javac_parser.py):
        #   1. Lexeme type
        #   2. Value (as it appears in the source file)
        #   3. A 2-tuple of start line, start column
        #   4. A 2-tuple of end line, end column
        #   5. A whitespace-free representation of the value
        for name, _raw_value, start, end, normalized in tokens:
            # Omit the EOF token, as it's only useful for the parser.
            if name == 'EOF':
                continue
            # Take the NORMALIZED value, as Java allows unicode escapes in
            # ARBITRARY tokens and then things get hairy here.
            yield Token(name=name, value=normalized,
                        start=Position(line=start[0], column=start[1]),
                        end=Position(line=end[0], column=end[1]))

    def check_syntax(self, source: Union[str, bytes]) -> bool:
        return self.java.get_num_parse_errors(to_str(source)) == 0

    def vocabularize_tokens(self, source: Iterable[Token]) -> Iterable[Tuple[Location, str]]:
        for token in source:
            yield token.location, java2sensibility(token)


# Big list of symbol names, derived from
# com.sun.tools.javac.parser.Tokens.TokenKind
RESERVED_WORDS_REPR = {
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

SYMBOLS_REPR = {
    "_", "->", "::", "(", ")", "{", "}", "[", "]", ";", ",", ".", "...", "=",
    ">", "<", "!", "~", "?", ":", "==", "<=", ">=", "!=", "&&", "||", "++",
    "--", "+", "-", "*", "/", "&", "|", "^", "%", "<<", ">>", ">>>", "+=",
    "-=", "*=", "/=", "&=", "|=", "^=", "%=", "<<=", ">>=", ">>>=", "@",
}

REPRESENTABLE_CLOSED_CLASSES = SYMBOLS_REPR | RESERVED_WORDS_REPR

NON_REPRESENTABLE_CLOSED_CLASSES = {
    'EOF', 'ERROR'
}

CLOSED_CLASSES = {
    # Keywords and other reserved words
    'ABSTRACT', 'ASSERT', 'BOOLEAN', 'BREAK', 'BYTE', 'CASE', 'CATCH',
    'CHAR', 'CLASS', 'CONST', 'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE',
    'ELSE', 'ENUM', 'EXTENDS', 'FINAL', 'FINALLY', 'FLOAT', 'FOR', 'GOTO',
    'IF', 'IMPLEMENTS', 'IMPORT', 'INSTANCEOF', 'INT', 'INTERFACE', 'LONG',
    'NATIVE', 'NEW', 'PACKAGE', 'PRIVATE', 'PROTECTED', 'PUBLIC', 'RETURN',
    'SHORT', 'STATIC', 'STRICTFP', 'SUPER', 'SWITCH', 'SYNCHRONIZED',
    'THIS', 'THROW', 'THROWS', 'TRANSIENT', 'TRY', 'VOID', 'VOLATILE',
    'WHILE', 'ABSTRACT', 'DEFAULT', 'FINAL', 'NATIVE', 'PRIVATE',
    'PROTECTED', 'PUBLIC', 'STATIC', 'STRICTFP', 'SYNCHRONIZED',
    'TRANSIENT', 'VOLATILE', 'BOOLEAN', 'BYTE', 'CHAR', 'DOUBLE', 'FLOAT',
    'INT', 'LONG', 'SHORT',
    # Reserved literals
    'TRUE', 'FALSE', 'NULL',

    # Symbols
    'UNDERSCORE', 'ARROW', 'COLCOL', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET', 'SEMI', 'COMMA', 'DOT', 'ELLIPSIS', 'EQ', 'GT',
    'LT', 'BANG', 'TILDE', 'QUES', 'COLON', 'EQEQ', 'LTEQ', 'GTEQ', 'BANGEQ',
    'AMPAMP', 'BARBAR', 'PLUSPLUS', 'SUBSUB', 'PLUS', 'SUB', 'STAR', 'SLASH',
    'AMP', 'BAR', 'CARET', 'PERCENT', 'LTLT', 'GTGT', 'GTGTGT', 'PLUSEQ',
    'SUBEQ', 'STAREQ', 'SLASHEQ', 'AMPEQ', 'BAREQ', 'CARETEQ', 'PERCENTEQ',
    'LTLTEQ', 'GTGTEQ', 'GTGTGTEQ', 'MONKEYS_AT',
}

NUMERIC_LITERALS = {
    'INTLITERAL', 'LONGLITERAL', 'FLOATLITERAL', 'DOUBLELITERAL', 'CHARLITERAL',
}
OPEN_CLASSES = {'IDENTIFIER', 'STRINGLITERAL'} | NUMERIC_LITERALS


def java2sensibility(lex: Lexeme) -> str:
    """
    Returns a simple string representation of the token. The string
    representation is guaranteed to not include any whitespace.

    Open classes and non-representable closed classes have a angle-bracket
    delimited name, e.g., <IDENTIFIER>, <STRING>, <ERROR>. Special case is
    EOF, which uses the NLP convention of </s> take to mean "end of sentence".

    Other closed classes are represented by their in-source value.
    """
    # > Except for comments (§3.7), identifiers, and the contents of character
    # > and string literals (§3.10.4, §3.10.5), all input elements (§3.5) in a
    # > program are formed only from ASCII characters (or Unicode escapes (§3.3)
    # > which result in ASCII characters).
    # https://docs.oracle.com/javase/specs/jls/se7/html/jls-3.html
    if lex.value in REPRESENTABLE_CLOSED_CLASSES:
        return lex.value
    elif lex.name in OPEN_CLASSES:
        if lex.name in NUMERIC_LITERALS:
            return f'<{lex.name}>'
        elif lex.name == 'STRINGLITERAL':
            return '<STRING>'
        else:
            assert lex.name == 'IDENTIFIER'
            return '<IDENTIFIER>'
    elif lex.name == 'EOF':
        return '</s>'
    elif lex.name == 'ERROR':
        return '<ERROR>'
    else:
        # When I forgot to account for a token.
        raise NotImplementedError(repr(lex))


def to_str(source: Union[str, bytes, IO[bytes]]) -> str:
    """
    Coerce an input format to a Unicode string.
    """
    if isinstance(source, str):
        return source
    elif isinstance(source, bytes):
        # XXX: Assume it's UTF-8 encoded!
        return source.decode('UTF-8')
    else:
        raise NotImplementedError


java = Java()
