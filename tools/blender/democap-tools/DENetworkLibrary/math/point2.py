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


class Point2:

    """Immutable integer 2 component point."""

    def __init__(self: 'Point2',
                 x: Optional[int] = 0,
                 y: Optional[int] = 0) -> None:
        """Create point."""

        self._x = x
        self._y = y

    @property
    def x(self: 'Point2') -> int:
        """X component.

        Return:
        int: X component.

        """
        return self._x

    @property
    def y(self: 'Point2') -> int:
        """Y component.

        Return:
        int: Y component.

        """
        return self._y

    def __eq__(self: 'Point2', other: 'Point2') -> bool:
        """Equals.

        Parameters:
        other (Point2): Object to compare against.

        Return:
        bool: Result

        """
        if isinstance(other, Point2):
            return (self._x, self._y) == (other._x, other._y)
        return NotImplemented

    def __ne__(self: 'Point2',  other: 'Point2') -> bool:
        """Not equal.

        Parameters:
        other (Point2): Point to compare against.

        Return:
        bool: Result.

        """
        return (self._x, self._y) != (other._x, other._y)

    def __lt__(self: 'Point2',  other: 'Point2') -> bool:
        """Less than.

        Parameters:
        other (Point2): Point to compare against.

        Return:
        bool: Result.

        """
        return self._x < other._x and self._y < other._y

    def __le__(self: 'Point2', other: 'Point2') -> bool:
        """Less than or equal.

        Parameters:
        other (Point2): Point to compare against.

        Return:
        bool: Result.

        """
        return self._x <= other._x and self._y <= other._y

    def __gt__(self: 'Point2', other: 'Point2') -> bool:
        """Greater than.

        Parameters:
        other (Point2): Point to compare against.

        Return:
        bool: Result.

        """
        return self._x > other._x and self._y > other._y

    def __ge__(self: 'Point2', other: 'Point2') -> bool:
        """Greater than or equal.

        Parameters:
        other (Point2): Point to compare against.

        Return:
        bool: Result.

        """
        return self._x >= other._x and self._y >= other._y

    def __add__(self: 'Point2', other: 'Point2') -> 'Point2':
        """Add.

        Parameters:
        other (Point2): Point to add.

        Return:
        Point2: Result.

        """
        return Point2(self._x + other._x, self._y + other._y)

    def __sub__(self: 'Point2', other: 'Point2') -> 'Point2':
        """Subtract.

        Parameters:
        other (Point2): Point to subtract.

        Return:
        Point2: Result.

        """
        return Point2(self._x - other._x, self._y - other._y)

    def __mul__(self: 'Point2', scale: float) -> 'Point2':
        """Multiply.

        Parameters:
        scale (float): Scale factor.

        Return:
        Point2: Result.

        """
        return Point2(self._x * scale, self._y * scale)

    def __div__(self: 'Point2', divisor: float) -> 'Point2':
        """Multiply.

        Parameters:
        divisor (float): Division factor.

        Return:
        Point2: Result.

        """
        return Point2(self._x / divisor, self._y / divisor)

    def __neg__(self: 'Point2') -> 'Point2':
        """Negate.

        Return:
        Point2: Result.

        """
        return Point2(-self._x, -self._y)

    def __hash__(self: 'Point2') -> int:
        """Hash.

        Return:
        int: Hash

        """
        return hash((self._x, self._y))

    def __repr__(self: 'Point2') -> str:
        """Representing string (object information).

        Return:
        str: String

        """
        return "Point2({0},{1})".format(self._x, self._y)

    def __str__(self: 'Point2') -> str:
        """Readable string.

        Return:
        str: String

        """
        return "Point2({0},{1})".format(self._x, self._y)

    def __getitem__(self: 'Point2', key: int) -> int:
        """Get component.

        Parameters:
        key (int): Index of component to return (0=x, 1=y).

        Return:
        int: Component value

        """
        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        else:
            raise KeyError()

    def __len__(self: 'Point2') -> int:
        """Lenght of point.

        Return:
        int: Length

        """
        return 2

    def __iter__(self: 'Point2') -> Iterator[int]:
        """Iterator.

        Return:
        Iterator: Iterator.

        """
        return iter((self._x,  self._y))
