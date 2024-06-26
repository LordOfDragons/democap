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

registeredClasses = []


knownClasses = []
registeredClasses = []
logPrefix = "DEMoCap Add-On: "


def delog(message):
    print(logPrefix + message)


def registerClass(cls):
    if cls not in knownClasses:
        knownClasses.append(cls)
    if cls not in registeredClasses:
        bpy.utils.register_class(cls)
        registeredClasses.append(cls)


def registerKnownClasses():
    for cls in knownClasses:
        registerClass(cls)


def unregisterRegisteredClasses():
    for cls in reversed(registeredClasses):
        bpy.utils.unregister_class(cls)
    del registeredClasses[:]


def appendToMenu(menu, cls):
    def menu_func(self, context):
        self.layout.operator(
            cls.bl_idname, text=cls.bl_label,
            icon=cls.bl_icon if hasattr(cls, "bl_icon") else None)
    menu.append(menu_func)


def appendSubMenuToMenu(menu, cls):
    def menu_func(self, context):
        self.layout.menu(cls.bl_idname)
    menu.append(menu_func)


def layOpRow(layout, cls, text=None, icon=None):
    if not text:
        if hasattr(cls, "bl_label_button"):
            text = cls.bl_label_button
        else:
            text = cls.bl_label
    if not icon and hasattr(cls, "bl_icon"):
        icon = cls.bl_icon
    if not icon:
        icon = 'NONE'
    return layout.row(align=True).operator(
        operator=cls.bl_idname, text=text, icon=icon)


def layPropRow(layout, data, property, expand=True, readonly=False):
    # prop = getattr(data, property)
    # readonly not supported yet by blender
    return layout.row(align=True).prop(
        data=data, property=property, expand=expand)


def layLabRow(layout, text):
    return layout.row(align=True).label(text=text)


def flatten(mat):
    dim = len(mat)
    return [mat[j][i] for i in range(dim) for j in range(dim)]
