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

from .configuration import Configuration
from .panel_demca_browser import panelDemcaBrowserRegister
from .panel_correctionbones import panelCorrectionBonesRegister
from .panel_live import panelLiveRegister
from .utils import registerKnownClasses, unregisterRegisteredClasses, delog
from .version import addonVersion

delog("Version {}".format(addonVersion))

bl_info = {
    "name": "DEMoCap Tools",
    "description": "DEMoCapTools",
    "author": "DragonDreams",
    "version": ({VERSION_MAJOR}, {VERSION_MINOR}),
    "blender": (3, 0, 0),
    "location": "View3D > Tools > DEMoCap",
    "warning": "",
    "wiki_url": "https://developer.dragondreams.ch/wiki/doku.php/democap:blender_democaptools",
    "tracker_url": "https://github.com/LordOfDragons/democap/issues",
    "link": "https://dragondreams.ch/?page_id=938",
    "support": "COMMUNITY",
    "category": "Import-Export"
    }


def register():
    """ Register add-on. """
    delog("Register classes")
    Configuration.get()
    panelDemcaBrowserRegister()
    panelCorrectionBonesRegister()
    panelLiveRegister()
    registerKnownClasses()


def unregister():
    """ Unregister add-on. """
    unregisterRegisteredClasses()
