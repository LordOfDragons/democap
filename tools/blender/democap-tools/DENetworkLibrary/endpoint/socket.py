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

from .endpoint import Endpoint
from ..message.message import Message
from .address import Address
from . import ifaddr
from ipaddress import ip_address
from typing import List
import asyncio
import socket
import warnings


class SocketEndpoint(Endpoint, asyncio.DatagramProtocol):

    """Endpoint using UDP socket."""

    def __init__(self: 'SocketEndpoint') -> None:
        """Create SocketEndpoint."""

        Endpoint.__init__(self)

        self._transport = None

    def dispose(self: 'SocketEndpoint') -> None:
        """Dispose of SocketEndpoint."""
        self.close()

    def open(self: 'SocketEndpoint',
             address: Address,
             listener: 'SocketEndpoint.Listener') -> None:
        """Open SocketEndpoint delivering events to the provided listener.

        Parameters:
        address (Address): Address to listen on.
        listener (Listener): Listener to invoke.

        """
        if self._transport:
            raise Exception("already open")
        if not address:
            raise Exception("address is None")
        if not listener:
            raise Exception("listener is None")

        if address.type == Address.Type.IPV6:
            protocol = socket.AF_INET6
            """
            saddr = (address.host, address.port, 0,
                     self.scope_id_for(address))
            """
            saddr = (address.host, address.port)
        else:
            protocol = socket.AF_INET
            saddr = (address.host, address.port)

        self.listener = listener
        try:
            loop = asyncio.get_event_loop()
            (t, p) = loop.run_until_complete(loop.create_datagram_endpoint(
                lambda: self, local_addr=saddr, family=protocol))

            self._transport = t
        except Exception as e:
            self.listener = None
            raise e

        if address.type == Address.Type.IPV6:
            self.address = SocketEndpoint.address_from_socket_ipv6(
                t.get_extra_info('sockname'))
        else:
            self.address = SocketEndpoint.address_from_socket_ipv4(
                t.get_extra_info('sockname'))

    def close(self: 'SocketEndpoint') -> None:
        """Close SocketEndpoint if open.

        Stop delivering events to listener provided in the previous open call.

        """
        if self._transport:
            self._transport.close()
            self._transport = None
        self.listener = None

    def send_datagram(self: 'SocketEndpoint',
                      address: Address,
                      message: Message) -> None:
        """Send datagram.

        Parameters:
        address (Address): Address to send datagram to.
        message (Message): Message to send.

        """
        if self._transport:
            if len(message.data) > 65500:
                raise Exception("Message too long: {} (max 65500)".format(
                    len(message.data)))

            if address.type == Address.Type.IPV6:
                saddr = (address.host, address.port, 0, 0)
            else:
                saddr = (address.host, address.port)
            self._transport.sendto(message.data, saddr)

    def scope_id_for(self: 'SocketEndpoint', address: Address) -> int:
        """Find scope id for address or 0 if not found.

        Return:
        str: Scope id or None.

        """
        host = address.host
        for adapter in ifaddr.get_adapters():
            for ip in adapter.ips:
                if ip.is_ipv6 and ip.ip[0] == host:
                    return ip.ip[2]
        return 0

    @classmethod
    def address_from_socket_ipv4(cls: 'SocketEndpoint',
                                 address: tuple) -> Address:
        """Get address from socket address.

        Parameters:
        address (tuple): Socket address.

        Return:
        Address: Converted address.

        """
        sa = int(ip_address(address[0]))
        values = []
        for _i in range(4):
            values.append(sa & 0xff)
            sa = sa >> 8
        return Address.ipv4(list(reversed(values)), address[1])

    @classmethod
    def address_from_socket_ipv6(cls: 'SocketEndpoint',
                                 address: tuple) -> Address:
        """Get address from socket address.

        Parameters:
        address (tuple): Socket address.

        Return:
        Address: Converted address.

        """
        sa = int(ip_address(address[0]))
        values = []
        for _i in range(16):
            values.append(sa & 0xff)
            sa = sa >> 8
        return Address.ipv6(list(reversed(values)), address[1])

    def datagram_received(self: 'SocketEndpoint',
                          data: str,
                          address: tuple) -> None:
        """DatagramProtocol.datagram_received.

        Parameters:
        data (str): Data.
        address (tuple): Socket address.

        """
        asyncio.get_event_loop().create_task(
            self.process_datagram(data, address))

    async def process_datagram(self: 'SocketEndpoint',
                               data: str, address: tuple) -> None:
        """Process received datagram."""
        if self.address.type == Address.Type.IPV6:
            a = self.address_from_socket_ipv6(address)
        else:
            a = self.address_from_socket_ipv4(address)
        if self.listener:
            self.listener.received_datagram(a, Message(data))

    def error_received(self: 'SocketEndpoint',  exception: Exception) -> None:
        """DatagramProtocol.error_received.

        Parameters:
        exception (Exception): Exception.

        """
        warnings.warn("Endpoint received an error: {0!r}".format(exception))

    @classmethod
    def find_public_address(cls: 'SocketEndpoint') -> List[str]:
        """Find public addresses.

        Return:
        List[str]: List of address as string.

        """
        result = []
        for adapter in ifaddr.get_adapters():
            for ip in adapter.ips:
                if ip.is_ipv6:
                    if ip.ip[0] == "::1":
                        continue
                    result.append(ip.ip[0])
                elif ip.is_ipv4:
                    if ip.ip == "127.0.0.1":
                        continue
                    result.append(ip.ip)
        return result

    @classmethod
    def find_all_address(cls: 'SocketEndpoint') -> List[str]:
        """Find all addresses.

        Return:
        List[str]: List of address as string.

        """
        result = []
        for adapter in ifaddr.get_adapters():
            for ip in adapter.ips:
                if ip.is_ipv6:
                    result.append(ip.ip[0])
                elif ip.is_ipv4:
                    result.append(ip.ip)
        return result

    @classmethod
    def resolve_address(cls: 'SocketEndpoint', address: str) -> Address:
        """Resolve address.

        Address is in the format "hostnameOrIP" or "hostnameOrIP:port".
        You can use a resolvable hostname or an IPv4. If the port is not
        specified the default port 3413 is used.

        If you overwrite create_socket() you have to also overwrite this
        method to resolve address using the appropriate method.

        Parameters:
        address (str): Address to resolve.

        Return:
        Address: Resolved address.

        """
        if not address:
            raise Exception("address is empty")
        delimiter = address.rfind(":")
        port_begin = -1
        flags = socket.AI_NUMERICSERV | socket.AI_ADDRCONFIG

        if delimiter != -1:
            if address[0] == "[":
                """[IPv6]:port"""
                if address[delimiter - 1] != "]":
                    raise Exception("address invalid")
                host = address[1:delimiter - 1]
                port_begin = delimiter + 1
                family = socket.AF_INET6
                flags |= socket.AI_NUMERICHOST
            elif address.find(":") != delimiter:
                """IPv6"""
                host = address
                family = socket.AF_INET6
                flags |= socket.AI_NUMERICHOST
            else:
                """IPv4:port" or "hostname:port"""
                host = address[0:delimiter]
                port_begin = delimiter + 1
                family = socket.AF_UNSPEC
        else:
            """IPv4" or "hostname"""
            host = address
            family = socket.AF_UNSPEC

        port = 3413
        if port_begin != -1:
            port = int(address[port_begin:])
        result = socket.getaddrinfo(host, port, family,
                                    socket.SOCK_DGRAM,
                                    socket.IPPROTO_UDP, flags)

        """there can be more than one address but we use the first one.
        using AI_ADDRCONFIG should give us IPv6 if the host system has
        an IPv6 address otherwise IPv4. should this be a problem we have
        to do this differently.

        according to documentation the first returned address should be
        used since the lookup function has internal sorting logic
        returning the preferred address first.
        """
        info = result[0]
        if info[0] == socket.AF_INET6:
            return SocketEndpoint.address_from_socket_ipv6(info[4])
        elif info[0] == socket.AF_INET:
            return SocketEndpoint.address_from_socket_ipv4(info[4])
        else:
            raise Exception("address invalid: scope resolve wrong family")
