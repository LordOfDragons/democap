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

from .endpoint.socket import SocketEndpoint
from .endpoint.address import Address
from .message.message import Message
from .message.real_message import RealMessage
from .message.reader import MessageReader
from .message.writer import MessageWriter
from .endpoint.endpoint import Endpoint
from .state import State
from .state.state_link import StateLink
from .protocol import *
from collections import deque
import logging
from enum import IntEnum, auto
from datetime import datetime, timezone
import asyncio
from time import time_ns


logger = logging.getLogger(__name__)


class Connection(Endpoint.Listener):

    """Network connection.

    Allows clients to connect to a server speaking Drag[en]gine Network
    Protocol.

    To use this class create a subclass overwriting one or more of the
    methods below.

    To start connecting to the server call connectTo() with the IP address
    to connect to in the format "hostnameOrIP" or "hostnameOrIP:port". You
    can use a resolvable hostname or an IPv4. If the port is not specified
    the default port 3413 is used. You can use any port you you like.
    Connecting attempt fails if it takes longer than SetConnectTimeout
    seconds. The default timeout is 3 seconds.

    If connecting to the server succeedes connectionEstablished() is called.
    Overwrite to request linking states and exchanging messages with the
    server. If connection timed out or another error occured
    connectionFailed() is called with the failure reason. Overwrite to
    handle connection failure.

    You can close the connection by calling disconnect(). This calls
    connectionClosed() which you can overwrite. This method is also called
    if the server closes the connection.

    Overwrite createState() to create states requested by the server.
    States synchronize a fixed set of values between the server and the
    client. The client can have read-write or read-only access to the state.
    Create an instance of a subclass of denState to handle individual states.
    It is not necessary to create a subclass of denState if you intent to
    subclass denValue* instead.

    Overwrite messageReceived() to process messages send by the server.

    Call update() in regular intervals to receive and process incoming
    messages as well as updating states. DENetwork does not use internal
    threading giving you full control over threading.

    To get logging implemnent a subclass of denLogger and set the logger
    instance using setLogger(). You can share the logger instance across
    multiple servers and connections.

    """

    class ConnectionState(IntEnum):

        """Connection state."""

        DISCONNECTED = auto()
        """Disconnected."""

        CONNECTING = auto()
        """Connecting."""

        CONNECTED = auto()
        """Connected."""

    class ConnectionFailedReason(IntEnum):

        """Connection failed reason."""

        GENERIC = auto()
        """Generic."""

        TIMEOUT = auto()
        """Timeout."""

        REJECTED = auto()
        """Rejected."""

        NO_COMMON_PROTOCOL = auto()
        """No common protocol."""

        INVALID_MESSAGE = auto()
        """Invalid message."""

    def __init__(self: 'Connection') -> None:
        """Create connection."""

        Endpoint.Listener.__init__(self)
        self._local_address = None
        self._remote_address = None
        self._endpoint = None
        self._real_remote_address = None
        self._connection_state = Connection.ConnectionState.DISCONNECTED
        self._connect_resend_interval = 1.0
        self._connect_timeout = 5.0
        self.reliable_resend_interval = 0.5
        self._reliable_timeout = 3.0
        self._elapsed_connect_resend = 0.0
        self._elapsed_connect_timeout = 0.0
        self._protocol = Protocols.DENETWORK_PROTOCOL
        self._state_links = deque()
        self._modified_state_links = deque()
        self._next_link_id = 0
        self._reliable_messages_send = deque()
        self._reliable_messages_recv = deque()
        self._reliable_number_send = 0
        self._reliable_number_recv = 0
        self._reliable_window_size = 10
        self._parent_server = None
        self._update_task = None
        self._long_message = None
        self._long_message_part_size = 1357
        self._long_link_state_message = None
        self._long_link_state_values = None

    def dispose(self: 'Connection') -> None:
        """Dispose of connection."""
        self._stop_update_task()
        try:
            self._disconnect(False, False)
        except Exception:
            logger.exception("DNL.Connection: Dispose")

        self._reliable_messages_send.clear()
        self._reliable_messages_recv.clear()
        self._reliable_number_send = 0
        self._reliable_number_recv = 0
        self._modified_state_links.clear()
        self._state_links.clear()

        if self._parent_server is None and self._endpoint is not None:
            self._endpoint.dispose()
        self._endpoint = None
        self._parent_server = None

    @property
    def local_address(self: 'Connection') -> Address:
        """Local address.

        Return:
        Address: Address.

        """
        return self._local_address

    @property
    def remote_address(self: 'Connection') -> Address:
        """Remote address.

        Return:
        Address: Address.

        """
        return self._remote_address

    @property
    def connect_resend_interval(self: 'Connection') -> float:
        """Connect resent interval in seconds.

        Return:
        float: Interval in seconds.

        """
        return self._connect_resend_interval

    @connect_resend_interval.setter
    def connect_resend_interval(self: 'Connection', value: float) -> None:
        """Connect resent interval in seconds.

        Parameters:
        value (float): Interval in seconds.

        """
        self._connect_resend_interval = max(value, 0.01)

    @property
    def connect_timeout(self: 'Connection') -> float:
        """Connect timeout in seconds.

        Return:
        float: Timeout in seconds.

        """
        return self._connect_timeout

    @connect_timeout.setter
    def connect_timeout(self: 'Connection', value: float) -> None:
        """Connect resent interval in seconds.

        Parameters:
        value (float): Interval in seconds.

        """
        self._connect_timeout = max(value, 0.01)

    @property
    def reliable_resend_interval(self: 'Connection') -> float:
        """Reliable message resend interval in seconds.

        Return:
        float: Interval in seconds.

        """
        return self._reliable_resend_interval

    @reliable_resend_interval.setter
    def reliable_resend_interval(self: 'Connection', value: float) -> None:
        """Set reliable message resend interval in seconds.

        Parameters:
        value (float): Interval in seconds.

        """
        self._reliable_resend_interval = max(value, 0.01)

    @property
    def reliable_timeout(self: 'Connection') -> float:
        """Reliable message timeout in seconds.

        Return:
        float: Timeout in seconds.

        """
        return self._reliable_timeout

    @reliable_timeout.setter
    def reliable_timeout(self: 'Connection', value: float) -> None:
        """Set reliable message timeout in seconds.

        Parameters:
        value (float): Timeout in seconds.

        """
        self._reliable_timeout = max(value, 0.01)

    @property
    def connection_state(self: 'Connection') -> 'Connection.ConnectionState':
        """Connection state.

        Return:
        Connection.ConnectionState: Connection state.

        """
        return self._connection_state

    @property
    def connected(self: 'Connection') -> bool:
        """Connection to a remote host is established.

        Return:
        bool: Connected.

        """
        return self._connection_state == Connection.ConnectionState.CONNECTED

    def connect_to(self: 'Connection',  address: str) -> None:
        """Connect to connection object on host at address.

        Parameters:
        address (str): Address to connect to.

        """
        if self._endpoint is not None or (
                self._connection_state
                != Connection.ConnectionState.DISCONNECTED):
            raise Exception('already connected')

        try:
            resolved = self.resolve_address(address)
            self._endpoint = self.create_endpoint()
            if resolved.type == Address.Type.IPV6:
                self._endpoint.open(Address.ipv6_any(), self)
            else:
                self._endpoint.open(Address.ipv4_any(), self)

            self._local_address = str(self._endpoint.address)

            message = Message()
            with MessageWriter(message) as w:
                w.write_byte(CommandCodes.CONNECTION_REQUEST.value)
                w.write_ushort(1)  # version
                w.write_ushort(Protocols.DENETWORK_PROTOCOL.value)
            self._real_remote_address = resolved
            self._remote_address = address
            logger.info("DNL.Connection: Connect to %s",
                        str(self._real_remote_address))

            self._endpoint.send_datagram(resolved, message)

            self._connection_state = Connection.ConnectionState.CONNECTING
            self._elapsed_connect_resend = 0.0
            self._elapsed_connect_timeout = 0.0
            self._start_update_task()
        except Exception as e:
            self.disconnect()
            raise e

    def resolve_address(self: 'Connection', address: str) -> str:
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

    def disconnect(self: 'Connection') -> None:
        """Disconnect from remote connection if connected."""
        logger.info("DNL.Connection: Disconnect")
        self._disconnect(True, False)

    def send_message(self: 'Connection', message: Message) -> None:
        """Send message to remote connection if connected.

        The message can be queued and send at a later time to optimize
        throughput. The message will be not delayed longer than the given
        amount of milliseconds. The message is send unreliable and it is
        acceptable for the message to get lost due to transmission failure.

        Sending messages is not reliable. Messages can be potentially lost
        and you will not be notified if this occurs. Use this method for
        messages where loosing them is fine. This is typically the case for
        messages repeating in regular intervals so missing one of them is
        not a problem.

        Parameters:
        message (Message): Message to send. Message can contain any kind of
                           byte sequence. The most simply way to build
                           messages is using.

        """
        if message is None:
            raise Exception("message is None")
        if len(message.data) < 1:
            raise Exception("message has 0 length")
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            raise Exception("not connected")

        request = Message()
        with MessageWriter(request) as w:
            w.write_byte(CommandCodes.MESSAGE.value)
            w.write_message(message)
        self._endpoint.send_datagram(self._real_remote_address, request)

    def send_reliable_message(self: 'Connection', message: Message) -> None:
        """Send reliable message to remote connection if connected.

        The message is append to already waiting reliable messages and send
        as soon as possible. Reliable messages always arrive in the same
        order they have been queued.

        This messages is guaranteed to be delivered in the order they have
        been send. Use this for messages which you can not afford to loose.
        This is typically the case for events happening once like a player
        activating an item or opening a door.

        Parameters:
        message (Message): Message to send. Message can contain any kind of
                           byte sequence. The most simply way to build
                           messages is using.

        """
        if message is None:
            raise Exception("message is None")
        data_len = len(message.data)
        if data_len < 1:
            raise Exception("message has 0 length")
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            raise Exception("not connected")

        part_count = (data_len - 1) // self._long_message_part_size + 1
        if part_count > 1:
            data = message.data
            offset = 0
            for i in range(part_count):
                real_message = RealMessage()
                real_message.type = CommandCodes.RELIABLE_MESSAGE_LONG
                real_message.number = (self._reliable_number_send
                                    + len(self._reliable_messages_send)) % 65535
                real_message.state = RealMessage.State.PENDING

                flags = 0
                if i == 0:
                    flags = flags | LongMessageFlags.FIRST
                if i == part_count - 1:
                    flags = flags | LongMessageFlags.LAST

                part_len = min(self._long_message_part_size, data_len - offset)

                with MessageWriter(real_message.message) as w:
                    w.write_byte(CommandCodes.RELIABLE_MESSAGE_LONG.value)
                    w.write_ushort(real_message.number)
                    w.write_byte(flags)
                    w.write(data, offset, part_len)

                self._add_reliable_message(real_message)
                offset = offset + part_len
            self._send_pending_reliables()

        else:
            real_message = RealMessage()
            real_message.type = CommandCodes.RELIABLE_MESSAGE
            real_message.number = (self._reliable_number_send
                                + len(self._reliable_messages_send)) % 65535
            real_message.state = RealMessage.State.PENDING

            with MessageWriter(real_message.message) as w:
                w.write_byte(CommandCodes.RELIABLE_MESSAGE.value)
                w.write_ushort(real_message.number)
                w.write_message(message)

            self._add_reliable_message(real_message)

    def link_state(self: 'Connection',  message: Message, state: State,
                   read_only: bool) -> None:
        """Link network state to remote network state.

        The message contains information for the remote system to know what
        state to link to. The request is queued and carried out as soon as
        possible. The local state is considered the master state and the
        remote state the slave state. By default only the master state can
        apply changes.

        Parameters:
        message (Message): Message to send. Message can contain any kind of
                           byte sequence. The most simply way to build
                           messages is using MessageWriter.
        state (State): State to link.
        read_only (bool): If True client receives a read-only link otherwise
                          a read-write link. Use true if the state to link is
                          a server managed state the client is only allowed
                          to read. Use false if this is a state the client
                          has to change.

        """
        if message is None:
            raise Exception("message is None")
        if len(message.data) < 1:
            raise Exception("message has 0 length")
        if len(message.data) > 0xffff:
            raise Exception("message is too long")
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            raise Exception("not connected")
        if state is None:
            raise Exception("state is None")

        """check if a link exists with this state already that is not broken"""
        state_link = next((x for x in self._state_links
                          if x.state == state), None)

        if state_link is not None and (state_link.link_state
                                       != StateLink.LinkState.DOWN):
            raise Exception("link with state present")

        """create the link if absent, assign it new identifier and add it"""
        if state_link is None:
            self._last_next_link_id = self._next_link_id
            found = next((x for x in self._state_links
                         if x.identifier == self._next_link_id),  None)
            if found is not None:
                self._next_link_id = (self._next_link_id + 1) % 65535
                if self._next_link_id == self._last_next_link_id:
                    raise Exception("too many state links")
            state_link = StateLink(self, state)
            state_link.identifier = self._next_link_id
            self._state_links.append(state_link)
            state.links.append(state_link)

        """add message"""
        real_message = RealMessage()
        real_message.type = CommandCodes.RELIABLE_LINK_STATE
        real_message.number = (self._reliable_number_send
                               + len(self._reliable_messages_send)) % 65535
        real_message.state = RealMessage.State.PENDING

        with MessageWriter(real_message.message) as w:
            w.write_byte(CommandCodes.RELIABLE_LINK_STATE.value)
            w.write_ushort(real_message.number)
            w.write_ushort(state_link.identifier)
            w.write_byte(1 if read_only else 0)  # flags readOnly=0x1
            w.write_ushort(len(message.data))
            w.write_message(message)
            state.link_write_values_with_verify(w)

        self._add_reliable_message(real_message)
        state_link.link_state = StateLink.LinkState.LISTENING

    def _add_reliable_message(self: 'Connection',
                              message: RealMessage) -> None:
        """Add reliable message and send it if fits into send window."""
        self._reliable_messages_send.append(message)

        """if the message fits into the window send it right now"""
        if len(self._reliable_messages_send) <= self._reliable_window_size:
            self._endpoint.send_datagram(self._real_remote_address,
                                         message.message)
            message.state = RealMessage.State.SEND
            message.elapsed_resend = 0.0
            message.elapsed_timeout = 0.0

    def received_datagram(self: 'Connection', address: Address,
                          message: Message) -> None:
        """Datagram received."""
        if self._connection_state == Connection.ConnectionState.DISCONNECTED:
            return
        if self._parent_server is not None:
            return
        try:
            self.process_datagram(MessageReader(message))
        except Exception as e:
            logger.error("DNL.Connection: Received datagram", exc_info=e)

    def create_endpoint(self: 'Connection') -> Endpoint:
        """Create endpoint.

        Default implementation creates an instance of DatagramChannelEndpoint
        which is a UDP socket. If you have to accept clients using a different
        transportation method overwrite method to create an instance of a class
        implementing Endpoint interface providing the required capabilities.

        Return:
        Endpoint: Endpoint.

        """
        return SocketEndpoint()

    def connection_established(self: 'Connection') -> None:
        """Connection established. Callback for subclass."""
        logger.info("DNL.Connection: Connection established")

    def connection_failed(self: 'Connection',
                          reason: 'Connection.ConnectionFailedReason') -> None:
        """Connection failed or timeout out. Callback for subclass."""
        logger.info("DNL.Connection: Connection failed")

    def connection_closed(self: 'Connection') -> None:
        """Connection closed.

        This is called if disconnect() is called or the server closes
        the connection. Callback for subclass.

        """
        logger.info("DNL.Connection: Connection closed")

    def message_received(self: 'Connection', message: Message) -> None:
        """Message received. Called asynchronously. Callback for subclass.

        Parameters:
        message(Message) Received message. Object can be stored for later use.

        """
        pass

    def message_progress(self: 'Connection', bytes_received: int) -> None:
        """Message received. Called asynchronously. Callback for subclass.

        Parameters:
        bytes_received(int) Amount of bytes received so far.

        """
        pass

    def create_state(self: 'Connection', message: Message,
                     read_only: bool) -> State:
        """Host send state to link.

        Overwrite to create states requested by the server. States
        synchronize a fixed set of values between the server and the client.
        The client can have read-write or read-only access to the state.
        Create an instance of a subclass of denState to handle individual
        states. It is not necessary to create a subclass of denState if you
        intent to subclass Value* instead.

        If you do not support a state requested by the server you can return
        None. In this case the state is not linked and state values are not
        synchronized. You can not re-link a state later on if you rejected
        it here. If you need re-linking a state make the server resend the
        link request. This will be a new state link.

        Return:
        State State or None to reject.

        """
        return

    @property
    def parent_server(self: 'Connection') -> 'Server':
        """Server owning this connection or None if client side.

        Return:
        Server Server owning this connection.

        """
        return self._parent_server

    @property
    def endpoint(self: 'Connection') -> Endpoint:
        """Endpoint or None if not connected.

        Return:
        Endpoint Endpoint

        """
        return self._endpoint

    @property
    def protocol(self: 'Connection') -> Protocols:
        """Connection protocol.

        Return:
        Protocols Connection protocol.

        """
        return self._protocol

    def matches(self: 'Connection', endpoint: Endpoint,
                address: Address) -> bool:
        """Connection matches endpoint and address.

        Parameters:
        endpoint (Endpoint) Endpoint.
        address (Address) Address.

        Return:
        bool Connection matches endpoint and address.

        """
        return (self._endpoint == endpoint and address
                == self._real_remote_address)

    def process_datagram(self: 'Connection', reader: MessageReader) -> None:
        """Process datagram.

        Parameters:
        reader (MessageReader) Message reader.

        """
        command = CommandCodes(reader.read_byte())
        if command == CommandCodes.CONNECTION_ACK:
            self._process_connection_ack(reader)
        elif command == CommandCodes.CONNECTION_CLOSE:
            self._process_connection_close(reader)
        elif command == CommandCodes.MESSAGE:
            self._process_message(reader)
        elif command == CommandCodes.RELIABLE_MESSAGE:
            self._process_reliable_message(reader)
        elif command == CommandCodes.RELIABLE_LINK_STATE:
            self._process_reliable_link_state(reader)
        elif command == CommandCodes.RELIABLE_ACK:
            self._process_reliable_ack(reader)
        elif command == CommandCodes.LINK_UP:
            self._process_link_up(reader)
        elif command == CommandCodes.LINK_DOWN:
            self._process_link_down(reader)
        elif command == CommandCodes.LINK_UPDATE:
            self._process_link_update(reader)
        elif command == CommandCodes.RELIABLE_MESSAGE_LONG:
            self._process_reliable_message_long(reader)
        elif command == CommandCodes.RELIABLE_LINK_STATE_LONG:
            self._process_reliable_link_state_long(reader)

    def accept_connection(self: 'Connection', server: 'Server',
                          endpoint: Endpoint, address: Address,
                          protocol: Protocols) -> None:
        """For internal use only."""
        self._endpoint = endpoint
        self._real_remote_address = address
        self._remote_address = str(address)
        self._connection_state = Connection.ConnectionState.CONNECTED
        self._elapsed_connect_resend = 0.0
        self._elapsed_connect_timeout = 0.0
        self._protocol = protocol
        self._parent_server = server
        self._start_update_task()
        self.connection_established()

    def _disconnect(self: 'Connection', notify: bool,
                    remote_closed: bool) -> None:
        """Disconnect.

        Parameters:
        notify (bool): Call callbacks.
        remote_closed (bool): Remote closed connection.

        """
        if self._endpoint is None:
            return
        if self._connection_state == Connection.ConnectionState.DISCONNECTED:
            return

        if self._connection_state == Connection.ConnectionState.CONNECTED:
            if remote_closed:
                logger.info("DNL.Connection: Remove closed connection")
            else:
                logger.info("DNL.Connection: Disconnecting")

                self._update_states()
                self._send_pending_reliables()

                message = Message()
                with MessageWriter(message) as w:
                    w.write_byte(CommandCodes.CONNECTION_CLOSE.value)
                self._endpoint.send_datagram(self._real_remote_address,
                                             message)

        self._clear_states()
        self._reliable_messages_recv.clear()
        self._reliable_messages_send.clear()
        self.reliable_number_send = 0
        self.reliable_number_recv = 0
        self._long_message = None
        self._long_link_state_message = None
        self._long_link_state_values = None

        self._close_endpoint()
        logger.info("DNL.Connection: Connection closed")
        if notify:
            self.connection_closed()

        self._remove_connection_from_parent_server()

    def _clear_states(self: 'Connection') -> None:
        """Clear states."""
        self._modified_state_links.clear()
        for lnk in self._modified_state_links:
            state = lnk.state
            if state is None:
                continue
            try:
                state.links.remove(lnk)
            except ValueError:
                continue  # not in list
            lnk.drop_state()
        self._state_links.clear()

    def _close_endpoint(self: 'Connection') -> None:
        """Close endpoint."""
        self._stop_update_task()
        self._connection_state = Connection.ConnectionState.DISCONNECTED
        self.elapsed_connect_resend = 0.0
        self.elapsed_connect_timeout = 0.0
        if self._parent_server is None and self._endpoint is not None:
            self._endpoint.dispose()
        self._endpoint = None

    def _remove_connection_from_parent_server(self: 'Connection') -> None:
        """Remove connection from parent server."""
        if self._parent_server is None:
            return
        self._close_endpoint()
        try:
            self._parent_server.connections.remove(self)
        except ValueError:
            pass  # not in list
        self._parent_server = None

    def _update_states(self: 'Connection') -> None:
        """Synchronized by caller."""
        link_count = len(self._modified_state_links)
        if link_count == 0:
            return

        changed_count = sum(1 for x in self._modified_state_links
                            if x.link_state == StateLink.LinkState.UP
                            and x.changed)
        if changed_count == 0:
            return
        changed_count = min(changed_count, 255)

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(CommandCodes.LINK_UPDATE.value)
            w.write_byte(changed_count)

            index = 0
            count = len(self._modified_state_links)
            while index < count and changed_count > 0:
                link = self._modified_state_links[index]
                if (link.link_state != StateLink.LinkState.UP
                        or not link.changed):
                    index = index + 1
                    continue

                w.write_ushort(link.identifier)
                state = link.state
                if state is None:
                    del self._modified_state_links[index]
                    count = count - 1
                    continue

                state.link_write_values_link(w, link)

                del self._modified_state_links[index]
                count = count - 1
                changed_count = changed_count - 1
        self._endpoint.send_datagram(self._real_remote_address, message)

    def _update_timeouts(self: 'Connection',  elapsed_time: float) -> None:
        """Synchronized by caller."""
        if self._connection_state == Connection.ConnectionState.CONNECTED:
            for m in self._reliable_messages_send:
                if m.state != RealMessage.State.SEND:
                    continue

                m.elapsed_timeout = m.elapsed_timeout + elapsed_time
                if m.elapsed_timeout > self._reliable_timeout:
                    logger.error("DNL.Connection: Reliable message timeout")
                    self.disconnect()
                    return

                m.elapsed_resend = m.elapsed_resend + elapsed_time
                if m.elapsed_resend > self._reliable_resend_interval:
                    m.elapsed_resend = 0.0
                    self._endpoint.send_datagram(
                        self._real_remote_address, m.message)
        elif self._connection_state == Connection.ConnectionState.CONNECTING:
            self._elapsed_connect_timeout = (
                self._elapsed_connect_timeout + elapsed_time)
            if self._elapsed_connect_timeout > self._connect_timeout:
                self._close_endpoint()
                logger.info("DNL.Connection: Connection failed (timeout)")
                self.connection_failed(
                    Connection.ConnectionFailedReason.TIMEOUT)

            self._elapsed_connect_resend = (
                self._elapsed_connect_resend + elapsed_time)
            if self._elapsed_connect_resend > self._connect_resend_interval:
                logger.debug("DNL.Connection: Resent connection request")
                self._elapsed_connect_resend = 0.0

                message = Message()
                with MessageWriter(message) as w:
                    w.write_byte(CommandCodes.CONNECTION_REQUEST.value)
                    w.write_ushort(1)  # version
                    w.write_ushort(Protocols.DENETWORK_PROTOCOL.value)
                self._endpoint.send_datagram(
                    self._real_remote_address, message)

    def add_modified_state_link(self: 'Connection',
                                state_link: StateLink) -> None:
        """Add state link.

        Parameters:
        state_link (StateLink) StateLink to add.

        """
        self._modified_state_links.append(state_link)

    def _process_queued_messages(self: 'Connection') -> None:
        """Process queued messages."""
        while True:
            message = next((x for x in self._reliable_messages_recv
                           if x.number == self._reliable_number_recv), None)
            if message is None:
                break

            if message.type == CommandCodes.RELIABLE_MESSAGE:
                self._process_reliable_message_message(
                    MessageReader(message.message))
            elif message.type == CommandCodes.RELIABLE_LINK_STATE:
                self._process_link_state(MessageReader(message.message))
            elif message.type == CommandCodes.RELIABLE_MESSAGE_LONG:
                self._process_reliable_message_message_long(
                    MessageReader(message.message))
            elif message.type == CommandCodes.RELIABLE_LINK_STATE_LONG:
                self._process_link_state_long(MessageReader(message.message))

            self._reliable_messages_recv.remove(message)
            self._reliable_number_recv = (
                self._reliable_number_recv + 1) % 65535

    def _process_connection_ack(self: 'Connection',
                                reader: MessageReader) -> None:
        """Process connection ack."""
        if self._connection_state != Connection.ConnectionState.CONNECTING:
            return
        ack = ConnectionAck(reader.read_byte())
        if ack == ConnectionAck.ACCEPTED:
            self._protocol = Protocols(reader.read_ushort())
            self._connection_state = Connection.ConnectionState.CONNECTED
            self._elapsed_connect_resend = 0.0
            self._elapsed_connect_timeout = 0.0
            logger.info("DNL.Connection: Connection established")
            self.connection_established()
        elif ack == ConnectionAck.REJECTED:
            self._close_endpoint()
            logger.info("DNL.Connection: Connection failed (rejected)")
            self.connection_failed(Connection.ConnectionFailedReason.REJECTED)
        elif ack == ConnectionAck.NO_COMMON_PROTOCOL:
            self._close_endpoint()
            logger.info("DNL.Connection: %s",
                        "Connection failed (no common protocol)")
            self.connection_failed(
                Connection.ConnectionFailedReason.NO_COMMON_PROTOCOL)
        else:
            self._close_endpoint()
            logger.info("DNL.Connection: Connection failed (invalid message)")
            self.connection_failed(
                Connection.ConnectionFailedReason.INVALID_MESSAGE)

    def _process_connection_close(self: 'Connection',
                                  reader: MessageReader) -> None:
        """Process connection close."""
        self._disconnect(True, True)

    def _process_message(self: 'Connection',
                         reader: MessageReader) -> None:
        """Process message."""
        message = Message(bytearray(len(reader.data) - reader.position))
        reader.read_message(message)
        self.message_received(message)

    def _process_reliable_message(self: 'Connection',
                                  reader: MessageReader) -> None:
        """Process reliable message."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        number = reader.read_ushort()
        if number < self._reliable_number_recv:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size) % 65535:
                return
        else:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size):
                return

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(CommandCodes.RELIABLE_ACK.value)
            w.write_ushort(number)
            w.write_byte(ReliableAck.SUCCESS.value)
        self._endpoint.send_datagram(self._real_remote_address, message)

        if number == self._reliable_number_recv:
            self._process_reliable_message_message(reader)
            self._reliable_number_recv = (
                self._reliable_number_recv + 1) % 65535
            self._process_queued_messages()
        else:
            self._add_reliable_receive(
                CommandCodes.RELIABLE_MESSAGE, number, reader)

    def _process_reliable_message_message(self: 'Connection',
                                          reader: MessageReader) -> None:
        """Process reliable message message."""
        message = Message(bytearray(len(reader.data) - reader.position))
        reader.read_message(message)
        self.message_received(message)

    def _process_reliable_ack(self: 'Connection',
                              reader: MessageReader) -> None:
        """Process reliable ack."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        number = reader.read_ushort()
        ack = ReliableAck(reader.read_byte())

        message = next((m for m in self._reliable_messages_send
                       if m.number == number), None)
        if message is None:
            return

        if ack == ReliableAck.SUCCESS:
            message.state = RealMessage.State.DONE
            self._remove_send_reliables_done()
        elif ack == ReliableAck.FAILED:
            logger.debug("DNL.Connection: Reliable ACK failed, resend")
            message.elapsed_resend = 0.0
            self._endpoint.send_datagram(
                self._real_remote_address, message.message)

    def _process_reliable_link_state(self: 'Connection',
                                     reader: MessageReader) -> None:
        """Process reliable link state."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        number = reader.read_ushort()
        if number < self._reliable_number_recv:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size) % 65535:
                return
        else:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size):
                return

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(CommandCodes.RELIABLE_ACK.value)
            w.write_ushort(number)
            w.write_byte(ReliableAck.SUCCESS.value)
        self._endpoint.send_datagram(self._real_remote_address, message)

        if number == self._reliable_number_recv:
            self._process_link_state(reader)
            self._reliable_number_recv = (
                self._reliable_number_recv + 1) % 65535
            self._process_queued_messages()
        else:
            self._add_reliable_receive(
                CommandCodes.RELIABLE_LINK_STATE, number, reader)

    def _process_link_up(self: 'Connection',
                         reader: MessageReader) -> None:
        """Process link up."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        identifier = reader.read_ushort()
        link = next((lnk for lnk in self._state_links
                    if lnk.identifier == identifier), None)
        if link is None or link.link_state != StateLink.LinkState.LISTENING:
            return
        link.link_state = StateLink.LinkState.UP

    def _process_link_down(self: 'Connection',
                           reader: MessageReader) -> None:
        """Process link down."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        identifier = reader.read_ushort()
        link = next((lnk for lnk in self._state_links
                    if lnk.identifier == identifier), None)
        if link is None or link.link_state != StateLink.LinkState.UP:
            return
        link.link_state = StateLink.LinkState.DOWN

    def _process_link_state(self: 'Connection',
                            reader: MessageReader) -> None:
        """Process link state."""
        identifier = reader.read_ushort()
        read_only = reader.read_byte() == 1  # flags: 0x1=readOnly

        link = next((lnk for lnk in self._state_links
                    if lnk.identifier == identifier), None)
        if link is None or link.link_state != StateLink.LinkState.DOWN:
            pass  # raise Exception("Link with identifier exists already")

        """create linked network state"""
        message = Message(bytearray(reader.read_ushort()))
        reader.read_message(message)

        state = self.create_state(message, read_only)

        command = CommandCodes.LINK_DOWN
        if state is not None:
            if (not state.link_read_and_verify_all_values(reader)
                    or link is not None):
                return

            link = StateLink(self, state)
            link.identifier = identifier
            self._state_links.append(link)
            state.links.append(link)

            link.link_state = StateLink.LinkState.UP
            command = CommandCodes.LINK_UP

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(command)
            w.write_ushort(identifier)
        self._endpoint.send_datagram(self._real_remote_address, message)

    def _process_link_update(self: 'Connection',
                             reader: MessageReader) -> None:
        """Process link update."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        count = reader.read_byte()
        for _i in range(count):
            identifier = reader.read_ushort()

            link = next((lnk for lnk in self._state_links
                        if lnk.identifier == identifier), None)
            if link is None or link.link_state != StateLink.LinkState.UP:
                return

            state = link.state
            if state is None:
                return
            state.link_read_values(reader, link)

    def _process_reliable_message_long(self: 'Connection',
                                       reader: MessageReader) -> None:
        """Process long reliable message."""
        if self._connection_state != Connection.ConnectionState.CONNECTED:
            return

        number = reader.read_ushort()
        if number < self._reliable_number_recv:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size) % 65535:
                return
        else:
            if number >= (self._reliable_number_recv
                          + self._reliable_window_size):
                return

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(CommandCodes.RELIABLE_ACK.value)
            w.write_ushort(number)
            w.write_byte(ReliableAck.SUCCESS.value)
        self._endpoint.send_datagram(self._real_remote_address, message)

        if number == self._reliable_number_recv:
            self._process_reliable_message_message_long(reader)
            self._reliable_number_recv = (
                self._reliable_number_recv + 1) % 65535
            self._process_queued_messages()
        else:
            self._add_reliable_receive(
                CommandCodes.RELIABLE_MESSAGE_LONG, number, reader)

    def _process_reliable_message_message_long(self: 'Connection',
                                               reader: MessageReader) -> None:
        """Process long reliable message message."""
        flags = reader.read_byte()
        if flags & LongMessageFlags.FIRST:
            self._long_message = Message()
        if self._long_message is None:
            return

        data_len = len(reader.data) - reader.position
        reader.read_message_append(self._long_message, data_len)

        if flags & LongMessageFlags.LAST:
            message = self._long_message
            self._long_message = None

            message.timestamp = datetime.now(timezone.utc)
            self.message_received(message)
        else:
            self.message_progress(len(self._long_message.data))

    def _process_link_state_long(self: 'Connection',
                                 reader: MessageReader) -> None:
        """Process long link state."""
        identifier = reader.read_ushort()
        flags = reader.read_byte()

        link = next((lnk for lnk in self._state_links
                    if lnk.identifier == identifier), None)
        if link is None or link.link_state != StateLink.LinkState.DOWN:
            pass

        if flags & LongLinkStateFlags.FIRST:
            self._long_link_state_message = Message()
            self._long_link_state_values = Message()
        if self._long_link_state_message is None:
            return
        if self._long_link_state_values is None:
            return
        
        data_len = reader.read_ushort()
        reader.read_message_append(self._long_link_state_message, data_len)
        
        data_len = len(reader.data) - reader.position
        reader.read_message_append(self._long_link_state_values, data_len)

        if not (flags & LongLinkStateFlags.LAST):
            return

        message = self._long_link_state_message
        self._long_link_state_message = None

        values = self._long_link_state_values
        self._long_link_state_values = None

        read_only = (flags & LongLinkStateFlags.READ_ONLY) != 0

        """create linked network state"""
        state = self.create_state(message, read_only)

        command = CommandCodes.LINK_DOWN
        if state is not None:
            if (not state.link_read_and_verify_all_values(MessageReader(message))
                    or link is not None):
                return

            link = StateLink(self, state)
            link.identifier = identifier
            self._state_links.append(link)
            state.links.append(link)

            link.link_state = StateLink.LinkState.UP
            command = CommandCodes.LINK_UP

        message = Message()
        with MessageWriter(message) as w:
            w.write_byte(command)
            w.write_ushort(identifier)
        self._endpoint.send_datagram(self._real_remote_address, message)

    def _add_reliable_receive(self: 'Connection', command: CommandCodes,
                              number: int, reader: MessageReader) -> None:
        """Add reliable receive."""
        message = RealMessage()
        message.message.data = bytearray(len(reader.data) - reader.position)
        reader.read_message(message.message)

        message.type = command
        message.number = number
        message.state = RealMessage.State.DONE

        self._reliable_messages_recv.append(message)

    def _remove_send_reliables_done(self: 'Connection') -> None:
        """Remove send reliables done."""
        any_removed = False
        while self._reliable_messages_send:
            if self._reliable_messages_send[0].state != RealMessage.State.DONE:
                break
            self._reliable_messages_send.pop()
            self._reliable_number_send = (
                self._reliable_number_send + 1) % 65535
            any_removed = True
        if any_removed:
            self._send_pending_reliables()

    def _send_pending_reliables(self: 'Connection') -> None:
        """Send pending reliables."""
        counter = 0
        for m in self._reliable_messages_send:
            if counter == self._reliable_window_size:
                break
            counter = counter + 1

            if m.state != RealMessage.State.PENDING:
                continue

            self._endpoint.send_datagram(self._real_remote_address, m.message)

            m.state = RealMessage.State.SEND
            m.elapsed_resend = 0.0
            m.elapsed_timeout = 0.0

    async def _task_update(self: 'Connection') -> None:
        """Update task."""
        last_time = time_ns()
        while True:
            await asyncio.sleep(0.005)
            if self._update_task is None:
                break
            cur_time = time_ns()
            elapsed = 1e-9 * (cur_time - last_time)
            last_time = cur_time
            try:
                self._update_timeouts(elapsed)
                self._update_states()
            except Exception:
                logger.exception("DNL.Connection: Connection timer update")

    def _start_update_task(self: 'Connection') -> None:
        """Start update task."""
        if self._update_task is None:
            self._update_task = asyncio.get_event_loop().create_task(
                self._task_update())

    def _stop_update_task(self: 'Connection') -> None:
        """Stop update task."""
        if self._update_task is not None:
            self._update_task.cancel()
            self._update_task = None
