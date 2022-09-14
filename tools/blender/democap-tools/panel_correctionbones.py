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

import mathutils
import bpy
import os
from fnmatch import fnmatch
from math import pi

from .configuration import Configuration
from .utils import registerClass, flatten


class ARMATURE_OT_AddCorrectionBones(bpy.types.Operator):
    """Add correction bones."""
    bl_idname = "democaptools.addcorrectionbones"
    bl_label = "Add correction bones"
    bl_description = "Add correction bones for selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    boneGroupName = "DEMoCap Correction"
    boneNamePrefix = "ik.mocap."
    constraintNameAdjustRotation = "DEMoCap Correction Rotation"
    constraintNameAdjustTransform = "DEMoCap Correction Transform"

    adjustLocation: bpy.props.BoolProperty(
        name="Adjust Location", default=False)
    scaleLength: bpy.props.FloatProperty(
        name="Scale Length", default=0.65, min=0.01, soft_min=0.1, soft_max=1)

    @classmethod
    def poll(cls, context):
        return (context.active_object
                and context.active_object.type == 'ARMATURE'
                and context.mode == 'POSE'
                and context.selected_pose_bones
                and len(context.selected_pose_bones) > 0)

    def execute(self, context):
        if (not context.active_object
                or context.active_object.type != 'ARMATURE'
                or context.mode != 'POSE'
                or not context.selected_pose_bones
                or len(context.selected_pose_bones) == 0):
            return {'CANCELLED'}

        boneGroupName = ARMATURE_OT_AddCorrectionBones.boneGroupName
        boneNamePrefix = ARMATURE_OT_AddCorrectionBones.boneNamePrefix
        constraintNameAdjustTransform = \
            ARMATURE_OT_AddCorrectionBones.constraintNameAdjustTransform
        constraintNameAdjustRotation = \
            ARMATURE_OT_AddCorrectionBones.constraintNameAdjustRotation

        windowManager = context.window_manager
        object = context.active_object
        armature = object.data
        selectedBones = list(context.selected_pose_bones[:])
        adjustLocation = self.adjustLocation
        scaleLength = self.scaleLength
        useWorldSpace = windowManager.democaptools_corrbones_worldspace

        # add edit bone
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')

        addedBones = []

        for orgPoseBone in selectedBones:
            orgEditBone = armature.edit_bones[orgPoseBone.name]
            newName = boneNamePrefix
            if useWorldSpace:
                newName = newName + "w."
            newName = newName + orgPoseBone.name
            if newName in armature.edit_bones:
                continue

            bone = armature.edit_bones.new(newName)
            bone.head = orgEditBone.head
            bone.tail = orgEditBone.tail
            bone.roll = orgEditBone.roll
            bone.length = orgEditBone.length * scaleLength
            bone.layers = orgEditBone.layers
            bone.parent = orgEditBone.parent
            bone.select = True

            if useWorldSpace:
                bone.tail = bone.head + mathutils.Vector((0, bone.length, 0))
                bone.roll = 0
                bone.parent = None

            addedBones.append((orgPoseBone.name, newName))

        # add pose bone to bone group
        bpy.ops.object.mode_set(mode='POSE')

        pose = object.pose

        if boneGroupName in pose.bone_groups:
            boneGroup = pose.bone_groups[boneGroupName]
        else:
            colorSets = ['THEME{:02d}'.format(x) for x in range(1, 21)]
            for boneGroup in pose.bone_groups:
                try:
                    colorSets.remove(colorSets.index(boneGroup.color_set))
                except ValueError:
                    pass  # not in list

            if not colorSets:
                colorSets.add('THEME01')

            boneGroup = pose.bone_groups.new(name=boneGroupName)
            boneGroup.color_set = next(iter(colorSets))

        for addedBone in addedBones:
            poseBone = pose.bones[addedBone[1]]
            poseBone.bone_group = boneGroup

        # add constraint to original pose bone
        for addedBone in addedBones:
            poseBone = pose.bones[addedBone[0]]

            if useWorldSpace:
                constraint = poseBone.constraints.new('TRANSFORM')
                constraint.influence = 1
                constraint.name = constraintNameAdjustRotation
                constraint.show_expanded = True
                constraint.from_min_x_rot = -pi
                constraint.from_min_y_rot = -pi
                constraint.from_min_z_rot = -pi
                constraint.from_max_x_rot = pi
                constraint.from_max_y_rot = pi
                constraint.from_max_z_rot = pi
                constraint.to_min_x_rot = -pi
                constraint.to_min_y_rot = -pi
                constraint.to_min_z_rot = -pi
                constraint.to_max_x_rot = pi
                constraint.to_max_y_rot = pi
                constraint.to_max_z_rot = pi
                constraint.owner_space = 'WORLD'
                constraint.target_space = 'WORLD'
                constraint.target = object
                constraint.subtarget = addedBone[1]
                constraint.from_rotation_mode = 'AUTO'
                constraint.to_euler_order = 'AUTO'
                constraint.map_to_x_from = 'X'
                constraint.map_to_y_from = 'Y'
                constraint.map_to_z_from = 'Z'
                constraint.map_from = 'ROTATION'
                constraint.map_to = 'ROTATION'
                constraint.use_motion_extrapolate = True
                constraint.mix_mode_rot = 'BEFORE'

            if adjustLocation:
                if useWorldSpace:
                    constraint = poseBone.constraints.new('TRANSFORM')
                    constraint.influence = 1
                    constraint.name = constraintNameAdjustTransform
                    constraint.show_expanded = True
                    constraint.from_min_x = 0
                    constraint.from_min_y = 0
                    constraint.from_min_z = 0
                    constraint.from_max_x = 1
                    constraint.from_max_y = 1
                    constraint.from_max_z = 1
                    constraint.to_min_x = 0
                    constraint.to_min_y = 0
                    constraint.to_min_z = 0
                    constraint.to_max_x = 1
                    constraint.to_max_y = 1
                    constraint.to_max_z = 1
                    constraint.owner_space = 'WORLD'
                    constraint.target_space = 'LOCAL'
                    constraint.target = object
                    constraint.subtarget = addedBone[1]
                    constraint.map_to_x_from = 'X'
                    constraint.map_to_y_from = 'Y'
                    constraint.map_to_z_from = 'Z'
                    constraint.map_from = 'LOCATION'
                    constraint.map_to = 'LOCATION'
                    constraint.use_motion_extrapolate = True
                    constraint.mix_mode_rot = 'ADD'
                else:
                    constraint = poseBone.constraints.new('COPY_TRANSFORMS')
                    constraint.influence = 1
                    constraint.name = constraintNameAdjustTransform
                    constraint.show_expanded = True
                    constraint.owner_space = 'LOCAL'
                    constraint.target_space = 'LOCAL'
                    constraint.target = object
                    constraint.subtarget = addedBone[1]
                    constraint.mix_mode = 'BEFORE'
                    constraint.head_tail = 0
            elif not useWorldSpace:
                constraint = poseBone.constraints.new('COPY_ROTATION')
                constraint.influence = 1
                constraint.name = constraintNameAdjustRotation
                constraint.show_expanded = True
                constraint.owner_space = 'LOCAL'
                constraint.target_space = 'LOCAL'
                constraint.target = object
                constraint.subtarget = addedBone[1]
                constraint.euler_order = 'AUTO'
                constraint.use_x = True
                constraint.use_y = True
                constraint.use_z = True
                constraint.invert_x = False
                constraint.invert_y = False
                constraint.invert_z = False
                constraint.mix_mode = 'BEFORE'

        return {'FINISHED'}


class VIEW3D_PT_DemocapToolsCorrectionBones(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DEMoCap'
    bl_label = "Correction Bones"
    bl_description = "DEMoCap Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        config = Configuration.get()
        windowManager = context.window_manager
        dtprops = windowManager.democaptools_properties

        layout = self.layout

        # correction bones
        row = layout.row(align=True)
        row.operator("democaptools.addcorrectionbones",
                     text="Add Rot").adjustLocation = False
        row.operator("democaptools.addcorrectionbones",
                     text="Add Rot+Loc").adjustLocation = True

        row = layout.row(align=True)
        row.prop(windowManager, "democaptools_corrbones_worldspace",
                 expand=True)

        column = layout.row().column(align=True)
        column.operator("democaptools.copybonetransform",
                        text="Copy Bone Matrices", icon='COPYDOWN')
        column.operator("democaptools.aligncorrectionbones",
                        text="Align Correction Bones", icon='PASTEDOWN')


class CopyBufferBoneTransform(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")
    matrix: bpy.props.FloatVectorProperty(subtype='MATRIX', size=16)


class ARMATURE_OT_CopyBoneTransform(bpy.types.Operator):
    """Copy bone transforms."""
    bl_idname = "democaptools.copybonetransform"
    bl_label = "Copy bone transform"

    @classmethod
    def poll(cls, context):
        return (context.active_object
                and context.active_object.type == 'ARMATURE'
                and context.mode == 'POSE'
                and context.selected_pose_bones
                and len(context.selected_pose_bones) > 0)

    def execute(self, context):
        if (not context.active_object
                or context.active_object.type != 'ARMATURE'
                or context.mode != 'POSE'
                or not context.selected_pose_bones
                or len(context.selected_pose_bones) == 0):
            return {'CANCELLED'}

        boneNamePrefix = ARMATURE_OT_AddCorrectionBones.boneNamePrefix
        pose = context.active_object.pose

        copybuffer = context.window_manager.\
            democaptools_copybuffer_bonetransforms
        copybuffer.clear()

        for selectedBone in context.selected_pose_bones:
            bone = copybuffer.add()
            bone.name = selectedBone.name
            bone.matrix = flatten(selectedBone.matrix)

            # if this is correction bone also copy the original bone
            if selectedBone.name.startswith(boneNamePrefix):
                stateName = selectedBone.name[len(boneNamePrefix):]
                if stateName.startswith("w."):
                    stateName = stateName[2:]
                if stateName in pose.bones:
                    selectedBone = pose.bones[stateName]
                    bone = copybuffer.add()
                    bone.name = selectedBone.name
                    bone.matrix = flatten(selectedBone.matrix)
        return {'FINISHED'}


class ARMATURE_OT_AlignCorrectionBones(bpy.types.Operator):
    """Align correction bones using copied bone transforms."""
    bl_idname = "democaptools.aligncorrectionbones"
    bl_label = "Align correction bones using copied bone transforms"
    bl_options = {'REGISTER', 'UNDO'}

    class BoneState:
        def __init__(self, orgBone, correctedBone, boneChain,
                     matrix, useWorldSpace):
            self.orgBone = orgBone
            self.correctedBone = correctedBone
            self.boneChain = boneChain
            self.matrix = matrix
            self.useWorldSpace = useWorldSpace

    @classmethod
    def poll(cls, context):
        return (context.active_object
                and context.active_object.type == 'ARMATURE'
                and context.mode == 'POSE'
                and context.selected_pose_bones
                and len(context.selected_pose_bones) > 0
                and len(context.window_manager.
                        democaptools_copybuffer_bonetransforms) > 0)

    def execute(self, context):
        if (not context.active_object
                or context.active_object.type != 'ARMATURE'
                or context.mode != 'POSE'
                or not context.selected_pose_bones
                or len(context.selected_pose_bones) == 0
                or len(context.window_manager.
                       democaptools_copybuffer_bonetransforms) == 0):
            return {'CANCELLED'}

        boneNamePrefix = ARMATURE_OT_AddCorrectionBones.boneNamePrefix
        constraintNameAdjustTransform = \
            ARMATURE_OT_AddCorrectionBones.constraintNameAdjustTransform
        constraintNameAdjustRotation = \
            ARMATURE_OT_AddCorrectionBones.constraintNameAdjustRotation

        copybuffer = {}
        for cb in context.window_manager.democaptools_copybuffer_bonetransforms:
            copybuffer[cb.name] = cb.matrix

        obj = context.active_object
        pose = obj.pose

        boneStates = []
        for correctedBone in context.selected_pose_bones:
            if not correctedBone.name.startswith(boneNamePrefix):
                continue

            stateName = correctedBone.name[len(boneNamePrefix):]
            useWorldSpace = stateName.startswith("w.")
            if useWorldSpace:
                stateName = stateName[2:]
            if stateName not in pose.bones or stateName not in copybuffer:
                continue

            orgBone = pose.bones[stateName]
            boneChain = orgBone.parent_recursive

            insertBefore = len(boneStates)
            for i in range(len(boneStates)):
                if orgBone in boneStates[i].boneChain:
                    insertBefore = i
                    break

            boneStates.insert(insertBefore,
                              ARMATURE_OT_AlignCorrectionBones.BoneState(
                                  orgBone, correctedBone, boneChain,
                                  copybuffer[stateName], useWorldSpace))

        matFlip = mathutils.Matrix.Rotation(pi, 4, 'Z')

        for boneState in boneStates:
            orgmat = boneState.orgBone.matrix
            invorgmat = orgmat.inverted()
            pastemat = boneState.matrix
            corrmat = boneState.correctedBone.matrix

            corrmat = pastemat @ invorgmat @ corrmat

            boneState.correctedBone.matrix = corrmat

            if not [x for x in boneState.orgBone.constraints
                    if x.name == constraintNameAdjustTransform]:
                boneState.correctedBone.location = mathutils.Vector()

            context.view_layer.update()

        return {'FINISHED'}


def panelCorrectionBonesRegister():
    registerClass(ARMATURE_OT_AddCorrectionBones)
    registerClass(VIEW3D_PT_DemocapToolsCorrectionBones)
    registerClass(CopyBufferBoneTransform)
    registerClass(ARMATURE_OT_CopyBoneTransform)
    registerClass(ARMATURE_OT_AlignCorrectionBones)

    bpy.types.WindowManager.democaptools_copybuffer_bonetransforms = \
        bpy.props.CollectionProperty(type=CopyBufferBoneTransform)
    bpy.types.WindowManager.democaptools_corrbones_worldspace = \
        bpy.props.BoolProperty(
            name="Use World Space",
            default=False,
            description="Use World Space instead of Local Space")
