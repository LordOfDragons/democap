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
		global liveConnection
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
		global liveConnection
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

def updateConnectionStatus(self, context):
	bpy.context.view_layer.update()

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
		options=set(('HIDDEN', 'SKIP_SAVE')))

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

def panelLiveRegister():
	registerAsyncioOperator()
	registerFrameUpdaterHandlers()
	registerClass(DemocapLiveParameters)
	registerClass(WM_OT_DemocapLiveConnect)
	registerClass(WM_OT_DemocapLiveDisconnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveConnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveActor)
	
	bpy.types.WindowManager.democaptoolslive_params = bpy.props.PointerProperty(type=DemocapLiveParameters)
	logger.info("registered")

def onExitBlender():
	if liveConnection is not None:
		liveConnection.dispose()

atexit.register(onExitBlender)
