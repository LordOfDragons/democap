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
import bpy

from mathutils import Vector, Quaternion
from .configuration import Configuration
from .asyncio_helper import startAsyncioLoop, stopAsyncioLoop
from .live_protocol import MessageCodes, LinkStateCodes
from .live_utils import convertBoneName, convertBoneTransform
from .live_utils import convertPosition, convertOrientation
from .live_utils import convertBonePosition, convertBoneOrientation
from .live_captureactor import DemocapLiveCaptureActor
from . import DENetworkLibrary as dnl


logger = logging.getLogger(__name__)


class DemocapLiveCaptureFrame:
	class Bone:
		def __init__(self, position, orientation, matrix):
			self._position = position
			self._orientation = orientation
			self._matrix = matrix
		
		@property
		def position(self):
			return self._position
		
		@property
		def orientation(self):
			return self._orientation
		
		@property
		def matrix(self):
			return self._matrix
	
	
	def __init__(self):
		self.position = Vector()
		self.orientation = Quaternion()
		self.scale = 1.0
		self.bones = []


class DemocapLiveCaptureBoneLayout:
	class Bone:
		def __init__(self, name, parent, matrix):
			self._name = name
			self._parent = parent
			self._matrix = matrix
		
		@property
		def name(self):
			return self._name
		
		@property
		def parent(self):
			return self._parent
		
		@property
		def matrix(self):
			return self._matrix
	
	
	def __init__(self):
		self.revision = 0
		self.bones = []
		self.rootBones = []


class DemocapLiveConnection(dnl.Connection):
	def __init__(self):
		dnl.Connection.__init__(self)
		self._params = None
		self._supportedFeatures = 0
		self._ready = False
		self._enabledFeatures = 0
		self._frameNumberWindowSize = 180
		self._lastFrameNumber = -1
		self._captureBoneLayout = None
		self._captureFrame = None
		self._captureActor = None
		startAsyncioLoop()
	
	def dispose(self) -> None:
		stopAsyncioLoop()
		dnl.Connection.dispose(self)
	
	@property
	def captureBoneLayout(self):
		return self._captureBoneLayout
	
	@property
	def captureFrame(self):
		return self._captureFrame
	
	@property
	def lastFrameNumber(self):
		return self._lastFrameNumber
	
	def connect_to_host(self, context):
		self._params = context.window_manager.democaptoolslive_params
		logger.info("DemocapLiveConnection: Connect to host='%s' port=%d",
			self._params.connect_host, self._params.connect_port)
		self._params.connection_status = "Connecting..."
		self.connect_to("{0}:{1}".format(self._params.connect_host, self._params.connect_port))
	
	def connection_established(self):
		dnl.Connection.connection_established(self)
		if self._params is not None:
			self._params.connection_status = "Connected: {0}".format(self.remote_address)
		message = dnl.message.Message()
		with dnl.message.MessageWriter(message) as w:
			w.write_byte(MessageCodes.CONNECT_REQUEST.value)
			w.write(b"DEMoCap-Client-0", 0, 16)
			w.write_uint(self._supportedFeatures)
			w.write_string8("BlenderDEMoCapLiveAddon")
		self.send_reliable_message(message)
	
	def connection_failed(self, reason):
		dnl.Connection.connection_failed(self, reason)
		self._resetState()
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
		self._resetState()
		if self._params is not None:
			self._params.connection_status = "Disconnected"
	
	def message_received(self, message):
		if not self._ready:
			with dnl.message.MessageReader(message) as r:
				code = MessageCodes(r.read_byte())
				if code == MessageCodes.CONNECT_ACCEPTED.value:
					self._processConnectAccepted(r)
			return
		
		with dnl.message.MessageReader(message) as r:
			code = MessageCodes(r.read_byte())
			if code == MessageCodes.ACTOR_CAPTURE_BONE_LAYOUT.value:
				self._processCaptureBoneLayout(r)
			elif code == MessageCodes.ACTOR_CAPTURE_FRAME.value:
				self._processCaptureFrame(r)
	
	def create_state(self, message, read_only):
		if not self._ready:
			return None
		
		with dnl.message.MessageReader(message) as r:
			code = MessageCodes(r.read_byte())
			if code == LinkStateCodes.RECORD_PLAYBACK.value:
				return None
		
		return None
	
	def _resetState(self):
		self._ready = False
		if self._captureActor is not None:
			self._captureActor.dispose()
			self._captureActor = None
		self._captureBoneLayout = None
		self._captureFrame = None
		self._lastFrameNumber = -1
		self._enabledFeatures = 0
		
	def _ignoreFrameNumber(self, frameNumber):
		if self._lastFrameNumber == -1:
			return False
		difference = frameNumber - self._lastFrameNumber
		if difference < -32767:
			difference += 65536  # wrap around uint16
		return abs(difference) > self._frameNumberWindowSize or difference < 0
	
	def _processConnectAccepted(self, reader):
		logger.info("DemocapLiveConnection: Received ConnectAccepted")
		signature = reader.read(16)
		if signature != b"DEMoCap-Server-0":
			logger.info("DemocapLiveConnection: Signature mismatch")
			self.disconnect()
			return
		
		self._enabledFeatures = reader.read_uint()
		if (self._enabledFeatures & self._supportedFeatures) != self._enabledFeatures:
			logger.info("DemocapLiveConnection: Feature mismatch")
			self.disconnect()
			return
		
		logger.info("DemocapLiveConnection: Ready")
		self._ready = True
		self._captureActor = DemocapLiveCaptureActor(self)
	
	def _processCaptureBoneLayout(self, reader):
		layout = DemocapLiveCaptureBoneLayout()
		layout.revision = reader.read_byte()
		boneCount = reader.read_ushort()
		layout.bones = [None] * boneCount
		
		for i in range(boneCount):
			boneName = convertBoneName(reader.read_string8())
			boneParent = reader.read_short()
			
			bonePosition = reader.read_vector3()
			boneOrientation = reader.read_quaternion()
			boneMatrix = convertBoneTransform(bonePosition, boneOrientation)
			layout.bones[i] = DemocapLiveCaptureBoneLayout.Bone(boneName, boneParent, boneMatrix)
			
			if boneParent == -1:
				layout.rootBones.append(i)
		
		"""finished reading message successfully so the bone layout can be stored"""
		self._captureBoneLayout = layout
		logger.info("DemocapLiveConnection: Capture Bone Layout: revision %d, bones %d", layout.revision, boneCount)
	
	def _processCaptureFrame(self, reader):
		frameNumber = reader.read_ushort()
		
		"""check if this message is not old"""
		if self._ignoreFrameNumber(frameNumber):
			return
		self._lastFrameNumber = frameNumber
		
		"""check if the revision matches"""
		revision = reader.read_byte()
		if revision != self._captureBoneLayout.revision:
			return
		
		"""store capture frame"""
		frame = DemocapLiveCaptureFrame()
		boneCount = len(self._captureBoneLayout.bones)
		unscaled = Vector((1, 1, 1))
		
		position = reader.read_vector3()
		frame.position = convertPosition(position)
		
		orientation = reader.read_quaternion()
		frame.orientation = convertOrientation(orientation)
		
		frame.scale = reader.read_float()
		
		frame.bones = [None] * boneCount
		
		for i in range(boneCount):
			bonePosition = reader.read_vector3()
			boneOrientation = reader.read_quaternion()
			
			#localTransform = convertBoneTransform(bonePosition, boneOrientation)
			#originTransform = self._captureBoneLayout.bones[i].matrix
			
			#frame.bones[i] = localTransform @ originTransform
			frame.bones[i] = DemocapLiveCaptureFrame.Bone(
				convertBonePosition(bonePosition),
				convertBoneOrientation(boneOrientation),
				None)  # localTransform)
		
		"""finished reading message successfully so the capture frame can be stored"""
		self._captureFrame = frame
