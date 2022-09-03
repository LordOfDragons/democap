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

from .live_frameupdater import addFrameUpdater, removeFrameUpdater


logger = logging.getLogger(__name__)


class DemocapLiveCaptureActor:
    class BoneMapping:
        def __init__(self, indexPoseBone, poseBone,
                     indexLayoutBone, layoutBone):
            self._indexPoseBone = indexPoseBone
            self._poseBone = poseBone
            self._indexLayoutBone = indexLayoutBone
            self._layoutBone = layoutBone

        @property
        def indexPoseBone(self):
            return self._indexPoseBone

        @property
        def poseBone(self):
            return self._poseBone

        @property
        def indexLayoutBone(self):
            return self._indexLayoutBone

        @property
        def layoutBone(self):
            return self._layoutBone

        def updatePose(self, captureFrame, insertKeyframes):
            frameBone = captureFrame.bones[self._indexLayoutBone]
            self._poseBone.location = frameBone.position
            self._poseBone.rotation_quaternion = frameBone.orientation
            if insertKeyframes:
                """self._poseBone.matrix = frameBone.matrix"""
                self._poseBone.keyframe_insert(data_path="location")
                self._poseBone.keyframe_insert(data_path="rotation_quaternion")

    def __init__(self, connection):
        self._connection = connection
        self._object = None
        self._boneLayout = None
        self._boneMapping = None
        self._captureFrame = None
        addFrameUpdater(self)

    def dispose(self):
        removeFrameUpdater(self)
        self._connection = None

    @property
    def object(self):
        return self._object

    @object.setter
    def object(self, value):
        if value == self._object:
            return
        self._object = value
        self._boneLayout = None
        self._boneMapping = None

    def onUpdatePreview(self):
        self._captureActor(False)

    def onFrameUpdate(self, scene):
        screen = bpy.context.screen
        if screen.is_scrubbing:
            return
        params = bpy.context.window_manager.democaptoolslive_params
        if screen.is_animation_playing and (params.preview or params.record):
            if self._captureFrame == self._connection.captureFrame:
                return
            self._captureActor(params.record)

    def captureSingleFrame(self):
        self._captureActor(True)

    def _captureActor(self, insertKeyframes):
        self.object = bpy.context.scene.democaptoolslive_actor
        if self._object is None:
            return
        self._updateBoneMapping()

        self._captureFrame = self._connection.captureFrame
        if self._captureFrame is None:
            return

        self._object.location = self._captureFrame.position
        self._object.rotation_quaternion = self._captureFrame.orientation
        if insertKeyframes:
            self._object.keyframe_insert(data_path="location")
            self._object.keyframe_insert(data_path="rotation_quaternion")

        for b in self._boneMapping:
            b.updatePose(self._captureFrame, insertKeyframes)
        """frame = self._connection.captureFrame()
        logger.info("onFrameUpdate %d", self._connection.lastFrameNumber)"""

    def _updateBoneMapping(self):
        boneLayout = self._connection.captureBoneLayout
        if boneLayout != self._boneLayout:
            self._boneLayout = boneLayout
            if boneLayout is None:
                return
            self._initBoneMapping()

    def _initBoneMapping(self):
        self._boneMapping = []
        pose = self._object.pose
        if pose is None:
            return

        names = pose.bones.keys()
        for i in range(len(self._boneLayout.bones)):
            layoutBone = self._boneLayout.bones[i]
            indexPoseBone = names.index(layoutBone.name)
            if indexPoseBone != -1:
                self._boneMapping.append(DemocapLiveCaptureActor.BoneMapping(
                    indexPoseBone, pose.bones[indexPoseBone], i, layoutBone))
