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
from ..math.half_float import HalfFloat
from .value import Value
from enum import IntEnum, auto


class ValueFloat(Value):

    """Floating network state value."""

    class Format(IntEnum):

        """Value type."""

        FLOAT16 = auto()
        """16-Bit float."""

        FLOAT32 = auto()
        """32-Bit float."""

        FLOAT64 = auto()
        """64-Bit float."""

    _map_value_type = {Format.FLOAT16: ValueTypes.FLOAT16,
                       Format.FLOAT32: ValueTypes.FLOAT32,
                       Format.FLOAT64: ValueTypes.FLOAT64}

    def __init__(self: 'ValueFloat',
                 value_format: 'ValueFloat.Format') -> None:
        """Create floating value.

        Parameters:
        format (ValueFloat.Format): Format of value.

        """
        Value.__init__(self, Value.Type.FLOAT,
                       ValueFloat._map_value_type[value_format])

        self._format = value_format
        self._value = 0.0
        self._last_value = 0.0
        self._precision = 1e-15
        self._min_precision = 1e-15

    @property
    def value(self: 'ValueFloat') -> float:
        """Value.

        Return:
        float: Value.

        """
        return self._value

    @value.setter
    def value(self: 'ValueFloat', value: float) -> None:
        """Set value.

        Parameters:
        value (float): Value.

        """
        self._value = value
        self._value_changed()

    @property
    def precision(self: 'ValueFloat') -> float:
        """Precision.

        Return:
        float: Precsion.

        """
        return self._precision

    @precision.setter
    def precision(self: 'ValueFloat', precision: float) -> None:
        """Set precision.

        Parameters:
        precision (float): Precsion.

        """
        self._precision = max(precision, self._min_precision)
        self._value_changed()

    def read(self: 'ValueFloat', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        if self._format == ValueFloat.Format.FLOAT16:
            self._last_value = HalfFloat.half_to_float(reader.read_ushort())
        elif self._format == ValueFloat.Format.FLOAT32:
            self._last_value = reader.read_float()
        elif self._format == ValueFloat.Format.FLOAT64:
            self._last_value = reader.read_double()
        self._value = self._last_value

    def write(self: 'ValueFloat', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        if self._format == ValueFloat.Format.FLOAT16:
            writer.write_ushort(HalfFloat.float_to_half(self._value))
        elif self._format == ValueFloat.Format.FLOAT32:
            writer.write_float(self._value)
        elif self._format == ValueFloat.Format.FLOAT64:
            writer.write_double(self._value)

    def update_value(self: 'ValueFloat', force: bool) -> bool:
        """Update value.

        Returns true if value needs to by synchronized otherwise false if
        not changed enough.

        Parameters:
        force (bool): Force updating value even if not changed.

        Return:
        bool: True if value change or force is True.

        """
        if not force and (abs(self._value - self._last_value)
                          <= self._precision):
            return False
        else:
            self._last_value = self._value
            return True
