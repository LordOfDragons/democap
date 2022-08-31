# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2022 DragonDreams (info@dragondreams.ch)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""@package Drag[en]gine Network Library Python Module."""

from ..protocol import ValueTypes
from ..message.reader import MessageReader
from ..message.writer import MessageWriter
from .value import Value


class ValueData(Value):

    """Data network state value."""

    def __init__(self: 'ValueData') -> None:
        """Create data value."""
        Value.__init__(self,  Value.Type.DATA, ValueTypes.DATA)

        self._value = bytes()
        self._last_value = self._value

    @property
    def value(self: 'ValueData') -> bytes:
        """Data.

        Return:
        bytes: Data.

        """
        return self._value

    @value.setter
    def value(self: 'ValueData', value: bytes) -> None:
        """Set Data.

        Parameters:
        value (bytes): Data.

        """

        if value is None:
            raise Exception("value is None")
        self._value = value
        self._value_changed()

    def read(self: 'ValueData', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        length = reader.read_ushort()
        self._value = reader.read(length)
        self._last_value = self._value

    def write(self: 'ValueData', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        length = len(self._value)
        writer.write_ushort(length)
        writer.write(self._value,  0, length)

    def update_value(self: 'ValueData', force: bool) -> bool:
        """Update value.

        Returns true if value needs to by synchronized otherwise false if
        not changed enough.

        Parameters:
        force (bool): Force updating value even if not changed.

        Return:
        bool: True if value change or force is True.

        """
        if not force and self._value == self._last_value:
            return False
        else:
            self._last_value = self._value
            return True
