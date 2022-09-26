from __future__ import annotations

import bpy
import os
import shutil

import sys
from pathlib import Path
from os.path import join, exists

from bpy.props import StringProperty, BoolProperty, EnumProperty
from .core import get_pref, PostProcess


class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform in {"darwin", "win32"}:
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_object is not None
                    and context.active_object.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )


class SPIO_OT_export_blend(ImageCopyDefault, bpy.types.Operator):
    """Export Selected objects to a blend file"""
    bl_idname = 'spio.export_blend'
    bl_label = 'Copy Blend'

    scripts_file_name: StringProperty(default='script_export_blend.py')
    filepath: StringProperty(default='')

    def get_temp_dir(self):
        ori_dir = bpy.context.preferences.filepaths.temporary_directory
        temp_dir = ori_dir
        if ori_dir == '' or not os.path.exists(ori_dir):
            temp_dir = str(Path(bpy.app.tempdir).parent)

        return temp_dir

    def execute(self, context):
        # copy buffer
        bpy.ops.view3d.copybuffer()
        temp_dir = self.get_temp_dir()  # win support only(not sure the temp dir of macOS)
        if self.filepath == '': self.filepath = os.path.join(temp_dir, context.active_object.name + '.blend')

        if exists(self.filepath):
            os.remove(self.filepath)  # remove exist file

        POST = PostProcess()
        POST.fix_blend(join(temp_dir, 'copybuffer.blend'),
                       scripts_file_name=self.scripts_file_name)
        # Copy
        shutil.copy(join(temp_dir, 'copybuffer.blend'),
                    self.filepath)
        # Prefs
        POST.copy_to_clipboard(paths=[self.filepath], op=self)
        POST.open_dir(self.filepath)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_blend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_blend)
