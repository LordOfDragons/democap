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
from .live_protocol import MessageCodes, LinkStateCodes, Features
from .live_utils import convertBoneName, convertBoneTransform
from .live_utils import convertPosition, convertOrientation
from .live_utils import convertBonePosition, convertBoneOrientation
from .live_captureactor import DemocapLiveCaptureActor
from .live_protocol import RecordPlaybackState
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

    class VertexPositionSet:
        def __init__(self, weight):
            self._weight = weight

        @property
        def weight(self):
            return self._weight

    def __init__(self):
        self.position = Vector()
        self.orientation = Quaternion()
        self.scale = 1.0
        self.bones = []
        self.vertexPositionSets = []


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

    class VertexPositionSet:
        def __init__(self, name):
            self._name = name

        @property
        def name(self):
            return self._name

    def __init__(self):
        self.revision = 0
        self.bones = []
        self.rootBones = []
        self.vertexPositionSets = []


class DemocapLiveStateRecordPlayback(dnl.state.State):
    def __init__(self, readOnly):
        dnl.state.State.__init__(self, readOnly)
        ifuint8 = dnl.value.ValueInt.Format.UINT8
        fffloat32 = dnl.value.ValueFloat.Format.FLOAT32
        self._valueStatus = dnl.value.ValueInt(ifuint8)
        self.add_value(self._valueStatus)
        self._valueFrameRate = dnl.value.ValueInt(ifuint8)
        self.add_value(self._valueFrameRate)
        self._valuePrepareTime = dnl.value.ValueFloat(fffloat32)
        self.add_value(self._valuePrepareTime)
        self._valuePlaySpeed = dnl.value.ValueFloat(fffloat32)
        self.add_value(self._valuePlaySpeed)
        self._valuePlayTime = dnl.value.ValueFloat(fffloat32)
        self.add_value(self._valuePlayTime)
        self._valuePlayPosition = dnl.value.ValueFloat(fffloat32)
        self.add_value(self._valuePlayPosition)

    @property
    def isRecording(self):
        return self._valueStatus.value == RecordPlaybackState.RECORDING


class DemocapLiveConnection(dnl.Connection):
    def __init__(self):
        dnl.Connection.__init__(self)
        self._infoStatus = "Disconnected"
        self._supportedFeatures = Features.ENABLE_VERTEX_POSITION_SETS
        self._ready = False
        self._enabledFeatures = 0
        self._useVertexPositionSets = False
        self._frameNumberWindowSize = 180
        self._lastFrameNumber = -1
        self._captureBoneLayout = None
        self._captureFrame = None
        self._captureActor = None
        self._statePlayback = None
        startAsyncioLoop()

    def dispose(self) -> None:
        stopAsyncioLoop()
        dnl.Connection.dispose(self)

    @property
    def useVertexPositionSets(self):
        return self._useVertexPositionSets

    @property
    def captureBoneLayout(self):
        return self._captureBoneLayout

    @property
    def captureFrame(self):
        return self._captureFrame

    @property
    def lastFrameNumber(self):
        return self._lastFrameNumber

    @property
    def infoStatus(self):
        return self._infoStatus

    @infoStatus.setter
    def infoStatus(self, value):
        self._infoStatus = value
        params = bpy.context.window_manager.democaptoolslive_params
        params.connection_status = value

    @property
    def statePlayback(self):
        return self._statePlayback

    def connect_to_host(self, context):
        params = context.window_manager.democaptoolslive_params
        logger.info("DemocapLiveConnection: Connect to host='%s' port=%d",
                    params.connect_host, params.connect_port)
        self.infoStatus = "Connecting..."
        self.connect_to("{0}:{1}".format(
            params.connect_host, params.connect_port))

    def onUpdatePreview(self):
        if self._captureActor is not None:
            self._captureActor.onUpdatePreview()

    def captureSingleFrame(self):
        if self._captureActor is not None:
            self._captureActor.captureSingleFrame()

    def connection_established(self):
        dnl.Connection.connection_established(self)
        self.infoStatus = "Connected: {0}".format(self.remote_address)
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
        if reason == dnl.Connection.ConnectionFailedReason.GENERIC:
            self.infoStatus = "Failed: Generic"
        elif reason == dnl.Connection.ConnectionFailedReason.TIMEOUT:
            self.infoStatus = "Failed: Timeout"
        elif reason == dnl.Connection.ConnectionFailedReason.REJECTED:
            self.infoStatus = "Failed: Rejected"
        elif reason == dnl.Connection.ConnectionFailedReason.NO_COMMON_PROTOCOL:
            self.infoStatus = "Failed: No Common Protocol"
        elif reason == dnl.Connection.ConnectionFailedReason.INVALID_MESSAGE:
            self.infoStatus = "Failed: Invalid Message"
        else:
            self.infoStatus = "Failed: ??"

    def connection_closed(self):
        dnl.Connection.connection_closed(self)
        self._resetState()
        self.infoStatus = "Disconnected"

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
                self._statePlayback = DemocapLiveStateRecordPlayback(read_only)
                return self._statePlayback

        return None

    def _resetState(self):
        self._ready = False
        self._statePlayback = None
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
        if ((self._enabledFeatures & self._supportedFeatures)
                != self._enabledFeatures):
            logger.info("DemocapLiveConnection: Feature mismatch")
            self.disconnect()
            return

        self._useVertexPositionSets = (
            self._enabledFeatures & Features.ENABLE_VERTEX_POSITION_SETS) != 0
        logger.info("DemocapLiveConnection: Use Vertex Position Sets = {}"
                    .format(self._useVertexPositionSets))

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
            layout.bones[i] = DemocapLiveCaptureBoneLayout.Bone(
                boneName, boneParent, boneMatrix)

            if boneParent == -1:
                layout.rootBones.append(i)

        """only send if vertex position sets are enabled"""
        if self._useVertexPositionSets:
            vpsCount = reader.read_ushort()
            layout.vertexPositionSets = [None] * vpsCount

            for i in range(vpsCount):
                vpsName = convertBoneName(reader.read_string8())
                layout.vertexPositionSets[i] = (
                    DemocapLiveCaptureBoneLayout.VertexPositionSet(vpsName))

        """finished reading message. store bone layout"""
        self._captureBoneLayout = layout
        logger.info("DemocapLiveConnection: Capture Bone Layout:"
                    + " revision %d, bones %d", layout.revision, boneCount)

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

            """
            localTransform = convertBoneTransform(bonePosition, boneOrientation)
            originTransform = self._captureBoneLayout.bones[i].matrix
            """

            """frame.bones[i] = localTransform @ originTransform"""
            frame.bones[i] = DemocapLiveCaptureFrame.Bone(
                convertBonePosition(bonePosition),
                convertBoneOrientation(boneOrientation),
                None)  # localTransform)

        """only send if vertex position sets are enabled"""
        if self._useVertexPositionSets:
            vpsCount = len(self._captureBoneLayout.vertexPositionSets)
            frame.vertexPositionSets = [None] * vpsCount
            for i in range(vpsCount):
                vpsWeight = reader.read_float()
                frame.vertexPositionSets[i] = (
                    DemocapLiveCaptureFrame.VertexPositionSet(vpsWeight))

        self._captureFrame = frame
