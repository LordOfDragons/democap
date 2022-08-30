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
from . import denetwork as dnl


class DemocapLiveConnection(dnl.Connection):
	def __init__(self):
		dnl.Connection.__init__(self)
	
	def connect_to_host(self, context):
		params = context.window_manager.democaptools_liveparams
		print("DemocapLiveConnection.connect: host='{}' port={}".format(
			params.connect_host, params.connect_port))
		self.connect_to("{0}:{1}".format(params.connect_host, params.connect_port))

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
		
		liveConnection.dispose()
		liveConnection = None
		return {'FINISHED'}

class VIEW3D_PT_DemocapToolsLiveConnect(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "DEMoCap Live"
	bl_label = "Connect"
	bl_description = "DEMoCap Tools Live Connect"
	
	def draw(self, context):
		global liveConnection
		
		config = Configuration.get()
		params = context.window_manager.democaptools_liveparams
		layout = self.layout
		
		block = layout.column(align=True)
		block.row(align=True).prop(params, "connect_host", expand=True)
		block.row(align=True).prop(params, "connect_port", expand=True)
		row = block.row(align=True)
		row.column(align=True).operator(operator="democaplive.connect")
		row.column(align=True).operator(operator="democaplive.disconnect")

class LiveParameters(bpy.types.PropertyGroup):
	connect_host: bpy.props.StringProperty(name="Host", description="Hostname or IP to connect to", default="localhost")
	connect_port: bpy.props.IntProperty(name="Port", description="Port to connect to", default=3413)


def panelLiveRegister():
	registerClass(LiveParameters)
	registerClass(WM_OT_DemocapLiveConnect)
	registerClass(WM_OT_DemocapLiveDisconnect)
	registerClass(VIEW3D_PT_DemocapToolsLiveConnect)
	
	bpy.types.WindowManager.democaptools_liveparams = bpy.props.PointerProperty(type=LiveParameters)
