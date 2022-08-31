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
from abc import ABC, abstractmethod
from enum import IntEnum, auto


class Value(ABC):

    """Network state value."""

    class Type(IntEnum):

        """Value type."""

        INTEGER = auto()
        """Integer."""

        FLOAT = auto()
        """Floating point."""

        STRING = auto()
        """String of arbitrary length."""

        DATA = auto()
        """Byte data of arbitrary length."""

        POINT2 = auto()
        """2 component integer point."""

        POINT3 = auto()
        """3 component integer point."""

        VECTOR2 = auto()
        """2 component float vector."""

        VECTOR3 = auto()
        """3 component float vector."""

        QUATERNION = auto()
        """4 component float quaternoion."""

    def __init__(self: 'Value', value_type: 'Value.Type',
                 data_type: ValueTypes) -> None:
        """Create Value.

        Parameters:
        value_type (Value.Type): Type of value.
        data_type (ValueTypes): Data type.

        """

        self._type = value_type
        self._data_type = data_type

        self.state = None
        """Owning state. For internal use only."""

        self.index = 0
        """Value index. For internal use only."""

    @property
    def type(self: 'Value') -> 'Value.Type':
        """Type of value.

        Return:
        Value.Type: Type of value.

        """
        return self._type

    @property
    def data_type(self: 'Value') -> ValueTypes:
        """Data type.

        Return:
        ValueTypes: Data type.

        """
        return self._data_type

    @abstractmethod
    def read(self: 'Value', reader: MessageReader) -> None:
        """Read value from message.

        Parameters:
        reader (MessageReader): Message reader.

        """
        pass

    @abstractmethod
    def write(self: 'Value', writer: MessageWriter) -> None:
        """Write value to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        pass

    @abstractmethod
    def update_value(self: 'Value', force: bool) -> bool:
        """Update value.

        Returns true if value needs to by synchronized otherwise false if
        not changed enough.

        Parameters:
        force (bool): Force updating value even if not changed.

        Return:
        bool: True if value change or force is True.

        """
        pass

    def remote_value_changed(self: 'Value') -> None:
        """Remote value changed.

        For use by subclass to react to remote value changes.

        """
        pass

    def _value_changed(self: 'Value') -> None:
        """Value changed."""
        if self.state is not None:
            self.state.value_changed(self)
