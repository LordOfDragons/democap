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

import bpy
import os
from fnmatch import fnmatch

from .configuration import Configuration
from .utils import registerClass
from .demca import Demca


class DemcaBrowserItem(bpy.types.PropertyGroup):
	"""Group of properties representing an item in the list."""
	
	name: bpy.props.StringProperty(default="")
	path: bpy.props.StringProperty(default="")
	isDirectory: bpy.props.BoolProperty(default=False)
	icon: bpy.props.StringProperty(default='OBJECT_DATAMODE')

class LIST_UL_DemcaBrowser(bpy.types.UIList):
	"""File List."""
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.label(text=item.name, icon=item.icon)
			if item.isDirectory:
				layout.operator("democaptools_demcabrowser.changedirectory", text="",
					icon='TRIA_LEFT' if item.name == '..' else 'TRIA_RIGHT').path = item.path
		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon=item.icon)

class DemcaBrowserSelectionInfo(bpy.types.PropertyGroup):
	"""Group of properties representing information about selected item in the list."""
	
	filename: bpy.props.StringProperty(name="Filename", default="")
	timestamp: bpy.props.StringProperty(name="Timestamp", default="")
	character: bpy.props.StringProperty("Character", default="")
	configuration: bpy.props.StringProperty("Configuration", default="")
	playtime: bpy.props.FloatProperty("Playtime", default=0, precision=1, soft_min=0, min=0, soft_max=10)
	frameRate: bpy.props.IntProperty("Framerate", default=0, soft_min=15, min=0, soft_max=90)
	pathAnimation: bpy.props.StringProperty(name="Path Animation", default="")
	pathDevicesRig: bpy.props.StringProperty(name="Path Devices Rig", default="")
	pathDevicesAnimation: bpy.props.StringProperty(name="Path Devices Animation", default="")

def DemcaBrowser_SelectionChanged(self, context):
	dtprops = context.window_manager.democaptools_properties
	dtlist = context.window_manager.democaptools_filelistdemca
	index = context.window_manager.democaptools_filelistdemca_index
	
	if index >= 0 and index < len(dtlist):
		entry = dtlist[index]
		if not entry.isDirectory:
			demca = Demca(entry.path)
			if demca.success:
				dtprops.browserSelectionInfo.filename = entry.name
				dtprops.browserSelectionInfo.timestamp = demca.formattedTimestamp
				dtprops.browserSelectionInfo.character = demca.characterProfile
				dtprops.browserSelectionInfo.configuration = demca.characterConfiguration
				dtprops.browserSelectionInfo.playtime = demca.playtime
				dtprops.browserSelectionInfo.frameRate = demca.frameRate
				dtprops.browserSelectionInfo.pathAnimation = demca.pathAnimation
				dtprops.browserSelectionInfo.pathDevicesRig = demca.pathDevicesRig
				dtprops.browserSelectionInfo.pathDevicesAnimation = demca.pathDevicesAnimation
				return
	
	dtprops.browserSelectionInfo.filename = ""
	dtprops.browserSelectionInfo.timestamp = ""
	dtprops.browserSelectionInfo.character = ""
	dtprops.browserSelectionInfo.configuration = ""
	dtprops.browserSelectionInfo.playtime = 0
	dtprops.browserSelectionInfo.frameRate = 0
	dtprops.browserSelectionInfo.pathAnimation = ""
	dtprops.browserSelectionInfo.pathDevicesRig = ""
	dtprops.browserSelectionInfo.pathDevicesAnimation = ""

def DemocapToolsPanelProperties_CurrentDirectory_Update(self, context):
	Configuration.get().setDemcaBrowserCurrentDirectory(self.currentDirectory)

class DemocapToolsPanelProperties(bpy.types.PropertyGroup):
	currentDirectory : bpy.props.StringProperty(
		name="Current directory",
		description="Current directory",
		default=Configuration.get().getDemcaBrowserCurrentDirectory(),
		update=DemocapToolsPanelProperties_CurrentDirectory_Update
		)
	
	browserSelectionInfo : bpy.props.PointerProperty(type=DemcaBrowserSelectionInfo)

class LIST_OT_DemcaBrowserChdir(bpy.types.Operator):
	"""Descent file listing."""
	bl_idname = "democaptools_demcabrowser.changedirectory"
	bl_label = "Descent file listing"
	
	path: bpy.props.StringProperty(default="")
	
	def execute(self, context):
		dtlist = context.window_manager.democaptools_filelistdemca
		if self.path:
			context.window_manager.democaptools_properties.currentDirectory = self.path
			bpy.ops.democaptools_demcabrowser.scanfiles('EXEC_DEFAULT')
		return {'FINISHED'}

class LIST_OT_DemcaBrowserScanFiles(bpy.types.Operator):
	"""Update file listing."""
	bl_idname = "democaptools_demcabrowser.scanfiles"
	bl_label = "Update file listing"
	
	def execute(self, context):
		dtlist = context.window_manager.democaptools_filelistdemca
		dtprops = context.window_manager.democaptools_properties
		
		context.window_manager.democaptools_filelistdemca_index = -1
		dtlist.clear()
		
		parentdir = os.path.split(dtprops.currentDirectory)[0]
		if parentdir:
			entry = dtlist.add()
			entry.name = ".."
			entry.path = parentdir
			entry.isDirectory = True
			entry.icon = 'FILE_FOLDER'
		
		for root, dirs, files in os.walk(dtprops.currentDirectory):
			for name in dirs:
				entry = dtlist.add()
				entry.name = name
				entry.path = os.path.join(root, name)
				entry.isDirectory = True
				entry.icon = 'FILE_FOLDER'
			del dirs[:]
			
			for name in files:
				if fnmatch(name, "*.demca"):
					entry = dtlist.add()
					entry.name = name
					entry.path = os.path.join(root, name)
					entry.isDirectory = False
					entry.icon = 'FILE'
		
		for i in range(len(dtlist)):
			if not dtlist[i].isDirectory:
				context.window_manager.democaptools_filelistdemca_index = i
				break
		
		return {'FINISHED'}

class LIST_OT_DemcaBrowserImportAnimation(bpy.types.Operator):
	"""Import Animation."""
	bl_idname = "democaptools_demcabrowser.importanimation"
	bl_label = "Import Animation"
	
	@classmethod
	def poll(cls, context):
		if context.active_object and context.active_object.type == 'ARMATURE':
			dtlist = context.window_manager.democaptools_filelistdemca
			index = context.window_manager.democaptools_filelistdemca_index
			dtprops = context.window_manager.democaptools_properties
			if index >= 0 and index < len(dtlist):
				if not dtlist[index].isDirectory:
					return dtprops.browserSelectionInfo.pathAnimation
		return False
	
	def execute(self, context):
		if context.active_object and context.active_object.type == 'ARMATURE':
			dtlist = context.window_manager.democaptools_filelistdemca
			index = context.window_manager.democaptools_filelistdemca_index
			dtprops = context.window_manager.democaptools_properties
			if index >= 0 and index < len(dtlist):
				if not dtlist[index].isDirectory:
					bpy.ops.dragengine.import_animation('EXEC_DEFAULT', filepath=Demca.getAbsPath(
						dtlist[index].path, dtprops.browserSelectionInfo.pathAnimation))
		return {'FINISHED'}

class LIST_OT_DemcaBrowserImportDevicesRig(bpy.types.Operator):
	"""Import Devices Rig."""
	bl_idname = "democaptools_demcabrowser.importdevicesrig"
	bl_label = "Import Devices Rig"
	
	@classmethod
	def poll(cls, context):
		dtlist = context.window_manager.democaptools_filelistdemca
		index = context.window_manager.democaptools_filelistdemca_index
		dtprops = context.window_manager.democaptools_properties
		if index >= 0 and index < len(dtlist):
			if not dtlist[index].isDirectory:
				return dtprops.browserSelectionInfo.pathDevicesRig
		return False
	
	def execute(self, context):
		dtlist = context.window_manager.democaptools_filelistdemca
		index = context.window_manager.democaptools_filelistdemca_index
		dtprops = context.window_manager.democaptools_properties
		if index >= 0 and index < len(dtlist):
			if not dtlist[index].isDirectory:
				if dtprops.browserSelectionInfo.pathDevicesRig:
					bpy.ops.object.mode_set(mode='OBJECT')
					bpy.ops.dragengine.import_rig('EXEC_DEFAULT', filepath=Demca.getAbsPath(
						dtlist[index].path, dtprops.browserSelectionInfo.pathDevicesRig))
		return {'FINISHED'}

class LIST_OT_DemcaBrowserImportDevicesAnimation(bpy.types.Operator):
	"""Import Devices Rig."""
	bl_idname = "democaptools_demcabrowser.importdevicesanimation"
	bl_label = "Import Devices Animation"
	
	@classmethod
	def poll(cls, context):
		if context.active_object and context.active_object.type == 'ARMATURE':
			dtlist = context.window_manager.democaptools_filelistdemca
			index = context.window_manager.democaptools_filelistdemca_index
			dtprops = context.window_manager.democaptools_properties
			if index >= 0 and index < len(dtlist):
				if not dtlist[index].isDirectory:
					return dtprops.browserSelectionInfo.pathDevicesAnimation
		return False
	
	def execute(self, context):
		if context.active_object and context.active_object.type == 'ARMATURE':
			dtlist = context.window_manager.democaptools_filelistdemca
			index = context.window_manager.democaptools_filelistdemca_index
			dtprops = context.window_manager.democaptools_properties
			if index >= 0 and index < len(dtlist):
				if not dtlist[index].isDirectory:
					if dtprops.browserSelectionInfo.pathDevicesAnimation:
						bpy.ops.dragengine.import_animation('EXEC_DEFAULT', filepath=Demca.getAbsPath(
							dtlist[index].path, dtprops.browserSelectionInfo.pathDevicesAnimation))
		return {'FINISHED'}

class VIEW3D_PT_DemocapTools(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'DEMoCap'
	bl_label = "DEMoCap Tools"
	
	def draw(self, context):
		pass

class VIEW3D_PT_DemocapToolsDemcaBrowser(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'DEMoCap'
	bl_parent_id = "VIEW3D_PT_DemocapTools"
	bl_label = "DEMCA Browser"
	
	def draw(self, context):
		#https://github.com/sketchfab/blender-plugin/blob/master/addons/io_sketchfab_plugin/__init__.py
		#https://sinestesia.co/blog/tutorials/using-uilists-in-blender/
		config = Configuration.get()
		windowManager = context.window_manager
		dtprops = windowManager.democaptools_properties
		
		layout = self.layout
		
		# browser
		row = layout.row(align=True)
		row.operator("democaptools_demcabrowser.changedirectory",
			text="Captured", icon='FILE_FOLDER').path = config.pathCaptureAnimations
		row.operator("democaptools_demcabrowser.changedirectory",
			text="Projects", icon='FILE_FOLDER').path = config.pathProjects
		
		layout.label(text="Directory: {}".format(os.path.split(dtprops.currentDirectory)[1]))
		
		row = layout.row()
		row.template_list("LIST_UL_DemcaBrowser", "File List", windowManager,
			"democaptools_filelistdemca", windowManager, "democaptools_filelistdemca_index")
		
		row = layout.row()
		row.operator("democaptools_demcabrowser.scanfiles", text="Scan Files")
		
		# information
		selinfo = dtprops.browserSelectionInfo
		
		layout.row().label(text="DEMCA Information:")
		column = layout.row().column(align=True)
		
		row = column.row()
		row.label(text="Filename")
		row.label(text=selinfo.filename)
		
		row = column.row()
		row.label(text="Timestamp")
		row.label(text=selinfo.timestamp)
		
		row = column.row()
		row.label(text="Character")
		row.label(text=selinfo.character)
		
		row = column.row()
		row.label(text="Configuration")
		row.label(text=selinfo.configuration)
		
		row = column.row()
		row.label(text="Playtime")
		row.label(text="{:.1f}s".format(selinfo.playtime))
		
		row = column.row()
		row.label(text="Framerate")
		row.label(text="{}".format(selinfo.frameRate))
		
		# import
		column = layout.row().column(align=True)
		column.operator("democaptools_demcabrowser.importanimation", icon='ACTION')
		column.operator("democaptools_demcabrowser.importdevicesrig", icon='ARMATURE_DATA')
		column.operator("democaptools_demcabrowser.importdevicesanimation", icon='ACTION')


def panelToolsRegister():
	registerClass(DemcaBrowserItem)
	registerClass(LIST_UL_DemcaBrowser)
	registerClass(DemcaBrowserSelectionInfo)
	registerClass(DemocapToolsPanelProperties)
	registerClass(LIST_OT_DemcaBrowserChdir)
	registerClass(LIST_OT_DemcaBrowserScanFiles)
	registerClass(LIST_OT_DemcaBrowserImportAnimation)
	registerClass(LIST_OT_DemcaBrowserImportDevicesRig)
	registerClass(LIST_OT_DemcaBrowserImportDevicesAnimation)
	registerClass(VIEW3D_PT_DemocapTools)
	registerClass(VIEW3D_PT_DemocapToolsDemcaBrowser)
	
	bpy.types.WindowManager.democaptools_properties = bpy.props.PointerProperty(type=DemocapToolsPanelProperties)
	bpy.types.WindowManager.democaptools_filelistdemca = bpy.props.CollectionProperty(type=DemcaBrowserItem)
	bpy.types.WindowManager.democaptools_filelistdemca_index = bpy.props.IntProperty(
		name="Index for filelistdemca", default=0, update=DemcaBrowser_SelectionChanged)
