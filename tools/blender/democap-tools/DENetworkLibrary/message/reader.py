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

from .message import Message
from struct import unpack_from
from ..math.vector2 import Vector2
from ..math.vector3 import Vector3
from ..math.quaternion import Quaternion
from ..math.point2 import Point2
from ..math.point3 import Point3


class MessageReader:

    """Message reader.

    This class does not require context managing to be used but you can
    do so to keep your code cleaner and more readable. This example matches
    the example in MessageWriter:

    import DENetworkLibrary as dnl
    message = dnl.message.Message()
    # read message data from somewhere
    with dnl.message.MessageReader(message) as r:
        print(r.read_byte())
        print(r.read_float())
        print(r.read_vector3())
        print(r.read_string8())

    """

    def __init__(self: 'MessageReader',  message: Message) -> None:
        """Create message reader."""

        self._data = message.data
        self._position = 0

    @property
    def data(self: 'MessageReader') -> bytearray:
        """Message data.

        Return:
        bytearray: message data.

        """
        return self._data

    @property
    def position(self: 'MessageReader') -> int:
        """Read position in bytes from the start of the message.

        Return:
        int: Position.

        """
        return self._position

    def read_char(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<b", self._data, self._position)[0]
        self._position = self._position + 1
        return value

    def read_byte(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<B", self._data, self._position)[0]
        self._position = self._position + 1
        return value

    def read_short(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<h", self._data, self._position)[0]
        self._position = self._position + 2
        return value

    def read_ushort(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<H", self._data, self._position)[0]
        self._position = self._position + 2
        return value

    def read_int(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<i", self._data, self._position)[0]
        self._position = self._position + 4
        return value

    def read_uint(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<I", self._data, self._position)[0]
        self._position = self._position + 4
        return value

    def read_long(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<q", self._data, self._position)[0]
        self._position = self._position + 8
        return value

    def read_ulong(self: 'MessageReader') -> int:
        """Read value.

        Return:
        int: Value

        """
        value = unpack_from("<Q", self._data, self._position)[0]
        self._position = self._position + 8
        return value

    def read_float(self: 'MessageReader') -> float:
        """Read value.

        Return:
        float: Value

        """
        value = unpack_from("<f", self._data, self._position)[0]
        self._position = self._position + 4
        return value

    def read_double(self: 'MessageReader') -> float:
        """Read value.

        Return:
        float: Value

        """
        value = unpack_from("<d", self._data, self._position)[0]
        self._position = self._position + 8
        return value

    def read_string8(self: 'MessageReader') -> str:
        """Read value.

        Return:
        str: Value

        """
        length = unpack_from("<B", self._data, self._position)[0]
        value = self._data[self._position + 1:self._position + 1 + length]
        value = value.decode('utf-8')
        if len(value) != length:
            raise Exception("not enough remaining data")
        self._position = self._position + 1 + length
        return value

    def read_string16(self: 'MessageReader') -> str:
        """Read value.

        Return:
        str: Value

        """
        length = unpack_from("<H", self._data, self._position)[0]
        value = self._data[self._position + 2:self._position + 2 + length]
        value = value.decode('utf-8')
        if len(value) != length:
            raise Exception("not enough remaining data")
        self._position = self._position + 2 + length
        return value

    def read_vector2(self: 'MessageReader') -> Vector2:
        """Read value.

        Return:
        Vector2: Value

        """
        value = unpack_from("<ff", self._data, self._position)
        value = Vector2(value[0], value[1])
        self._position = self._position + 8
        return value

    def read_vector3(self: 'MessageReader') -> Vector3:
        """Read value.

        Return:
        Vector3: Value

        """
        value = unpack_from("<fff", self._data, self._position)
        value = Vector3(value[0], value[1],  value[2])
        self._position = self._position + 12
        return value

    def read_quaternion(self: 'MessageReader') -> Quaternion:
        """Read value.

        Return:
        Quaternion: Value

        """
        value = unpack_from("<ffff",  self._data, self._position)
        value = Quaternion(value[0], value[1],  value[2],  value[3])
        self._position = self._position + 16
        return value

    def read_point2(self: 'MessageReader') -> Point2:
        """Read value.

        Return:
        Point2: Value

        """
        value = unpack_from("<ii", self._data, self._position)
        value = Point2(value[0], value[1])
        self._position = self._position + 8
        return value

    def read_point3(self: 'MessageReader') -> Point3:
        """Read value.

        Return:
        Point3: Value

        """
        value = unpack_from("<iii", self._data, self._position)
        value = Point3(value[0], value[1], value[2])
        self._position = self._position + 12
        return value

    def read_dvector(self: 'MessageReader') -> Vector3:
        """Read value.

        Return:
        Vector3: Value

        """
        value = unpack_from("<ddd", self._data, self._position)
        value = Vector3(value[0], value[1],  value[2])
        self._position = self._position + 24
        return value

    def read(self: 'MessageReader', length: int) -> str:
        """Read data.

        Parameters:
        length (int): Count of bytes to read.

        Return:
        str: Data

        """
        if length < 0:
            raise Exception("length < 0")
        value = self._data[self._position:self._position + length]
        if len(value) != length:
            raise Exception("not enough remaining data")
        self._position = self._position + length
        return value

    def read_info(self: 'MessageReader',
                  buffer: str,
                  offset: int,
                  length: int) -> None:
        """Read data into buffer.

        Parameters:
        buffer (str): Buffer to read into.
        offset (int): Offset in bytes to start writing to.
        length (int): Count of bytes to read.

        """
        if length < 0:
            raise Exception("length < 0")
        buffer[offset:offset + length] = self._data[
            self._position:self._position + length]
        self._position = self._position + length

    def read_message(self: 'MessageReader', message: Message) -> None:
        """Read message.

        Parameters:
        message (Message): Message to read into. Message length has to
                           be set to the count of bytes to read.

        """
        length = len(message.data)
        if length == 0:
            raise Exception("length < 0")
        message.data = self._data[self._position:self._position + length]
        self._position = self._position + length

    def __enter__(self: 'MessageReader') -> 'MessageReader':
        """Enter method for context manager support.

        This class does not need context manager usage but for clearer
        coding and grouping code this is implemented. Function does nothing.

        Return:
        MessageWriter: Self.

        """
        return self

    def __exit__(self: 'MessageReader',
                 exception_type: None,
                 exception_value: None,
                 traceback: None) -> None:
        """Exit method for context manager support.

        This class does not need context manager usage but for clearer
        coding and grouping code this is implemented. Function does nothing.

        """
        pass
