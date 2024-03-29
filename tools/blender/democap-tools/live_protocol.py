# -*- coding: utf-8 -*-
#
# DEMoCap Blender Tools
#
# Copyright (C) 2022, DragonDreams (roland@dragondreams.ch)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# NOTE: For the GPL copy see http://www.gnu.org/licenses/gpl.html
#

from enum import IntEnum


class Features(IntEnum):
    ENABLE_VERTEX_POSITION_SETS = 0x1


class MessageCodes(IntEnum):
    CONNECT_REQUEST = 1
    CONNECT_ACCEPTED = 2
    ACTOR_CAPTURE_BONE_LAYOUT = 3
    ACTOR_CAPTURE_FRAME = 4


class LinkStateCodes(IntEnum):
    RECORD_PLAYBACK = 1


class RecordPlaybackState(IntEnum):
    IDLE = 0
    PREPARE_RECORDING = 1
    RECORDING = 2
    PLAYBACK = 3
    PLAYBACK_PAUSED = 4
