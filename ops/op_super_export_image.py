from __future__ import annotations

import bpy
import os
from os import getenv

import subprocess
import sys

from .ops_super_import import import_icon


class WM_OT_super_export_image(bpy.types.Operator):
    """Export Image to Clipboard"""

    bl_idname = 'wm.super_export_image'
    bl_label = 'Super Export'

    @classmethod
    def poll(_cls, context):
        if sys.platform == "win32":
            return (
                    context.area.type == "IMAGE_EDITOR"
                    and context.area.spaces.active.image is not None
                    and context.area.spaces.active.image.has_data is True
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

    def execute(self, context):
        active_image = context.area.spaces.active.image
        image_path = os.path.join(bpy.app.tempdir, f'{active_image.name}.png')

        bpy.ops.image.save_as(filepath=image_path, save_as_render=True, copy=True)

        script = (
            "Add-Type -Assembly System.Windows.Forms; "
            "Add-Type -Assembly System.Drawing; "
            f"$image = [Drawing.Image]::FromFile('{image_path}'); "
            "$imageStream = New-Object System.IO.MemoryStream; "
            "$image.Save($imageStream, [System.Drawing.Imaging.ImageFormat]::Png); "
            "$dataObj = New-Object System.Windows.Forms.DataObject('Bitmap', $image); "
            "$dataObj.SetData('PNG', $imageStream); "
            "[System.Windows.Forms.Clipboard]::SetDataObject($dataObj, $true); "
        )

        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        subprocess.Popen(**parms)

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.super_export_image', icon_value=import_icon.get_image_icon_id())


def register():
    bpy.utils.register_class(WM_OT_super_export_image)

    bpy.types.IMAGE_MT_image.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(WM_OT_super_export_image)

    bpy.types.IMAGE_MT_image.remove(draw_menu)
