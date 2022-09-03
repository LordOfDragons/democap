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

from .state_link import StateLink
from ..value.value import Value
from ..message.reader import MessageReader
from ..message.writer import MessageWriter
from ..protocol import ValueTypes
from typing import List, Deque
from collections import deque
import logging


logger = logging.getLogger(__name__)


class State:

    """Network state."""

    def __init__(self: 'State', read_only: bool) -> None:
        """Create state.

        Parameters:
        read_only (bool): State is read-only.

        """

        self._read_only = read_only
        self._values = []
        self._links = deque()

    def dispose(self: 'State') -> None:
        """Dispose of state."""
        for link in self._links:
            link.drop_state()

    def update(self: 'State') -> None:
        """Update state."""
        pass

    @property
    def read_only(self: 'State') -> bool:
        """State is read-only.

        Return:
        bool: State is read-only.

        """
        return self._read_only

    @property
    def links(self: 'State') -> Deque['State']:
        """State links.

        Return:
        Deque[State]: State links.

        """
        return self._links

    @property
    def values(self: 'State') -> List[Value]:
        """Values.

        Do not modify the list in place. Use it only ready-only.

        Return:
        List[Value]: Values.

        """
        return self._values

    def add_value(self: 'State', value: Value) -> None:
        """Add value.

        Parameters:
        value (Value): Value to add.

        """
        if value is None:
            raise Exception("value is None")
        self._values.append(value)
        value.state = self
        value.index = len(self._values) - 1

    def remove_value(self: 'State', value: Value) -> None:
        """Remove value.

        Parameters:
        value (Value): Value to remove.

        """
        self._values.remove(value)
        value.state = None

        index = 0
        for value in self._values:
            value.index = index
            index = index + 1

    def link_read_values(self: 'State', reader: MessageReader,
                         link: StateLink) -> None:
        """Read values from message.

        Parameters:
        reader (MessageReader): Message reader.
        link (StateLink): Link.

        """
        count = reader.read_byte()
        real_count = len(self._values)
        for _i in range(count):
            index = reader.read_ushort()
            if index < 0 or index >= real_count:
                raise Exception("index out of range")
            value = self._values[index]
            value.read(reader)
            self.invalidate_value_except(index, link)
            self.remote_value_changed(value)
            value.remote_value_changed()
        link.changed = link.has_changed_values

    def link_read_all_values(self: 'State', reader: MessageReader,
                             link: StateLink) -> None:
        """Read all values from message.

        Parameters:
        reader (MessageReader): Message reader.
        link (StateLink): Link.

        """
        count = len(self._values)
        for i in range(count):
            value = self._values[i]
            value.read(reader)
            self.invalidate_value(i)
            self.remote_value_changed(value)
            value.remote_value_changed()
        if not link.has_changed_values:
            link.changed = False

    def link_read_and_verify_all_values(self: 'State',
                                        reader: MessageReader) -> bool:
        """Read all values from message including types.

        Verifies that the values in the state match in type and update
        their values.

        Return:
        bool: True if state matches and has been updated.

        """
        count = len(self._values)
        if count != reader.read_ushort():
            raise Exception("count out of range")
        for i in range(count):
            data_type = ValueTypes(reader.read_byte())
            value = self._values[i]
            if data_type != value.data_type:
                logger.debug("DNL.State: data type mismatch: %s",
                             "expected {0} found {1}".format(
                                data_type, value.data_type))
                raise Exception("data type mismatch")
            value.read(reader)
            self.invalidate_value(i)
            self.remote_value_changed(value)
            value.remote_value_changed()
        return True

    def link_write_values_all(self: 'State', writer: MessageWriter) -> None:
        """Write all values to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        for value in self._values:
            value.write(writer)

    def link_write_values_with_verify(self: 'State',
                                      writer: MessageWriter) -> None:
        """Write all values to message.

        Parameters:
        writer (MessageWriter): Message writer.

        """
        writer.write_ushort(len(self._values))
        for value in self._values:
            writer.write_byte(value.data_type.value)
            value.write(writer)

    def link_write_values_link(self: 'State', writer: MessageWriter,
                               link: StateLink) -> None:
        """Write values to message if changed in link.

        Parameters:
        writer (MessageWriter): Message writer.
        link (StateLink): State link.

        """
        count = len(self._values)
        changed_count = 0
        for i in range(count):
            if link.value_changed(i):
                changed_count = changed_count + 1
        changed_count = min(changed_count, 255)

        writer.write_byte(changed_count)

        for i in range(count):
            if not link.value_changed(i):
                continue
            writer.write_ushort(i)
            self._values[i].write(writer)
            link.set_value_changed(i, False)
            changed_count = changed_count - 1
            if changed_count == 0:
                break
        link.changed = link.has_changed_values

    def invalidate_value(self: 'State', index: int) -> None:
        """Invalid value in all state links.

        Parameters:
        index (int): Index of value to invalidate.

        """
        for link in self._links:
            link.set_value_changed(index, True)

    def invalidate_value_except(self: 'State', index: int,
                                link: StateLink) -> None:
        """Invalid value in all state links.

        Parameters:
        index (int): Index of link to invalidate.
        link (StateLink): Except link.

        """
        for each in self._links:
            if each != link:
                each.set_value_changed(index, True)

    def value_changed(self: 'State', value: Value) -> None:
        """For use by Value only.

        Parameters:
        value (Value): Value.

        """
        if value.update_value(False):
            self.invalidate_value(value.index)

    def remote_value_changed(self: 'State', value: Value) -> None:
        """Remote value changed.

        For use by subclass to react to remote value changes. After this
        call Value.remote_value_changed is called too so you can decide
        where to subclass.

        Parameters:
        value (Value): Value.

        """
        pass
