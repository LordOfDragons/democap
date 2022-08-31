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

from ..message.reader import MessageReader
from ..message.writer import MessageWriter
from ..math.vector2 import Vector2
from ..math.half_float import HalfFloat
from .value import Value
from .value_float import ValueFloat


class ValueVector2(Value):

    """2 component float vector value."""

    def __init__(self: 'ValueVector2',
                 value_format: 'ValueFloat.Format') -> None:
        """Create value.

        Parameters:
        format (ValueFloat.Format): Format of value.

        """
        Value.__init__(self, Value.Type.VECTOR2,
                       ValueFloat._map_value_type[value_format])

        self._format = value_format
        self._value = Vector2()
        self._last_value = self._value

    @property
    def value(self: 'ValueVector2') -> Vector2:
        """Value.

        Return:
        Vector2: Value.

        """
        return self._value

    @value.setter
    def value(self: 'ValueVector2', value: Vector2) -> None:
        """Set value.

        Parameters:
        value (Vector2): Value.

        """
        self._value = value
        self._value_changed()

    def read(self: 'ValueVector2', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        if self._format == ValueFloat.Format.FLOAT16:
            x = HalfFloat.half_to_float(reader.read_ushort())
            y = HalfFloat.half_to_float(reader.read_ushort())
        elif self._format == ValueFloat.Format.FLOAT32:
            x = reader.read_float()
            y = reader.read_float()
        elif self._format == ValueFloat.Format.FLOAT64:
            x = reader.read_double()
            y = reader.read_double()
        self._last_value = Vector2(x, y)
        self._value = self._last_value

    def write(self: 'ValueVector2', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        if self._format == ValueFloat.Format.FLOAT16:
            writer.write_ushort(HalfFloat.float_to_half(self._value.x))
            writer.write_ushort(HalfFloat.float_to_half(self._value.y))
        elif self._format == ValueFloat.Format.FLOAT32:
            writer.write_float(self._value.x)
            writer.write_float(self._value.y)
        elif self._format == ValueFloat.Format.FLOAT64:
            writer.write_double(self._value.x)
            writer.write_double(self._value.y)

    def update_value(self: 'ValueVector2', force: bool) -> bool:
        """Update value.

        Returns true if value needs to by synchronized otherwise false if
        not changed enough.

        Parameters:
        force (bool): Force updating value even if not changed.

        Return:
        bool: True if value change or force is True.

        """
        if not force and self._value.equals(self._last_value, self._precision):
            return False
        else:
            self._last_value = self._value
            return True
