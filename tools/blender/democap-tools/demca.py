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
import xml.etree.ElementTree as ET
import traceback
from datetime import datetime

from .utils import registerClass
from .configuration import Configuration

class Demca:
	def __init__(self, path):
		self.path = path
		self.characterProfile = ""
		self.characterConfiguration = ""
		self.pathAnimation = ""
		self.playtime = 0.0
		self.frameRate = 25
		self.pathDevicesRig = ""
		self.pathDevicesAnimation = ""
		self.pathObjectRig = ""
		self.pathObjectAnimation = ""
		self.success = False
		self.loadDemca()
	
	def loadDemca(self):
		try:
			self.filename = os.path.split(self.path)[1]
			
			tree = ET.parse(self.path)
			ns = {"ns": ""}
			
			root = tree.getroot()
			if root.tag != "mocapAnimation":
				raise "invalid root tag: " + root.tag
			self.timestamp = datetime.strptime(root.find("timestamp", ns).text, '%Y-%m-%dT%H:%M:%S')
			self.formattedTimestamp = self.timestamp.strftime("%H:%M:%S %m-%d %Y")
			
			nodeCharacter = root.find("character", ns)
			if nodeCharacter:
				self.characterProfile = nodeCharacter.find("profileName", ns).text
				self.characterConfiguration = nodeCharacter.find("configurationName", ns).text
			
			nodeAnimation = root.find("capturedAnimation", ns)
			if nodeAnimation:
				self.pathAnimation = nodeAnimation.find("pathAnimation", ns).text
				self.playtime = float(nodeAnimation.find("playtime", ns).text)
				self.frameRate = int(nodeAnimation.find("frameRate", ns).text)
			
			nodeDevices = root.find("capturedAnimationDevices", ns)
			if nodeDevices:
				self.pathDevicesRig = nodeDevices.find("pathRig", ns).text
				self.pathDevicesAnimation = nodeDevices.find("pathAnimation", ns).text
			
			nodeObject = root.find("capturedAnimationObject", ns)
			if nodeObject:
				self.pathObjectRig = nodeObject.find("pathRig", ns).text
				self.pathObjectAnimation = nodeObject.find("pathAnimation", ns).text
				self.playtime = float(nodeObject.find("playtime", ns).text)
				self.frameRate = int(nodeObject.find("frameRate", ns).text)
			
			self.success = True
		except Exception:
			self.success = False
			traceback.print_exc()
	
	@classmethod
	def getAbsPath(self, pathDemca, relativePath):
		path = relativePath
		
		if path.startswith("/"):
			components = path[1:].split("/")
			print(components)
			if components[0] == "capture":
				path = os.path.join(Configuration.get().pathDemocapCapture, *components[1:])
			elif components[0] == "config":
				path = os.path.join(Configuration.get().pathDemocapConfig, *components[1:])
			else:
				path = os.path.join(Configuration.get().pathDemocapOverlay, *components)
		else:
			# we have to find the project file to find the right path
			basePath = os.path.split(pathDemca)[0]
			while basePath:
				parentDir = os.path.split(basePath)[0]
				if basePath.endswith("-data"):
					if os.path.exists(os.path.join(parentDir, "{}.demcp".format(basePath[0:-5]))):
						break
				basePath = parentDir
			
			if basePath:
				path = os.path.join(basePath, path)
			else:
				raise Exception("Failed finding project file")
		
		return path
