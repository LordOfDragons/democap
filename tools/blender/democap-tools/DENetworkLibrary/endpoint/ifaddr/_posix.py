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


import os
import ctypes.util
import ipaddress
import collections
import socket

from typing import Iterable, Optional

from . import _shared as shared


class Ifaddrs(ctypes.Structure):

    """Ifaddrs."""

    pass


Ifaddrs._fields_ = [
    ('ifa_next', ctypes.POINTER(Ifaddrs)),
    ('ifa_name', ctypes.c_char_p),
    ('ifa_flags', ctypes.c_uint),
    ('ifa_addr', ctypes.POINTER(shared.Sockaddr)),
    ('ifa_netmask', ctypes.POINTER(shared.Sockaddr)),
]

libc = ctypes.CDLL(ctypes.util.find_library(
    "socket" if os.uname()[0] == "SunOS" else "c"),
    use_errno=True)  # type: ignore


def get_adapters(include_unconfigured: bool = False) -> Iterable[
        shared.Adapter]:
    """Get adapters.

    Return:
    Iterable: Adapters.

    """

    addr0 = addr = ctypes.POINTER(Ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    if retval != 0:
        eno = ctypes.get_errno()
        raise OSError(eno, os.strerror(eno))

    ips = collections.OrderedDict()

    def add_ip(adapter_name: str, ip: Optional[shared.IP]) -> None:
        if adapter_name not in ips:
            index = None  # type: Optional[int]
            try:
                # Mypy errors on this when the Windows CI runs:
                #     error: Module has no attribute "if_nametoindex"
                index = socket.if_nametoindex(adapter_name)  # type: ignore
            except (OSError, AttributeError):
                pass
            ips[adapter_name] = shared.Adapter(adapter_name, adapter_name,
                                               [], index=index)
        if ip is not None:
            ips[adapter_name].ips.append(ip)

    while addr:
        name = addr[0].ifa_name.decode(encoding='UTF-8')
        ip_addr = shared.sockaddr_to_ip(addr[0].ifa_addr)
        if ip_addr:
            if addr[0].ifa_netmask and not addr[0].ifa_netmask[0].sa_familiy:
                addr[0].ifa_netmask[0].sa_familiy = (
                    addr[0].ifa_addr[0].sa_familiy)
            netmask = shared.sockaddr_to_ip(addr[0].ifa_netmask)
            if isinstance(netmask, tuple):
                netmask_str = str(netmask[0])
                prefixlen = shared.ipv6_prefixlength(
                    ipaddress.IPv6Address(netmask_str))
            else:
                assert netmask is not None,\
                    f'sockaddr_to_ip({addr[0].ifa_netmask}) returned None'
                netmask_str = str('0.0.0.0/' + netmask)
                prefixlen = ipaddress.IPv4Network(netmask_str).prefixlen
            ip = shared.IP(ip_addr, prefixlen, name)
            add_ip(name, ip)
        else:
            if include_unconfigured:
                add_ip(name, None)
        addr = addr[0].ifa_next

    libc.freeifaddrs(addr0)

    return ips.values()
