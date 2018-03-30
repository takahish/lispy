# Copyright 2018 Takahiro Ishikawa. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import re
import io
from clispy.symbol import *


class _InPort(object):
    """An input port. Retains a line of chars.
    """
    __tokenizer = r"""\s*(,@|#'|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""

    def __init__(self, file):
        """Inits _InPort with file pointer.
        """
        self.file = file
        self.line = ''

    def next_token(self):
        """Return the next token, reading new text into line buffer if needed.
        """
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return EOF_OBJECT
            token, self.line = re.match(_InPort.__tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

def _convert_to_atom(token):
    """Numbers become numbers; t and nil are booleans; "..." string; otherwise Symbol.

    Args:
        token: token extracted from inport.

    Returns:
        Int, Float or Symbol.
    """
    if token == 't':
        return True
    elif token == 'nil':
        return False
    elif token[0] == '"':
        encoded_str = token[1:-1].encode('unicode_escape')
        return encoded_str.decode('unicode_escape')

    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
            except ValueError:
                return symbol_table[token]

def _read_ahead(token, inport):
    """Helper function of read.

    Args:
        token: token extracted from inport.
        inport: _InPort object.

    Returns:
        Quote expression or atom.
    """
    if '(' == token:
        L = []
        while True:
            token = inport.next_token()
            if token == ')':
                return L
            else:
                L.append(_read_ahead(token, inport))
    elif ')' == token:
        raise SyntaxError('unexpected )')
    elif token in QUOTES:
        return [QUOTES[token], _read(inport)]
    elif token is EOF_OBJECT:
        raise SyntaxError('unexpected EOF in list')
    else:
        return _convert_to_atom(token)

def _read(inport):
    """Read scheme expression from an inport port.

    Args:
        inport: _InPort object.

    Returns:
        Quote expression or atom.
    """
    # body of _read
    token1 = inport.next_token()
    return EOF_OBJECT if token1 is EOF_OBJECT else _read_ahead(token1, inport)

def parse(inport):
    """Parse a program: read and expand/error-check it.

    Args:
        inport: _InPort object or string.

    Return:
        Quote expression or atom.
    """
    if isinstance(inport, str):
        inport = _InPort(io.StringIO(inport))
    return _read(inport)

def _readchar(inport):
    """Read the next character from an input port.

    Args:
        inport: _InPort object.

    Returns:
        Character.
    """
    if inport.line != '':
        char, inport.line = inport.line[0], inport.line[1:]
        return char
    else:
        return inport.file.read(1) or EOF_OBJECT
