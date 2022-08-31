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


class Vector3:

    """Immutable integer 3 component vector."""

    def __init__(self: 'Vector3',
                 x: Optional[float] = 0.0,
                 y: Optional[float] = 0.0,
                 z: Optional[float] = 0.0) -> None:
        """Create vector."""

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self: 'Vector3') -> float:
        """X component.

        Return:
        float: X component.

        """
        return self._x

    @property
    def y(self: 'Vector3') -> float:
        """Y component.

        Return:
        float: Y component.

        """
        return self._y

    @property
    def z(self: 'Vector3') -> float:
        """Z component.

        Return:
        float: Z component.

        """
        return self._z

    def equals(self: 'Vector3',
               other: 'Vector3',
               threshold: float = 1e-15) -> bool:
        """Equals.

        Parameters:
        other (Vector3): Object to compare against.
        threshold (float): Equality threshold

        Return:
        bool: Result

        """
        return (fabs(self._x - other._x) <= threshold
                and fabs(self._y - other._y) <= threshold
                and fabs(self._z - other._z) <= threshold)

    def differs(self: 'Vector3',
                other: 'Vector3',
                threshold: float = 1e-15) -> bool:
        """Equals.

        Parameters:
        other (Vector3): Object to compare against.
        threshold (float): Equality threshold

        Return:
        bool: Result

        """
        return (fabs(self._x - other._x) > threshold
                or fabs(self._y - other._y) > threshold
                or fabs(self._z - other._z) > threshold)

    def __eq__(self: 'Vector3', other: 'Vector3') -> bool:
        """Equals.

        Parameters:
        other (Vector3): Object to compare against.

        Return:
        bool: Result

        """
        if isinstance(other, Vector3):
            return self.equals(other,  1e-15)
        return NotImplemented

    def __ne__(self: 'Vector3',  other: 'Vector3') -> bool:
        """Not equal.

        Parameters:
        other (Vector3): vector to compare against.

        Return:
        bool: Result.

        """
        return self.differs(other,  1e-15)

    def __lt__(self: 'Vector3',  other: 'Vector3') -> bool:
        """Less than.

        Parameters:
        other (Vector3): vector to compare against.

        Return:
        bool: Result.

        """
        return self._x < other._x and self._y < other._y and self._z < other._z

    def __le__(self: 'Vector3', other: 'Vector3') -> bool:
        """Less than or equal.

        Parameters:
        other (Vector3): vector to compare against.

        Return:
        bool: Result.

        """
        return (self._x <= other._x and self._y <= other._y
                and self._z <= other._z)

    def __gt__(self: 'Vector3', other: 'Vector3') -> bool:
        """Greater than.

        Parameters:
        other (Vector3): vector to compare against.

        Return:
        bool: Result.

        """
        return self._x > other._x and self._y > other._y and self._z > other._z

    def __ge__(self: 'Vector3', other: 'Vector3') -> bool:
        """Greater than or equal.

        Parameters:
        other (Vector3): vector to compare against.

        Return:
        bool: Result.

        """
        return (self._x >= other._x and self._y >= other._y
                and self._z >= other._z)

    def __abs__(self: 'Vector3') -> 'Vector3':
        """Absolute.

        Return:
        Vector3: Result.

        """
        return Vector3(fabs(self._x), fabs(self._y), fabs(self._z))

    def __add__(self: 'Vector3', other: 'Vector3') -> 'Vector3':
        """Add.

        Parameters:
        other (Vector3): vector to add.

        Return:
        Vector3: Result.

        """
        return Vector3(self._x + other._x, self._y + other._y,
                       self._z + other._z)

    def __sub__(self: 'Vector3', other: 'Vector3') -> 'Vector3':
        """Subtract.

        Parameters:
        other (Vector3): vector to subtract.

        Return:
        Vector3: Result.

        """
        return Vector3(self._x - other._x, self._y - other._y,
                       self._z - other._z)

    def __mul__(self: 'Vector3', scale: float) -> 'Vector3':
        """Multiply.

        Parameters:
        scale (float): Scale factor.

        Return:
        Vector3: Result.

        """
        return Vector3(self._x * scale, self._y * scale, self._z * scale)

    def __div__(self: 'Vector3', divisor: float) -> 'Vector3':
        """Multiply.

        Parameters:
        divisor (float): Division factor.

        Return:
        Vector3: Result.

        """
        return Vector3(self._x / divisor, self._y / divisor, self._z / divisor)

    def __neg__(self: 'Vector3') -> 'Vector3':
        """Negate.

        Return:
        Vector3: Result.

        """
        return Vector3(-self._x, -self._y, -self._z)

    def __hash__(self: 'Vector3') -> int:
        """Hash.

        Return:
        int: Hash

        """
        return hash((self._x, self._y, self._z))

    def __repr__(self: 'Vector3') -> str:
        """Representing string (object information).

        Return:
        str: String

        """
        return "Vector3({0},{1},{2})".format(self._x, self._y, self._z)

    def __str__(self: 'Vector3') -> str:
        """Readable string.

        Return:
        str: String

        """
        return "Vector3({0:.3g},{1:.3g},{2:.3g})".format(
               self._x, self._y, self._z)

    def __getitem__(self: 'Vector3', key: int) -> float:
        """Get component.

        Parameters:
        key (int): Index of component to return (0=x, 1=y, 2=z).

        Return:
        float: Component value

        """
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        elif key == 2:
            return self._z
        else:
            raise KeyError()

    def __len__(self: 'Vector3') -> int:
        """Lenght of vector.

        Return:
        int: Length

        """
        return 3

    def __iter__(self: 'Vector3') -> Iterator[float]:
        """Iterator.

        Return:
        Iterator: Iterator.

        """
        return iter((self._x,  self._y,  self._z))
