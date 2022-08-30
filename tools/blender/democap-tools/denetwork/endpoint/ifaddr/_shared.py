# -*- coding: utf-8 -*-

# Copyright (c) 2014 Stefan C. Mueller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""@package ifaddr."""


import ctypes
import socket
import ipaddress
import platform

from typing import List, Optional, Tuple, Union


class Adapter(object):

    """Represents a network interface device controller (NIC).

    For example a network card. An adapter can have multiple IPs.

    On Linux aliasing (multiple IPs per physical NIC) is implemented
    by creating 'virtual' adapters, each represented by an instance
    of this class. Each of those 'virtual' adapters can have both
    a IPv4 and an IPv6 IP address.

    """

    def __init__(self: 'Adapter', name: str, nice_name: str,
                 ips: List['IP'], index: Optional[int] = None) -> None:
        """Init."""

        #: Unique name that identifies the adapter in the system.
        #: On Linux this is of the form of `eth0` or `eth0:1`, on
        #: Windows it is a UUID in string representation, such as
        #: `{846EE342-7039-11DE-9D20-806E6F6E6963}`.
        self.name = name

        #: Human readable name of the adpater. On Linux this
        #: is currently the same as :attr:`name`. On Windows
        #: this is the name of the device.
        self.nice_name = nice_name

        #: List of :class:`ifaddr.IP` instances in the order they were
        #: reported by the system.
        self.ips = ips

        #: Adapter index as used by some API (e.g. IPv6 multicast group join).
        self.index = index

    def __repr__(self: 'Adapter') -> str:
        """String representation.

        Return:
        str: String.

        """
        return "Adapter({name}, {nice_name}, {ips}, {index})".format(
            name=repr(self.name), nice_name=repr(self.nice_name),
            ips=repr(self.ips), index=repr(self.index)
        )


# Type of an IPv4 address (a string in "xxx.xxx.xxx.xxx" format)
_IPv4Address = str

# Type of an IPv6 address (a three-tuple `(ip, flowinfo, scope_id)`)
_IPv6Address = Tuple[str, int, int]


class IP(object):

    """Represents an IP address of an adapter."""

    def __init__(self: 'IP', ip: Union[_IPv4Address, _IPv6Address],
                 network_prefix: int, nice_name: str) -> None:
        """Init."""

        #: IP address. For IPv4 addresses this is a string in
        #: "xxx.xxx.xxx.xxx" format. For IPv6 addresses this
        #: is a three-tuple `(ip, flowinfo, scope_id)`, where
        #: `ip` is a string in the usual collon separated
        #: hex format.
        self.ip = ip

        #: Number of bits of the IP that represent the
        #: network. For a `255.255.255.0` netmask, this
        #: number would be `24`.
        self.network_prefix = network_prefix

        #: Human readable name for this IP.
        #: On Linux is this currently the same as the adapter name.
        #: On Windows this is the name of the network connection
        #: as configured in the system control panel.
        self.nice_name = nice_name

    @property
    def is_ipv4(self: 'IP') -> bool:
        """Check if this is an IPv4 address.

        Return:

        bool: Address is IPv4."""
        return not isinstance(self.ip, tuple)

    @property
    def is_ipv6(self: 'IP') -> bool:
        """Check if this is an IPv6 address.

        Return:

        bool: Address is IPv6."""
        return isinstance(self.ip, tuple)

    def __repr__(self: 'IP') -> str:
        """String representation:.

        Return:
        str: String.

        """
        return "IP({ip}, {network_prefix}, {nice_name})".format(
            ip=repr(self.ip), network_prefix=repr(self.network_prefix),
            nice_name=repr(self.nice_name)
        )


if platform.system() == "Darwin" or "BSD" in platform.system():

    # BSD derived systems use marginally different structures
    # than either Linux or Windows.
    # I still keep it in `shared` since we can use
    # both structures equally.

    class Sockaddr(ctypes.Structure):
        _fields_ = [
            ('sa_len', ctypes.c_uint8),
            ('sa_familiy', ctypes.c_uint8),
            ('sa_data', ctypes.c_uint8 * 14),
        ]

    class SockaddrIn(ctypes.Structure):
        _fields_ = [
            ('sa_len', ctypes.c_uint8),
            ('sa_familiy', ctypes.c_uint8),
            ('sin_port', ctypes.c_uint16),
            ('sin_addr', ctypes.c_uint8 * 4),
            ('sin_zero', ctypes.c_uint8 * 8),
        ]

    class SockaddrIn6(ctypes.Structure):
        _fields_ = [
            ('sa_len', ctypes.c_uint8),
            ('sa_familiy', ctypes.c_uint8),
            ('sin6_port', ctypes.c_uint16),
            ('sin6_flowinfo', ctypes.c_uint32),
            ('sin6_addr', ctypes.c_uint8 * 16),
            ('sin6_scope_id', ctypes.c_uint32),
        ]

else:

    class Sockaddr(ctypes.Structure):  # type: ignore
        _fields_ = [('sa_familiy', ctypes.c_uint16),
                    ('sa_data', ctypes.c_uint8 * 14)]

    class SockaddrIn(ctypes.Structure):  # type: ignore
        _fields_ = [
            ('sin_familiy', ctypes.c_uint16),
            ('sin_port', ctypes.c_uint16),
            ('sin_addr', ctypes.c_uint8 * 4),
            ('sin_zero', ctypes.c_uint8 * 8),
        ]

    class SockaddrIn6(ctypes.Structure):  # type: ignore
        _fields_ = [
            ('sin6_familiy', ctypes.c_uint16),
            ('sin6_port', ctypes.c_uint16),
            ('sin6_flowinfo', ctypes.c_uint32),
            ('sin6_addr', ctypes.c_uint8 * 16),
            ('sin6_scope_id', ctypes.c_uint32),
        ]


def sockaddr_to_ip(sockaddr_ptr: 'ctypes.pointer[Sockaddr]') -> Optional[
        Union[_IPv4Address, _IPv6Address]]:
    """Sock addr to ip.

    Return:
    _IPv4Address: Address if IPv4.
    _IPv6Address: Address if IPv6.

    """
    if sockaddr_ptr:
        if sockaddr_ptr[0].sa_familiy == socket.AF_INET:
            ipv4 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(SockaddrIn))
            ippacked = bytes(bytearray(ipv4[0].sin_addr))
            return str(ipaddress.ip_address(ippacked))
        elif sockaddr_ptr[0].sa_familiy == socket.AF_INET6:
            ipv6 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(SockaddrIn6))
            flowinfo = ipv6[0].sin6_flowinfo
            ippacked = bytes(bytearray(ipv6[0].sin6_addr))
            ip = str(ipaddress.ip_address(ippacked))
            scope_id = ipv6[0].sin6_scope_id
            return (ip, flowinfo, scope_id)
    return None


def ipv6_prefixlength(address: ipaddress.IPv6Address) -> int:
    """IPv6 prefix length.

    Return:
    int: Prefix length.

    """
    prefix_length = 0
    for i in range(address.max_prefixlen):
        if int(address) >> i & 1:
            prefix_length = prefix_length + 1
    return prefix_length
