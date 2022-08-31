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

from enum import IntEnum, auto

"""
from .state import State
# circular import
"""


class StateLink:

    """State link."""

    class LinkState(IntEnum):

        """Link state."""

        DOWN = auto()
        """Link down."""

        LISTENING = auto()
        """Link listening."""

        UP = auto()
        """Link up."""

    def __init__(self: 'StateLink', connection: 'Connection',
                 state: 'State') -> None:
        """Create state link."""

        if connection is None:
            raise Exception("connection is None")
        if state is None:
            raise Exception("state is None")

        self._connection = connection
        self._value_changed = [False] * len(state.values)
        self._state = state
        self._identifier = -1
        self._link_state = StateLink.LinkState.DOWN
        self._changed = False

    @property
    def state(self: 'StateLink') -> 'State':
        """State or None if dropped.

        Return:
        State: State.

        """
        return self._state

    @property
    def identifier(self: 'StateLink') -> int:
        """Unique identifier.

        Return:
        int: Identifier.

        """
        return self._identifier

    @identifier.setter
    def identifier(self: 'StateLink', value: int) -> None:
        """Set unique identifier.

        Parameters:
        value (int): Identifier.

        """
        if value < -1:
            raise "value < -1"
        self._identifier = value

    @property
    def link_state(self: 'StateLink') -> 'StateLink.LinkState':
        """Link state.

        Return:
        StateLink.LinkState: Link state.

        """
        return self._link_state

    @link_state.setter
    def link_state(self: 'StateLink', value: 'StateLink.LinkState') -> None:
        """Set link state.

        Parameters:
        value (StateLink.LinkState): Link state.

        """
        self._link_state = value

    @property
    def connection(self: 'StateLink') -> 'Connection':
        """Connection.

        Return:
        Connection: Connection.

        """
        return self._connection

    @property
    def changed(self: 'StateLink') -> bool:
        """State link changed.

        Return:
        bool: State link changed.

        """
        return self._changed

    @changed.setter
    def changed(self: 'StateLink', value: bool) -> None:
        """Set if state link changed.

        Parameters:
        value (bool): Link changed.

        """
        if value != self._changed:
            self._changed = value
            if value:
                self._connection.add_modified_state_link(self)

    def value_changed(self: 'StateLink', index: int) -> bool:
        """Value changed.

        Parameters:
        index (int): Index of value.

        Return:
        bool: Value changed.

        """
        return self._value_changed[index]

    def set_value_changed(self: 'StateLink', index: int,
                          changed: bool) -> None:
        """Set if value changed.

        Parameters:
        index (int): Index of value.
        changed (bool): Value changed.

        """
        if changed != self._value_changed[index]:
            self._value_changed[index] = changed
            if changed:
                self.changed = True

    @property
    def has_changed_values(self: 'StateLink') -> bool:
        """One or more values are marked changed.

        Return:
        bool: Values changed.

        """
        return any(self._value_changed)

    def reset_changed(self: 'StateLink') -> None:
        """Reset changed of all values and state link."""
        self._changed = False
        self._value_changed = [False] * len(self._value_changed)

    def drop_state(self: 'StateLink') -> None:
        """Drop state. For use by State only."""
        self._state = None
