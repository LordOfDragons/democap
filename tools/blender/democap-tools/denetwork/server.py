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

from typing import List, Deque
from .connection import Connection
from .endpoint.socket import SocketEndpoint
from .endpoint.address import Address
from .message.message import Message
from .message.reader import MessageReader
from .message.writer import MessageWriter
from .endpoint.endpoint import Endpoint
from .protocol import CommandCodes, ConnectionAck, Protocols
from collections import deque
import logging


class Server(Endpoint.Listener):

    """Network server.

    Allows clients speaking Drag[en]gine Network Protocol to connect.

    To use this class create a subclass and overwrite createConnection()
    and clientConnected(). The method createConnection() method creates
    a Connection instance for each connecting client. By overwriting this
    method you can create a subclass of Connection handling the client.
    Overwriting clientConnected() allows to communicate with a connecting
    client to link states and exchanging messages.

    The default implementation connects by creating a UDP socket. If you
    have to accept clients using a different transportation method overwrite
    createSocket() to create a class instance implementing Endpoint interface
    providing the required capabilities. Usually this is not required.

    To start listening call ListenOn with the IP address to listen on in the
    format "hostnameOrIP" or "hostnameOrIP:port". You can use a resolvable
    hostname or an IPv4. If the port is not specified the default port 3413
    is used. You can use any port you you like.

    """

    def __init__(self: 'Server') -> None:
        """Create server."""

        Endpoint.Listener.__init__(self)
        self._address = None
        self._endpoint = None
        self._listening = False
        self._connections = deque()

    def dispose(self: 'Server') -> None:
        """Dispose of server."""
        self.stop_listening()

    @property
    def address(self: 'Server') -> str:
        """Address.

        Return:
        str: Address.

        """
        return self._address

    @property
    def listening(self: 'Server') -> bool:
        """Server is listening for connections.

        Return:
        bool: Listening.

        """
        return self._listening

    def listen_on(self: 'Server', address: str) -> None:
        """Start listening on address for incoming connections.

        Parameters:
        address (str): address Address is in the format "hostnameOrIP" or
                       "hostnameOrIP:port". You can use a resolvable hostname
                       or an IPv4. If the port is not specified the default
                       port 3413 is used. You can use any port you you like.

        """
        if self._listening:
            raise Exception("Already listening")

        use_address = address
        if use_address == "*":
            addrs = self.find_public_address()
            if addrs:
                logging.info("Found public address: %s",  ", ".join(addrs))
                use_address = addrs[0]
            else:
                logging.info("No public address found. Using localhost")
                use_address = "127.0.0.1"

        self._endpoint = self.create_endpoint()
        self._endpoint.open(self.resolve_address(use_address), self)

        logging.info("Server: Listening on %s", self._endpoint.address)
        self._listening = True

    def stop_listening(self: 'Server') -> None:
        """Stop listening."""
        if self._listening:
            for connection in list(self._connections):
                connection.dispose()
            self._connections.clear()
            if self._endpoint is not None:
                self._endpoint.dispose()
                self._endpoint = None
            self._listening = False

    @property
    def connections(self: 'Server') -> Deque[Connection]:
        """Connections.

        Do not modify the linked list. Use it read only.

        Return:
        Deque[Connection]: Connections.

        """
        return self._connections

    def received_datagram(self: 'Server', address: Address,
                          message: Message) -> None:
        """Datagram received."""
        connection = None
        try:
            reader = MessageReader(message)
            connection = next((c for c in self._connections if
                              c.matches(self._endpoint, address)), None)
            if connection is not None:
                connection.process_datagram(reader)
            else:
                command = CommandCodes(reader.read_byte())
                if command == CommandCodes.CONNECTION_REQUEST:
                    self._process_connection_request(address, reader)
                """else: ignore invalid package"""
        except Exception:
            logging.exception("failed processing received datagra")

    def create_connection(self: 'Server') -> Connection:
        """Create connection for each connecting client.

        Overwrite this method to create an instance of a custom subclass of
        Connection handling the client.

        Default implementation creates instance of Connection.

        Return:
        Connection: Connection.

        """
        return Connection()

    def create_endpoint(self: 'Server') -> Endpoint:
        """Create endpoint.

        Default implementation creates an instance of DatagramChannelEndpoint
        which is a UDP socket. If you have to accept clients using a different
        transportation method overwrite method to create an instance of a class
        implementing Endpoint interface providing the required capabilities.

        Return:
        Endpoint: Endpoint.

        """
        return SocketEndpoint()

    def find_public_address(self: 'Server') -> List[str]:
        """Find public addresses.

        Return:
        List[str]: List of address as string.

        """
        return SocketEndpoint.find_public_address()

    def resolve_address(self: 'Server', address: str) -> str:
        """Resolve address.

        Address is in the format "hostnameOrIP" or "hostnameOrIP:port".
        You can use a resolvable hostname or an IPv4. If the port is not
        specified the default port 3413 is used.

        If you overwrite create_socket() you have to also overwrite this
        method to resolve address using the appropriate method.

        Parameters:
        address (str): Address to resolve.

        Return:
        str: Resolved address.

        """
        return SocketEndpoint.resolve_address(address)

    def client_connected(self: 'Server', connection: Connection) -> None:
        """Client connected.

        Overwrite to communicate with a connecting client to link states
        and exchange messages.

        Parameters:
        connection (Connection): Connection of connecting client.

        """
        pass

    def _process_connection_request(self: 'Server', address: Address,
                                    reader: MessageReader) -> None:
        """Process connection request."""
        if not self._listening:
            message = Message()
            with MessageWriter(message) as w:
                w.write_byte(CommandCodes.CONNECTION_ACK.value)
                w.write_byte(ConnectionAck.REJECTED.value)
            self._endpoint.send_datagram(address, message)
            return

        """find best protocol to speak"""
        count = reader.read_ushort()
        client_protocols = [reader.read_ushort() for i in range(count)]

        if Protocols.DENETWORK_PROTOCOL.value not in client_protocols:
            message = Message()
            with MessageWriter(message) as w:
                w.write_byte(CommandCodes.CONNECTION_ACK.value)
                w.write_byte(ConnectionAck.NO_COMMON_PROTOCOL.value)
            self._endpoint.send_datagram(address, message)
            return

        protocol = Protocols.DENETWORK_PROTOCOL

        """create connection"""
        connection = self.create_connection()
        connection.accept_connection(self, self._endpoint, address, protocol)
        self._connections.append(connection)

        """send back result"""
        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(CommandCodes.CONNECTION_ACK.value)
            w.write_byte(ConnectionAck.ACCEPTED.value)
            w.write_ushort(protocol.value)
        self._endpoint.send_datagram(address, message)

        logging.info("Server: Client connected from %s", address)
        self.client_connected(connection)
