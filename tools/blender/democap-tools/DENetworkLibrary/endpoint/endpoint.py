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

from ..message.message import Message
from .address import Address
from abc import ABC,  abstractmethod


class Endpoint(ABC):

    """Endpoint interface."""

    class Listener(ABC):
        """Endpoint listener interface."""

        def __init__(self: 'Endpoint.Listener'):
            """Create endpoint listener."""
            pass

        @abstractmethod
        def received_datagram(self: 'Endpoint.Listener',
                              address: Address,
                              message: Message) -> None:
            """Datagram received.

            Parameters:
            address (Address): Address of sending client.
            message (Message): Received message.

            """
            pass

    def __init__(self: 'Endpoint') -> None:
        """Create endpoint."""

        self.address = None
        """Address if listening otherwise None."""

    def dispose(self: 'Endpoint') -> None:
        """Dispose of endpoint."""
        pass

    @abstractmethod
    def open(self: 'Endpoint',
             address: Address,
             listener: 'Endpoint.Listener') -> None:
        """Open endpoint delivering events to the provided listener.

        Parameters:
        address (Address): Address to listen on.
        listener (Listener): Listener to invoke.

        """
        pass

    @abstractmethod
    def close(self: 'Endpoint') -> None:
        """Close endpoint if open.

        Stop delivering events to listener provided in the previous open call.

        """
        pass

    @abstractmethod
    def send_datagram(self: 'Endpoint',
                      address: Address,
                      message: Message) -> None:
        """Send datagram.

        Parameters:
        address (Address): Address to send datagram to.
        message (Message): Message to send.

        """
        pass
