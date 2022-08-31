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

import struct
import binascii


class HalfFloat:

    """Half floting point class.

    Modified from:
    https://davidejones.com/blog/python-precision-floating-point/

    """

    def __init__(self: 'HalfFloat') -> None:
        """Class can not be instantiated."""
        raise Exception('class can not be instantiated')

    @classmethod
    def float_to_half(cls: 'HalfFloat', value: float) -> int:
        """Convert 32-bit float to 16-float.

        Parameters:
        value (float): Value to encode.

        Return:
        int: Value encoded as 16-bit unsigned integer.

        """
        f16_exponent_bits = 0x1f
        f16_exponent_shift = 10
        f16_exponent_bias = 15
        f16_mantissa_bits = 0x3ff
        f16_mantissa_shift = (23 - f16_exponent_shift)
        f16_max_exponent = (f16_exponent_bits << f16_exponent_shift)

        a = struct.pack(">f", value)
        b = binascii.hexlify(a)

        f32 = int(b, 16)
        sign = (f32 >> 16) & 0x8000
        exponent = ((f32 >> 23) & 0xff) - 127
        mantissa = f32 & 0x007fffff

        if exponent == 128:
            f16 = sign | f16_max_exponent
            if mantissa:
                f16 |= (mantissa & f16_mantissa_bits)
            return f16
        elif exponent > 15:
            return sign | f16_max_exponent
        elif exponent > -15:
            exponent += f16_exponent_bias
            mantissa >>= f16_mantissa_shift
            return sign | exponent << f16_exponent_shift | mantissa
        else:
            return sign

    @classmethod
    def half_to_float(cls: 'HalfFloat', value: int) -> float:
        """Convert 16-bit float to 32-bit float.

        Parameters:
        value (int): 16-bit unsigned integer value to decode.

        Return:
        float: Decoded floating point value.

        """
        s = int((value >> 15) & 0x00000001)    # sign
        e = int((value >> 10) & 0x0000001f)    # exponent
        f = int(value & 0x000003ff)            # fraction

        if e == 0:
            if f == 0:
                return int(s << 31)
            else:
                while not (f & 0x00000400):
                    f = f << 1
                    e -= 1
                e += 1
                f &= ~0x00000400
        elif e == 31:
            if f == 0:
                return int((s << 31) | 0x7f800000)
            else:
                return int((s << 31) | 0x7f800000 | (f << 13))

        e = e + (127 - 15)
        f = f << 13
        i = int((s << 31) | (e << 23) | f)
        return struct.unpack(">f", struct.pack(">I", i))[0]
