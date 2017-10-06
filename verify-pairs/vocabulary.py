#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2016 Eddie Antonio Santos <easantos@ualberta.ca>
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

import warnings
from typing import Any, Dict, Iterable, List, NewType, Sequence, Sized, Tuple
from typing import cast

__all__ = 'Vocabulary', 'Entry', 'Vind', 'vocabulary'

# A vocabulary index that gets in your face.
Vind = NewType('Vind', int)
# A vocabulary entry
Entry = NewType('Entry', str)

UNK_TOKEN = '<UNK>'
START_TOKEN = '<s>'
END_TOKEN = '</s>'


class Vocabulary(Sized):
    """
    One-to-one mapping of vocabulary strings to vocabulary indices (Vinds).

    """
    SPECIAL_ENTRIES = (UNK_TOKEN, START_TOKEN, END_TOKEN)

    def __init__(self, entries: Iterable[str]) -> None:
        self._index2text = cast(Sequence[Entry],
                                self.SPECIAL_ENTRIES + tuple(entries))
        self._text2index = {
            text: Vind(index) for index, text in enumerate(self._index2text)
        }  # type: Dict[str, Vind]

        assert len(self._index2text) == len(set(self._index2text)), (
            'Duplicate entries in vocabulary'
        )

    def entries(self) -> Iterable[Entry]:
        """
        Yields all "true" entries of the vocabulary (all minus the special
        entries).
        """
        for ind in range(len(self.SPECIAL_ENTRIES), len(self)):
            yield self._index2text[cast(Vind, ind)]

    def to_text(self, index: Vind) -> str:
        return self._index2text[index]

    def to_index(self, text: str) -> Vind:
        try:
            return self._text2index[text]
        except KeyError:
            # Unks **SHOULD** only apply to error tokens...
            if text != '<ERROR>':
                warnings.warn(f'Token converted to <unk>: {text!r}')
            return self.unk_token_index

    def __len__(self) -> int:
        return len(self._index2text)

    def __getitem__(self, idx: Vind) -> Entry:
        return self._index2text[idx]

    def to_lexeme(self, idx: Vind) -> None:
        # TODO: return a lexeme
        raise NotImplementedError

    unk_token_index = Vind(0)
    start_token_index = Vind(1)
    end_token_index = Vind(2)
    unk_token = UNK_TOKEN
    start_token = START_TOKEN
    end_token = END_TOKEN


vocabulary = Vocabulary(["^", "^=", "~", "<", "<<", "<<=", "<=", "=", "==",
                         ">", ">=", ">>", ">>=", ">>>", ">>>=", "|", "|=",
                         "||", "-", "-=", "->", "--", ",", ";", ":", "::", "!",
                         "!=", "?", "/", "/=", ".", "...", "(", ")", "[", "]",
                         "{", "}", "@", "*", "*=", "&", "&=", "&&", "%", "%=",
                         "+", "+=", "++", "abstract", "assert", "boolean",
                         "break", "byte", "case", "catch", "char",
                         "<CHARLITERAL>", "class", "const", "continue",
                         "default", "do", "double", "<DOUBLELITERAL>", "else",
                         "enum", "extends", "false", "final", "finally",
                         "float", "<FLOATLITERAL>", "for", "goto",
                         "<IDENTIFIER>", "if", "implements", "import",
                         "instanceof", "int", "interface", "<INTLITERAL>",
                         "long", "<LONGLITERAL>", "native", "new", "null",
                         "package", "private", "protected", "public", "return",
                         "short", "static", "strictfp", "<STRING>", "super",
                         "switch", "synchronized", "this", "throw", "throws",
                         "transient", "true", "try", "void", "volatile",
                         "while"])
