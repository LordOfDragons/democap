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
from fnmatch import fnmatch

from .configuration import Configuration
from .utils import registerClass, flatten
from .live_connection import DemocapLiveConnection, registerAsyncioOperator
from . import DENetworkLibrary as dnl

logger = logging.getLogger(__name__)


live_connection = None


class WM_OT_DemocapLiveConnect(bpy.types.Operator):
	"""Connect to DEMoCap."""
	bl_idname = "democaplive.connect"
	bl_label = "Connect"
	bl_description = "Connect to DEMoCap"
	bl_options = set()
	
	@classmethod
	def poll(cls, context):
		global live_connection
		return live_connection is None
	
	def execute(self, context):
		global live_connection
		if live_connection is not None:
			return {'CANCELLED'}
		
		live_connection = DemocapLiveConnection()
		live_connection.connect_to_host(context)
		return {'FINISHED'}

class WM_OT_DemocapLiveDisconnect(bpy.types.Operator):
	"""Connect to DEMoCap."""
	bl_idname = "democaplive.disconnect"
	bl_label = "Disconnect"
	bl_description = "Disconnect from DEMoCap"
	bl_options = set()
	
	@classmethod
	def poll(cls, context):
		global live_connection
		return live_connection is not None
	
	def execute(self, context):
		global live_connection
		if live_connection is None:
			return {'CANCELLED'}
		
		params = context.window_manager.democaptools_liveparams
		
		live_connection.dispose()
		live_connection = None
		params.connection_status = "Disconnected"
		return {'FINISHED'}

class VIEW3D_PT_DemocapToolsLiveConnect(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "DEMoCap"
	bl_label = "Lice Connect"
	bl_description = "DEMoCap Tools Live Connect"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		global live_connection
		
		config = Configuration.get()
		params = context.window_manager.democaptools_liveparams
		layout = self.layout
		
		if live_connection is not None and live_connection.connection_state == dnl.Connection.ConnectionState.DISCONNECTED:
			live_connection.dispose()
			live_connection = None
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
		update=updateConnectionStatus)


def panelLiveRegister():
	registerAsyncioOperator()
	registerClass(DemocapLiveParameters)
	registerClass(WM_OT_DemocapLiveConnect)
	registerClass(WM_OT_DemocapLiveDisconnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveConnect)
	
	bpy.types.WindowManager.democaptools_liveparams = bpy.props.PointerProperty(type=DemocapLiveParameters)
	logger.info("registered")
