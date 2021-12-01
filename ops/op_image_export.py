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

        parms = {
            'args': self.get_args(self.script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        subprocess.Popen(**parms)

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


class SPIO_OT_export_pixel(ImageCopyDefault, bpy.types.Operator):
    bl_idname = 'spio.export_pixel'
    bl_label = 'Copy Pixel'

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


class SPIO_OT_export_image(ImageCopyDefault, bpy.types.Operator):
    bl_idname = 'spio.export_image'
    bl_label = 'Copy Image'

    def execute(self, context):
        active_image = context.area.spaces.active.image
        image_path = os.path.join(bpy.app.tempdir, f'{active_image.name}.png')

        bpy.ops.image.save_as(filepath=image_path, save_as_render=True, copy=True)

        script = (
            f"$file = '{image_path}';"
            '$col = New-Object Collections.Specialized.StringCollection;'
            '$col.add($file);'
            "Add-Type -Assembly System.Windows.Forms; "
            "[System.Windows.Forms.Clipboard]::SetFileDropList($col)"
        )
        # file list
        # f"$filelist = '{image_path}'"
        # 'foreach($file in $filelist){$col.add($file)};'

        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
        print(parms)
        subprocess.Popen(**parms)

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


from .utils import PopupExportMenu


class WM_OT_super_export(bpy.types.Operator):
    """Export to Clipboard"""

    bl_idname = 'wm.super_export'
    bl_label = 'Super Export'

    def execute(self, context):
        popup = PopupExportMenu(temp_path=None, context=context)
        popup.default_image_menu()
        return {'FINISHED'}


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.super_export', icon_value=import_icon.get_image_icon_id())


def register():
    bpy.utils.register_class(SPIO_OT_export_pixel)
    bpy.utils.register_class(SPIO_OT_export_image)
    bpy.utils.register_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_pixel)
    bpy.utils.unregister_class(SPIO_OT_export_image)
    bpy.utils.unregister_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.remove(draw_menu)
