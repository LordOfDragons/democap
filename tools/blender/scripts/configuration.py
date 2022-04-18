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
import json
import platform

class Configuration:
	_instance = None
	
	@classmethod
	def get(cls):
		if not cls._instance:
			cls._instance = cls()
		return cls._instance
	
	def __init__(self):
		self.data = {}
		
		if platform.system() == "Windows":
			commonPath = ["DELaunchers", "Config", "games", "e31f1c11-3ca6-c66b-adca-95484bedfc1f"]
			
			pathBase = os.path.join(os.getenv("LOCALAPPDATA"), "Packages",
				"DragonDreams.Dragengine.GameEngine_14hw6vre8sh8m", "LocalCache", "Roaming", *commonPath)
			if not os.path.exists(pathBase):
				pathBase = os.path.join(os.getenv("APPDATA"), *commonPath)
			
			self.pathDemocapConfig = os.path.join(pathBase, "config")
			self.pathDemocapOverlay = os.path.join(pathBase, "overlay")
			self.pathDemocapCapture = os.path.join(pathBase, "capture")
			
		elif platform.system() == "Darwin":
			pathBase = os.path.expanduser("~/.config/delauncher/games/e31f1c11-3ca6-c66b-adca-95484bedfc1f")
			self.pathDemocapConfig = os.path.join(pathBase, "config")
			self.pathDemocapOverlay = os.path.join(pathBase, "overlay")
			self.pathDemocapCapture = os.path.join(pathBase, "capture")
			
		else:
			pathBase = os.path.expanduser("~/.config/delauncher/games/e31f1c11-3ca6-c66b-adca-95484bedfc1f")
			self.pathDemocapConfig = os.path.join(pathBase, "config")
			self.pathDemocapOverlay = os.path.join(pathBase, "overlay")
			self.pathDemocapCapture = os.path.join(pathBase, "capture")
		
		self.pathCaptureAnimations = os.path.join(self.pathDemocapCapture, "animations")
		self.pathProjects = os.path.join(self.pathDemocapConfig, "projects")
		
		self.pathScriptTools = bpy.utils.user_resource("CONFIG", path="democap-tools", create=True)
		self.pathScriptConfig = os.path.join(self.pathScriptTools, "config.json")
		
		print("DEMoCap-Tools: Path Overlay '{}'".format(self.pathDemocapOverlay))
		print("DEMoCap-Tools: Path Capture '{}'".format(self.pathDemocapCapture))
		print("DEMoCap-Tools: Path Capture Animations '{}'".format(self.pathCaptureAnimations))
		print("DEMoCap-Tools: Path Projects '{}'".format(self.pathProjects))
		print("DEMoCap-Tools: Config File '{}'".format(self.pathScriptConfig))
		
		if os.path.exists(self.pathScriptConfig):
			with open(self.pathScriptConfig, 'rb') as f:
				self.data = json.loads(f.read().decode('utf-8'))
	
	
	def getDemcaBrowserCurrentDirectory(self):
		return self.getAt('demcaBrowserCurDir', self.pathCaptureAnimations)
	
	def setDemcaBrowserCurrentDirectory(self, directory):
		self.setAt('demcaBrowserCurDir', directory)
	
	
	
	def getAt(self, key, default):
		if key in self.data:
			return self.data[key]
		return default
	
	def setAt(self, key, value):
		self.data[key] = value
		self.writeConfig()
	
	def clearAt(self, key):
		if key in self.data:
			del self.data[key]
		self.writeConfig()
	
	def writeConfig(self):
		with open(self.pathScriptConfig, 'wb+') as f:
			f.write(json.dumps(self.data).encode('utf-8'))
