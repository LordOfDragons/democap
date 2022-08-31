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

from mathutils import Vector, Quaternion, Matrix

transformPosition = Matrix(((-1,0,0,0), (0,0,-1,0), (0,1,0,0), (0,0,0,1)))
transformBonePosition = Matrix(((1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1)))

def convertBoneName(name):
	return name

def convertPosition(position):
	return Vector((-position.x, -position.z, position.y))

def convertOrientation(orientation):
	return Quaternion((orientation.w, -orientation.x, -orientation.z, orientation.y))

def convertTransform(position, orientation):
	return Matrix.LocRotScale(convertPosition(position), convertOrientation(orientation), Vector((1,1,1)))

def convertBonePosition(position):
	return Vector((position.x, position.z, position.y))

def convertBoneOrientation(orientation):
	return Quaternion((-orientation.w, orientation.x, orientation.z, orientation.y))

def convertBoneTransform(position, orientation):
	return convertBoneOrientation(orientation).to_matrix().to_4x4()\
		@ Matrix.Translation(convertBonePosition(position))
	"""return Matrix.LocRotScale(convertBonePosition(position), convertBoneOrientation(orientation), Vector((1,1,1)))"""
