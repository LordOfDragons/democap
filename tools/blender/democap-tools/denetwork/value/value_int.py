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
from enum import IntEnum, auto


class ValueInt(Value):

    """integer network state value."""

    class Format(IntEnum):

        """Value type."""

        SINT8 = auto()
        """8-Bit signed integer."""

        UINT8 = auto()
        """8-Bit unsigned integer."""

        SINT16 = auto()
        """16-Bit signed integer."""

        UINT16 = auto()
        """16-Bit unsigned integer."""

        SINT32 = auto()
        """32-Bit signed integer."""

        UINT32 = auto()
        """32-Bit unsigned integer."""

        SINT64 = auto()
        """64-Bit signed integer."""

        UINT64 = auto()
        """64-Bit unsigned integer."""

    _map_value_type = {Format.SINT8: ValueTypes.SINT8,
                       Format.UINT8: ValueTypes.UINT8,
                       Format.SINT16: ValueTypes.SINT16,
                       Format.UINT16: ValueTypes.UINT16,
                       Format.SINT32: ValueTypes.SINT32,
                       Format.UINT32: ValueTypes.UINT32,
                       Format.SINT64: ValueTypes.SINT64,
                       Format.UINT64: ValueTypes.UINT64}

    def __init__(self: 'ValueInt',
                 value_format: 'ValueInt.Format') -> None:
        """Create integer value.

        Parameters:
        format (ValueInt.Format): Format of value.

        """
        Value.__init__(self, type, ValueInt._map_value_type[value_format])

        self._format = value_format
        self._value = 0
        self._last_value = 0

    @property
    def value(self: 'ValueInt') -> int:
        """Value.

        Return:
        int: Value.

        """
        return self._value

    @value.setter
    def value(self: 'ValueInt', value: int) -> None:
        """Set value.

        Parameters:
        value (int): Value.

        """
        self._value = value
        self._value_changed()

    def read(self: 'ValueInt', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        if self._format == ValueInt.Format.SINT8:
            self._last_value = reader.read_char()
        elif self._format == ValueInt.Format.UINT8:
            self._last_value = reader.read_byte()
        elif self._format == ValueInt.Format.SINT16:
            self._last_value = reader.read_short()
        elif self._format == ValueInt.Format.UINT16:
            self._last_value = reader.read_ushort()
        elif self._format == ValueInt.Format.SINT32:
            self._last_value = reader.read_int()
        elif self._format == ValueInt.Format.UINT32:
            self._last_value = reader.read_uint()
        elif self._format == ValueInt.Format.SINT64:
            self._last_value = reader.read_long()
        elif self._format == ValueInt.Format.UINT64:
            self._last_value = reader.read_ulong()
        self._value = self._last_value

    def write(self: 'ValueInt', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        if self._format == ValueInt.Format.SINT8:
            writer.write_char(self._value)
        elif self._format == ValueInt.Format.UINT8:
            writer.write_byte(self._value)
        elif self._format == ValueInt.Format.SINT16:
            writer.write_short(self._value)
        elif self._format == ValueInt.Format.UINT16:
            writer.write_ushort(self._value)
        elif self._format == ValueInt.Format.SINT32:
            writer.write_int(self._value)
        elif self._format == ValueInt.Format.UINT32:
            writer.write_uint(self._value)
        elif self._format == ValueInt.Format.SINT64:
            writer.write_long(self._value)
        elif self._format == ValueInt.Format.UINT64:
            writer.write_ulong(self._value)

    def update_value(self: 'ValueInt', force: bool) -> bool:
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
