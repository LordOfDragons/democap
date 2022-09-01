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
from bpy.app.handlers import persistent


logger = logging.getLogger(__name__)


updaters = []
isRendering = False


def addFrameUpdater(updater):
	updaters.append(updater)

def removeFrameUpdater(updater):
	updaters.remove(updater)


@persistent
def onRenderInit(scene):
	global isRendering
	isRendering = True

@persistent
def onRenderCancel(scene):
	global isRendering
	isRendering = False

@persistent
def onRenderComplete(scene):
	global isRendering
	isRendering = False

@persistent
def onFrameChangePost(scene):
	if not isRendering:
		for x in updaters:
			x.onFrameUpdate(scene)

def registerFrameUpdaterHandlers():
	bpy.app.handlers.render_init.append(onRenderInit)
	bpy.app.handlers.render_cancel.append(onRenderCancel)
	bpy.app.handlers.render_complete.append(onRenderComplete)
	#bpy.app.handlers.frame_change_pre.append(onFrameChangePre)
	bpy.app.handlers.frame_change_post.append(onFrameChangePost)
	logger.info("DEMoCapLive FrameUpdater: Registered handlers")

def unregisterFrameUpdaterHandlers():
	bpy.app.handlers.render_init.remove(onRenderInit)
	bpy.app.handlers.render_cancel.remove(onRenderCancel)
	bpy.app.handlers.render_complete.remove(onRenderComplete)
	#bpy.app.handlers.frame_change_pre.remove(onFrameChangePre)
	bpy.app.handlers.frame_change_post.remove(onFrameChangePost)
	logger.info("DEMoCapLive FrameUpdater: Unregistered handlers")
