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
import os
import atexit
from fnmatch import fnmatch
from bpy.app.handlers import persistent

from .configuration import Configuration
from .utils import registerClass, flatten
from .asyncio_helper import registerAsyncioOperator
from .live_connection import DemocapLiveConnection
from .live_frameupdater import registerFrameUpdaterHandlers
from . import DENetworkLibrary as dnl

logger = logging.getLogger(__name__)


liveConnection = None


class WM_OT_DemocapLiveConnect(bpy.types.Operator):
	"""Connect to DEMoCap."""
	bl_idname = "democaplive.connect"
	bl_label = "Connect"
	bl_description = "Connect to DEMoCap"
	bl_options = set()
	
	@classmethod
	def poll(cls, context):
		return liveConnection is None
	
	def execute(self, context):
		global liveConnection
		if liveConnection is not None:
			return {'CANCELLED'}
		
		liveConnection = DemocapLiveConnection()
		liveConnection.connect_to_host(context)
		return {'FINISHED'}

class WM_OT_DemocapLiveDisconnect(bpy.types.Operator):
	"""Connect to DEMoCap."""
	bl_idname = "democaplive.disconnect"
	bl_label = "Disconnect"
	bl_description = "Disconnect from DEMoCap"
	bl_options = set()
	
	@classmethod
	def poll(cls, context):
		return liveConnection is not None
	
	def execute(self, context):
		global liveConnection
		if liveConnection is None:
			return {'CANCELLED'}
		
		params = context.window_manager.democaptoolslive_params
		
		liveConnection.dispose()
		liveConnection = None
		params.connection_status = "Disconnected"
		return {'FINISHED'}

class VIEW3D_PT_DemocapToolsLiveConnect(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "DEMoCap"
	bl_label = "Live Connect"
	bl_description = "DEMoCap Tools Live Connect"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		global liveConnection
		
		params = context.window_manager.democaptoolslive_params
		layout = self.layout
		
		if liveConnection is not None and liveConnection.connection_state == dnl.Connection.ConnectionState.DISCONNECTED:
			liveConnection.dispose()
			liveConnection = None
			params.connection_status = "Disconnected"
		
		block = layout.column(align=True)
		block.row(align=True).prop(params, "connect_host", expand=True)
		block.row(align=True).prop(params, "connect_port", expand=True)
		row = block.row(align=True)
		row.column(align=True).operator(operator="democaplive.connect")
		row.column(align=True).operator(operator="democaplive.disconnect")
		row = block.row(align=False)
		row.emboss = 'NONE'
		row.enabled = False
		row.prop(params, "connection_status", expand=True)

class VIEW3D_PT_DemocapToolsLiveActor(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "DEMoCap"
	bl_label = "Live Actor"
	bl_description = "DEMoCap Tools Live Connect"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		layout = self.layout
		
		block = layout.column(align=True)
		block.row(align=True).prop(context.scene, "democaptoolslive_actor", expand=True)

class WM_OT_DemocapLiveCaptureFrame(bpy.types.Operator):
	"""Connect to DEMoCap."""
	bl_idname = "democaplive.captureframe"
	bl_label = "Capture Frame"
	bl_description = "Capture single frame"
	bl_options = set()
	
	@classmethod
	def poll(cls, context):
		params = context.window_manager.democaptoolslive_params
		screen = context.screen
		return liveConnection is not None and params.preview\
			and not params.record and not screen.is_scrubbing
	
	def execute(self, context):
		params = context.window_manager.democaptoolslive_params
		screen = context.screen
		if liveConnection is None or not params.preview\
				or params.record or screen.is_scrubbing:
			return {'CANCELLED'}
		
		liveConnection.captureSingleFrame()
		return {'FINISHED'}

class VIEW3D_PT_DemocapToolsLiveRecord(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "DEMoCap"
	bl_label = "Live Capture"
	bl_description = "DEMoCap Tools Live Capturing"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		params = context.window_manager.democaptoolslive_params
		layout = self.layout
		
		block = layout.column(align=True)
		row = block.row(align=True)
		row.column(align=True).prop(params, "preview", expand=True, toggle=True)
		row.column(align=True).prop(context.scene, "democaptoolslive_previewrate", expand=True)
		row = block.row(align=True)
		row.operator(operator="democaplive.captureframe")
		
		block = layout.column(align=True)
		row = block.row(align=True)
		row.column(align=True).prop(params, "record", expand=True, toggle=True)
		row.column(align=True).prop(params, "sync_recording", expand=True, toggle=True)

def updateConnectionStatus(self, context):
	bpy.context.view_layer.update()

def onTimerPreview():
	params = bpy.context.window_manager.democaptoolslive_params
	if not params.preview:
		return None
	nextTimeout = 1 / bpy.context.scene.democaptoolslive_previewrate
	screen = bpy.context.screen
	if screen.is_scrubbing:
		return nextTimeout
	"""
	if not screen.is_animation_playing or screen.is_scrubbing:
		params.preview = False
		return None
	"""
	if liveConnection is not None:
		liveConnection.onUpdatePreview()
	return nextTimeout

def onTimerRecord():
	params = bpy.context.window_manager.democaptoolslive_params
	screen = bpy.context.screen
	if not params.record or screen.is_scrubbing or not screen.is_animation_playing:
		params.record = False
		bpy.context.view_layer.update()
		return None
	return 0.01

def updatePreview(self, context):
	if bpy.context.window_manager.democaptoolslive_params.preview:
		bpy.app.timers.register(onTimerPreview, first_interval=0)

def updateRecord(self, context):
	if bpy.context.window_manager.democaptoolslive_params.record:
		bpy.ops.screen.animation_play(sync=True)
		bpy.app.timers.register(onTimerRecord, first_interval=0.01)
	else:
		bpy.ops.screen.animation_cancel(restore_frame=True)

def onTimerSyncRecord():
	params = bpy.context.window_manager.democaptoolslive_params
	if not params.sync_recording:
		return None
	if liveConnection is not None:
		state = liveConnection.statePlayback
		if state is not None:
			recording = state.isRecording
			if recording != params.record:
				params.record = recording
				bpy.context.view_layer.update()
	return 0.1

def updateSyncRecord(self, context):
	if bpy.context.window_manager.democaptoolslive_params.sync_recording:
		bpy.app.timers.register(onTimerSyncRecord, first_interval=0)

class DemocapLiveParameters(bpy.types.PropertyGroup):
	connect_host: bpy.props.StringProperty(name="Host",
		description="Hostname or IP to connect to",
		default="localhost")
	
	connect_port: bpy.props.IntProperty(name="Port",
		description="Port to connect to",
		default=3413)
	
	connection_status: bpy.props.StringProperty(name="",
		description="Connection state",
		default="Disconnected",
		update=updateConnectionStatus,
		options={'HIDDEN', 'SKIP_SAVE'})
	
	preview: bpy.props.BoolProperty(name="Preview",
		description="Live preview motion capture",
		default=False,
		update=updatePreview,
		options={'SKIP_SAVE'})
	
	record: bpy.props.BoolProperty(name="Record",
		description="Record motion capture",
		default=False,
		update=updateRecord,
		options={'SKIP_SAVE'})
	sync_recording: bpy.props.BoolProperty(name="Sync",
		description="Sync recording to DEMoCap recording state",
		default=False,
		update=updateSyncRecord,
		options={'SKIP_SAVE'})

def filterOnlyArmatures(self, object):
	return object.type == 'ARMATURE'

def actorChanged(self, context):
	#logger.info("Actor changed to {}".format(context.scene.democaptoolslive_actor))
	pass

bpy.types.Scene.democaptoolslive_actor = bpy.props.PointerProperty(type=bpy.types.Object,
	name="Actor",
	description="Armature to link MoCap actor to",
	poll=filterOnlyArmatures,
	update=actorChanged)

bpy.types.Scene.democaptoolslive_previewrate = bpy.props.IntProperty(name="Rate",
	description="Frame rate of live preview",
	default=25,
	soft_min=10,
	min=1,
	soft_max=50,
	max=100)

@persistent
def onPostLoad(always_none):
	if liveConnection is not None:
		bpy.context.window_manager.democaptoolslive_params.connection_status = liveConnection.infoStatus

def panelLiveRegister():
	registerAsyncioOperator()
	registerFrameUpdaterHandlers()
	registerClass(DemocapLiveParameters)
	registerClass(WM_OT_DemocapLiveConnect)
	registerClass(WM_OT_DemocapLiveDisconnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveConnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveActor)
	registerClass(WM_OT_DemocapLiveCaptureFrame)
	registerClass(VIEW3D_PT_DemocapToolsLiveRecord)
	
	bpy.types.WindowManager.democaptoolslive_params = bpy.props.PointerProperty(type=DemocapLiveParameters)
	bpy.app.handlers.load_post.append(onPostLoad)
	logger.info("registered")

def onExitBlender():
	if liveConnection is not None:
		liveConnection.dispose()

atexit.register(onExitBlender)
