from __future__ import annotations

import bpy
import os
from os import getenv

import subprocess
import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty
from .ops_super_import import import_icon
from ..clipboard.windows import PowerShellClipboard
from ..exporter.utils import run_blend_fix

class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform == "win32":
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_object is not None
                    and context.active_object.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )


class SPIO_OT_export_blend(ImageCopyDefault, bpy.types.Operator):
    """Export Selected obj as blend file"""
    bl_idname = 'spio.export_blend'
    bl_label = 'Copy Blend'


    def execute(self, context):
        bpy.ops.view3d.copybuffer()  # copy buffer

        ori_dir = context.preferences.filepaths.temporary_directory
        temp_dir = ori_dir
        if ori_dir == '':
            temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')

        filepath = os.path.join(temp_dir, context.active_object.name + '.blend')
        if os.path.exists(filepath): os.remove(filepath)
        os.rename(os.path.join(temp_dir, 'copybuffer.blend'), filepath)

        run_blend_fix(filepath)

        clipboard = PowerShellClipboard()
        clipboard.push_to_clipboard(path=filepath)

        self.report({'INFO'}, f'{context.active_object.name}.blend has been copied to Clipboard')

        return {'FINISHED'}



def register():
    bpy.utils.register_class(SPIO_OT_export_blend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_blend)