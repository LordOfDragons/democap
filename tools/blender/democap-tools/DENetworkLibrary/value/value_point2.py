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
from ..math.point2 import Point2
from .value import Value
from .value_int import ValueInt


class ValuePoint2(Value):

    """2 component integer vector value."""

    _map_value_type = {ValueInt.Format.SINT8: ValueTypes.POINT2S8,
                       ValueInt.Format.UINT8: ValueTypes.POINT2U8,
                       ValueInt.Format.SINT16: ValueTypes.POINT2S16,
                       ValueInt.Format.UINT16: ValueTypes.POINT2U16,
                       ValueInt.Format.SINT32: ValueTypes.POINT2S32,
                       ValueInt.Format.UINT32: ValueTypes.POINT2U32,
                       ValueInt.Format.SINT64: ValueTypes.POINT2S64,
                       ValueInt.Format.UINT64: ValueTypes.POINT2U64}

    def __init__(self: 'ValuePoint2',
                 value_format: 'ValueInt.Format') -> None:
        """Create integer value.

        Parameters:
        format (ValueInt.Format): Format of value.

        """
        Value.__init__(self, Value.Type.POINT2,
                       ValuePoint2._map_value_type[value_format])

        self._format = value_format
        self._value = Point2()
        self._last_value = self._value

    @property
    def value(self: 'ValuePoint2') -> Point2:
        """Value.

        Return:
        Point2: Value.

        """
        return self._value

    @value.setter
    def value(self: 'ValuePoint2', value: Point2) -> None:
        """Set value.

        Parameters:
        value (Point2): Value.

        """
        self._value = value
        self._value_changed()

    def read(self: 'ValuePoint2', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        if self._format == ValueInt.Format.SINT8:
            x = reader.read_char()
            y = reader.read_char()
        elif self._format == ValueInt.Format.UINT8:
            x = reader.read_byte()
            y = reader.read_byte()
        elif self._format == ValueInt.Format.SINT16:
            x = reader.read_short()
            y = reader.read_short()
        elif self._format == ValueInt.Format.UINT16:
            x = reader.read_ushort()
            y = reader.read_ushort()
        elif self._format == ValueInt.Format.SINT32:
            x = reader.read_int()
            y = reader.read_int()
        elif self._format == ValueInt.Format.UINT32:
            x = reader.read_uint()
            y = reader.read_uint()
        elif self._format == ValueInt.Format.SINT64:
            x = reader.read_long()
            y = reader.read_long()
        elif self._format == ValueInt.Format.UINT64:
            x = reader.read_ulong()
            y = reader.read_ulong()
        self._last_value = Point2(x, y)
        self._value = self._last_value

    def write(self: 'ValuePoint2', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        if self._format == ValueInt.Format.SINT8:
            writer.write_char(self._value.x)
            writer.write_char(self._value.y)
        elif self._format == ValueInt.Format.UINT8:
            writer.write_byte(self._value.x)
            writer.write_byte(self._value.y)
        elif self._format == ValueInt.Format.SINT16:
            writer.write_short(self._value.x)
            writer.write_short(self._value.y)
        elif self._format == ValueInt.Format.UINT16:
            writer.write_ushort(self._value.x)
            writer.write_ushort(self._value.y)
        elif self._format == ValueInt.Format.SINT32:
            writer.write_int(self._value.x)
            writer.write_int(self._value.y)
        elif self._format == ValueInt.Format.UINT32:
            writer.write_uint(self._value.x)
            writer.write_uint(self._value.y)
        elif self._format == ValueInt.Format.SINT64:
            writer.write_long(self._value.x)
            writer.write_long(self._value.y)
        elif self._format == ValueInt.Format.UINT64:
            writer.write_ulong(self._value.x)
            writer.write_ulong(self._value.y)

    def update_value(self: 'ValuePoint2', force: bool) -> bool:
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
