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

import logging
import mathutils
import bpy

from .configuration import Configuration
from .asyncio_helper import startAsyncioLoop, stopAsyncioLoop
from . import DENetworkLibrary as dnl


logger = logging.getLogger(__name__)


class DemocapLiveConnection(dnl.Connection):
	def __init__(self):
		dnl.Connection.__init__(self)
		self._params = None
		startAsyncioLoop()
	
	def dispose(self) -> None:
		stopAsyncioLoop()
		dnl.Connection.dispose(self)
	
	def connect_to_host(self, context):
		self._params = context.window_manager.democaptools_liveparams
		logger.info("DemocapLiveConnection.connect: host='%s' port=%d",
			self._params.connect_host, self._params.connect_port)
		self._params.connection_status = "Connecting..."
		self.connect_to("{0}:{1}".format(self._params.connect_host, self._params.connect_port))
	
	def connection_established(self):
		dnl.Connection.connection_established(self)
		if self._params is not None:
			self._params.connection_status = "Connected: {0}".format(self.remote_address)
	
	def connection_failed(self, reason):
		dnl.Connection.connection_failed(self, reason)
		if self._params is not None:
			if reason == dnl.Connection.ConnectionFailedReason.GENERIC:
				self._params.connection_status = "Failed: Generic"
			elif reason == dnl.Connection.ConnectionFailedReason.TIMEOUT:
				self._params.connection_status = "Failed: Timeout"
			elif reason == dnl.Connection.ConnectionFailedReason.REJECTED:
				self._params.connection_status = "Failed: Rejected"
			elif reason == dnl.Connection.ConnectionFailedReason.NO_COMMON_PROTOCOL:
				self._params.connection_status = "Failed: No Common Protocol"
			elif reason == dnl.Connection.ConnectionFailedReason.INVALID_MESSAGE:
				self._params.connection_status = "Failed: Invalid Message"
			else:
				self._params.connection_status = "Failed: ??"
	
	def connection_closed(self):
		dnl.Connection.connection_closed(self)
		if self._params is not None:
			self._params.connection_status = "Disconnected"
