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

from enum import IntEnum


class CommandCodes(IntEnum):

    """Protocol command codes."""

    CONNECTION_REQUEST = 0
    """Connection Request."""

    CONNECTION_ACK = 1
    """Connection Acknowledge."""

    CONNECTION_CLOSE = 2
    """Close Connection."""

    MESSAGE = 3
    """Unreliable message."""

    RELIABLE_MESSAGE = 4
    """Reliable message."""

    RELIABLE_LINK_STATE = 5
    """Link state."""

    RELIABLE_ACK = 6
    """Reliable acknowledge."""

    LINK_UP = 7
    """Link up."""

    LINK_DOWN = 8
    """Link down."""

    LINK_UPDATE = 9
    """Link update."""


class ConnectionAck(IntEnum):

    """Acknowledge connection codes."""

    ACCEPTED = 0
    """Connection accepted."""

    REJECTED = 1
    """Connection rejected."""

    NO_COMMON_PROTOCOL = 2
    """Connection rejected because client and server have no common
    protocol."""


class Protocols(IntEnum):

    """Protocols."""

    DENETWORK_PROTOCOL = 0
    """Drag[en]gine Network Protocol (DNP) Version 1"""


class ReliableAck(IntEnum):

    """Reliable acknowledge codes."""

    SUCCESS = 0
    """Reliable message received successfully."""

    FAILED = 1
    """Received reliable message is invalid. Sender has to resend it."""


class ValueTypes(IntEnum):

    """State value types."""

    SINT8 = 0
    """Integer: Signed char (8-bit)."""

    UINT8 = 1
    """Integer: Unsigned char (8-bit)."""

    SINT16 = 2
    """Integer: Signed short (16-bit)."""

    UINT16 = 3
    """Integer: Unsigned short (16-bit)."""

    SINT32 = 4
    """Integer: Signed long (32-bit)."""

    UINT32 = 5
    """Integer: Unsigned long (32-bit)."""

    SINT64 = 6
    """Integer: Signed long (64-bit)."""

    UINT64 = 7
    """Integer: Unsigned long (64-bit)."""

    FLOAT16 = 8
    """Float: Half float (16-bit)."""

    FLOAT32 = 9
    """Float: Float (32-bit)."""

    FLOAT64 = 10
    """Float: Float (32-bit)."""

    STRING = 11
    """String."""

    DATA = 12
    """Data: Length unsigned 8-bit"""

    POINT2S8 = 13
    """Point2: Signed 8-bit per component."""

    POINT2U8 = 14
    """Point2: Unsigned 8-bit per component."""

    POINT2S16 = 15
    """Point2: Signed 16-bit per component."""

    POINT2U16 = 16
    """Point2: Unsigned 16-bit per component."""

    POINT2S32 = 17
    """Point2: Signed 32-bit per component."""

    POINT2U32 = 18
    """Point2: Unsigned 32-bit per component."""

    POINT2S64 = 19
    """Point2: Signed 64-bit per component."""

    POINT2U64 = 20
    """Point2: Unsigned 64-bit per component."""

    POINT3S8 = 21
    """Point3: Signed 8-bit per component."""

    POINT3U8 = 22
    """Point3: Unsigned 8-bit per component."""

    POINT3S16 = 23
    """Point3: Signed 16-bit per component."""

    POINT3U16 = 24
    """Point3: Unsigned 16-bit per component."""

    POINT3S32 = 25
    """Point3: Signed 32-bit per component."""

    POINT3U32 = 26
    """Point3: Unsigned 32-bit per component."""

    POINT3S64 = 27
    """Point3: Signed 64-bit per component."""

    POINT3U64 = 28
    """Point3: Unsigned 64-bit per component."""

    VECTOR2F16 = 29
    """Vector2: 16-bit per component."""

    VECTOR2F32 = 30
    """Vector2: 32-bit per component."""

    VECTOR2F64 = 31
    """Vector2: 64-bit per component."""

    VECTOR3F16 = 32
    """Vector3: 16-bit per component."""

    VECTOR3F32 = 33
    """Vector3: 32-bit per component."""

    VECTOR3F64 = 34
    """Vector3: 64-bit per component."""

    QUATERNIONF16 = 35
    """Quaternion: 16-bit per component."""

    QUATERNIONF32 = 36
    """Quaternion: 32-bit per component."""

    QUATERNIONF64 = 37
    """Quaternion: 64-bit per component."""
