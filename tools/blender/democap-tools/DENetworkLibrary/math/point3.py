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


class Point3:

    """Immutable integer 3 component point."""

    def __init__(self: 'Point3',
                 x: Optional[int] = 0,
                 y: Optional[int] = 0,
                 z: Optional[int] = 0) -> None:
        """Create point."""

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self: 'Point3') -> int:
        """X component.

        Return:
        int: X component.

        """
        return self._x

    @property
    def y(self: 'Point3') -> int:
        """Y component.

        Return:
        int: Y component.

        """
        return self._y

    @property
    def z(self: 'Point3') -> int:
        """Z component.

        Return:
        int: Z component.

        """
        return self._z

    def __eq__(self: 'Point3', other: 'Point3') -> bool:
        """Equals.

        Parameters:
        other (Point3): Object to compare against.

        Return:
        bool: Result

        """
        if isinstance(other, Point3):
            return (self._x, self._y, self._z) == (other._x, other._y, self._z)
        return NotImplemented

    def __ne__(self: 'Point3',  other: 'Point3') -> bool:
        """Not equal.

        Parameters:
        other (Point3): Point to compare against.

        Return:
        bool: Result.

        """
        return (self._x, self._y, self._z) != (other._x, other._y, self._z)

    def __lt__(self: 'Point3',  other: 'Point3') -> bool:
        """Less than.

        Parameters:
        other (Point3): Point to compare against.

        Return:
        bool: Result.

        """
        return (self._x < other._x and self._y < other._y
                and self._z < other._z)

    def __le__(self: 'Point3', other: 'Point3') -> bool:
        """Less than or equal.

        Parameters:
        other (Point3): Point to compare against.

        Return:
        bool: Result.

        """
        return (self._x <= other._x and self._y <= other._y
                and self._z <= other._z)

    def __gt__(self: 'Point3', other: 'Point3') -> bool:
        """Greater than.

        Parameters:
        other (Point3): Point to compare against.

        Return:
        bool: Result.

        """
        return self._x > other._x and self._y > other._y and self._z > other._z

    def __ge__(self: 'Point3', other: 'Point3') -> bool:
        """Greater than or equal.

        Parameters:
        other (Point3): Point to compare against.

        Return:
        bool: Result.

        """
        return (self._x >= other._x and self._y >= other._y
                and self._z >= other._z)

    def __add__(self: 'Point3', other: 'Point3') -> 'Point3':
        """Add.

        Parameters:
        other (Point3): Point to add.

        Return:
        Point3: Result.

        """
        return Point3(self._x + other._x, self._y + other._y,
                      self._z + other._z)

    def __sub__(self: 'Point3', other: 'Point3') -> 'Point3':
        """Subtract.

        Parameters:
        other (Point3): Point to subtract.

        Return:
        Point3: Result.

        """
        return Point3(self._x - other._x, self._y - other._y,
                      self._z - other._z)

    def __mul__(self: 'Point3', scale: float) -> 'Point3':
        """Multiply.

        Parameters:
        scale (float): Scale factor.

        Return:
        Point3: Result.

        """
        return Point3(self._x * scale, self._y * scale, self._z * scale)

    def __div__(self: 'Point3', divisor: float) -> 'Point3':
        """Multiply.

        Parameters:
        divisor (float): Division factor.

        Return:
        Point3: Result.

        """
        return Point3(self._x / divisor, self._y / divisor, self._z / divisor)

    def __neg__(self: 'Point3') -> 'Point3':
        """Negate.

        Return:
        Point3: Result.

        """
        return Point3(-self._x, -self._y, -self._z)

    def __hash__(self: 'Point3') -> int:
        """Hash.

        Return:
        int: Hash

        """
        return hash((self._x, self._y, self._z))

    def __repr__(self: 'Point3') -> str:
        """Representing string (object information).

        Return:
        str: String

        """
        return "Point3({0},{1},{2})".format(self._x, self._y, self._z)

    def __str__(self: 'Point3') -> str:
        """Readable string.

        Return:
        str: String

        """
        return "Point3({0},{1},{2})".format(self._x, self._y, self._z)

    def __getitem__(self: 'Point3', key: int) -> int:
        """Get component.

        Parameters:
        key (int): Index of component to return (0=x, 1=y, 2=z).

        Return:
        int: Component value

        """
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        elif key == 2:
            return self._z
        else:
            raise KeyError()

    def __len__(self: 'Point3') -> int:
        """Lenght of point.

        Return:
        int: Length

        """
        return 3

    def __iter__(self: 'Point3') -> Iterator[int]:
        """Iterator.

        Return:
        Iterator: Iterator.

        """
        return iter((self._x,  self._y,  self._z))
