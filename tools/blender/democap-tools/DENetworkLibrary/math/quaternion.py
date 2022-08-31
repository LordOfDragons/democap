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

from typing import Optional, Iterator
from math import fabs


class Quaternion:

    """Immutable integer 4 component quaternion."""

    def __init__(self: 'Quaternion',
                 x: Optional[float] = 0.0,
                 y: Optional[float] = 0.0,
                 z: Optional[float] = 0.0,
                 w: Optional[float] = 1.0) -> None:
        """Create quaternion."""

        self._x = x
        self._y = y
        self._z = z
        self._w = w

    @property
    def x(self: 'Quaternion') -> float:
        """X component.

        Return:
        float: X component.

        """
        return self._x

    @property
    def y(self: 'Quaternion') -> float:
        """Y component.

        Return:
        float: Y component.

        """
        return self._y

    @property
    def z(self: 'Quaternion') -> float:
        """Z component.

        Return:
        float: Z component.

        """
        return self._z

    @property
    def w(self: 'Quaternion') -> float:
        """W component.

        Return:
        float: W component.

        """
        return self._w

    def equals(self: 'Quaternion',
               other: 'Quaternion',
               threshold: float = 1e-15) -> bool:
        """Equals.

        Parameters:
        other (Quaternion): Object to compare against.
        threshold (float): Equality threshold

        Return:
        bool: Result

        """
        return (fabs(self._x - other._x) <= threshold
                and fabs(self._y - other._y) <= threshold
                and fabs(self._z - other._z) <= threshold
                and fabs(self._w - other._w) <= threshold)

    def differs(self: 'Quaternion',
                other: 'Quaternion',
                threshold: float = 1e-15) -> bool:
        """Equals.

        Parameters:
        other (Quaternion): Object to compare against.
        threshold (float): Equality threshold

        Return:
        bool: Result

        """
        return (fabs(self._x - other._x) > threshold
                or fabs(self._y - other._y) > threshold
                or fabs(self._z - other._z) > threshold
                or fabs(self._w - other._w) > threshold)

    def __eq__(self: 'Quaternion', other: 'Quaternion') -> bool:
        """Equals.

        Parameters:
        other (Quaternion): Object to compare against.

        Return:
        bool: Result

        """
        if isinstance(other, Quaternion):
            return self.equals(other,  1e-15)
        return NotImplemented

    def __ne__(self: 'Quaternion',  other: 'Quaternion') -> bool:
        """Not equal.

        Parameters:
        other (Quaternion): quaternion to compare against.

        Return:
        bool: Result.

        """
        return self.differs(other,  1e-15)

    def __lt__(self: 'Quaternion',  other: 'Quaternion') -> bool:
        """Less than.

        Parameters:
        other (Quaternion): quaternion to compare against.

        Return:
        bool: Result.

        """
        return (self._x < other._x and self._y < other._y
                and self._z < other._z and self._w < other._w)

    def __le__(self: 'Quaternion', other: 'Quaternion') -> bool:
        """Less than or equal.

        Parameters:
        other (Quaternion): quaternion to compare against.

        Return:
        bool: Result.

        """
        return (self._x <= other._x and self._y <= other._y
                and self._z <= other._z and self._w <= other._w)

    def __gt__(self: 'Quaternion', other: 'Quaternion') -> bool:
        """Greater than.

        Parameters:
        other (Quaternion): quaternion to compare against.

        Return:
        bool: Result.

        """
        return (self._x > other._x and self._y > other._y
                and self._z > other._z and self._w > other._w)

    def __ge__(self: 'Quaternion', other: 'Quaternion') -> bool:
        """Greater than or equal.

        Parameters:
        other (Quaternion): quaternion to compare against.

        Return:
        bool: Result.

        """
        return (self._x >= other._x and self._y >= other._y
                and self._z >= other._z and self._w >= other._w)

    def __abs__(self: 'Quaternion') -> 'Quaternion':
        """Absolute.

        Return:
        Quaternion: Result.

        """
        return Quaternion(fabs(self._x), fabs(self._y),
                          fabs(self._z), fabs(self._w))

    def __add__(self: 'Quaternion', other: 'Quaternion') -> 'Quaternion':
        """Add.

        Parameters:
        other (Quaternion): quaternion to add.

        Return:
        Quaternion: Result.

        """
        return Quaternion(self._x + other._x, self._y + other._y,
                          self._z + other._z, self._w + other._w)

    def __sub__(self: 'Quaternion', other: 'Quaternion') -> 'Quaternion':
        """Subtract.

        Parameters:
        other (Quaternion): quaternion to subtract.

        Return:
        Quaternion: Result.

        """
        return Quaternion(self._x - other._x, self._y - other._y,
                          self._z - other._z, self._w - other._w)

    def __mul__(self: 'Quaternion', scale: float) -> 'Quaternion':
        """Multiply.

        Parameters:
        scale (float): Scale factor.

        Return:
        Quaternion: Result.

        """
        return Quaternion(self._x * scale, self._y * scale,
                          self._z * scale, self._w * scale)

    def __div__(self: 'Quaternion', divisor: float) -> 'Quaternion':
        """Multiply.

        Parameters:
        divisor (float): Division factor.

        Return:
        Quaternion: Result.

        """
        return Quaternion(self._x / divisor, self._y / divisor,
                          self._z / divisor, self._w / divisor)

    def __neg__(self: 'Quaternion') -> 'Quaternion':
        """Negate.

        Return:
        Quaternion: Result.

        """
        return Quaternion(-self._x, -self._y, -self._z, -self._w)

    def __hash__(self: 'Quaternion') -> int:
        """Hash.

        Return:
        int: Hash

        """
        return hash((self._x, self._y, self._z, self._w))

    def __repr__(self: 'Quaternion') -> str:
        """Representing string (object information).

        Return:
        str: String

        """
        return "Quaternion({0},{1},{2},{3})".format(
               self._x, self._y, self._z, self._w)

    def __str__(self: 'Quaternion') -> str:
        """Readable string.

        Return:
        str: String

        """
        return "Quaternion({0:.3g},{1:.3g},{2:.3g},{3:.3g})".format(
               self._x, self._y, self._z, self._w)

    def __getitem__(self: 'Quaternion', key: int) -> float:
        """Get component.

        Parameters:
        key (int): Index of component to return (0=x, 1=y, 2=z, 3=w).

        Return:
        float: Component value

        """
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        elif key == 2:
            return self._z
        elif key == 3:
            return self._w
        else:
            raise KeyError()

    def __len__(self: 'Quaternion') -> int:
        """Lenght of vector.

        Return:
        int: Length

        """
        return 4

    def __iter__(self: 'Quaternion') -> Iterator[float]:
        """Iterator.

        Return:
        Iterator: Iterator.

        """
        return iter((self._x,  self._y,  self._z,  self._w))
