from __future__ import annotations

import bpy
import os
from os import getenv

import subprocess
import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty
from .ops_super_import import import_icon


class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform == "win32":
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_obejct is not None
                    and context.active_obejct.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )

    def get_args(self, script):
        powershell_args = [
            os.path.join(
                getenv("SystemRoot"),
                "System32",
                "WindowsPowerShell",
                "v1.0",
                "powershell.exe",
            ),
            "-NoProfile",
            "-NoLogo",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
        ]
        script = (
                "$OutputEncoding = "
                "[System.Console]::OutputEncoding = "
                "[System.Console]::InputEncoding = "
                "[System.Text.Encoding]::UTF8; "
                + "$PSDefaultParameterValues['*:Encoding'] = 'utf8'; "
                + script
        )
        args = powershell_args + ["& { " + script + " }"]
        return args


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

        script = (
            f"$file = '{filepath}'; "
            "$col = New-Object Collections.Specialized.StringCollection; "
            "$col.add($file); "
            "Add-Type -Assembly System.Windows.Forms; "
            "[System.Windows.Forms.Clipboard]::SetFileDropList($col); "
        )

        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        subprocess.Popen(**parms)

        self.report({'INFO'}, f'{context.active_object.name}.blend has been copied to Clipboard')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_blend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_blend)
