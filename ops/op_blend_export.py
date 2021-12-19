from __future__ import annotations

import bpy
import os
import shutil

import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty
from .ops_super_import import import_icon
from .core import get_pref

if sys.platform == "win32":
    from ..clipboard.windows import PowerShellClipboard as Clipboard
elif sys.platform == "darwin":
    from ..clipboard.darwin.mac import MacClipboard as Clipboard

from ..exporter.default_blend import post_process_blend_file


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
            # win temp file
            temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')

        return temp_dir

    def execute(self, context):
        # copy buffer
        bpy.ops.view3d.copybuffer()
        # win support only(not sure the temp dir of macOS)
        temp_dir = self.get_temp_dir()
        if self.filepath == '': self.filepath = os.path.join(temp_dir, context.active_object.name + '.blend')

        if os.path.exists(self.filepath):
            os.remove(self.filepath)  # remove exist file

        post_process_blend_file(os.path.join(temp_dir, 'copybuffer.blend'), scripts_file_name=self.scripts_file_name)

        shutil.copy(os.path.join(temp_dir, 'copybuffer.blend'), self.filepath)
        # append obj to scene, mark slower

        # push
        if get_pref().post_push_to_clipboard:
            clipboard = Clipboard()
            clipboard.push_to_clipboard(paths=[self.filepath])

            self.report({'INFO'}, f'{context.active_object.name}.blend has been copied to Clipboard')

        if get_pref().post_open_dir:
            import subprocess
            if sys.platform == 'darwin':
                subprocess.check_call(['open', '--', temp_dir])
            elif sys.platform == 'win32':
                os.startfile(temp_dir)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_blend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_blend)
