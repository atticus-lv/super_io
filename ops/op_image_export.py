import bpy
import os
import sys

from ..clipboard.windows import PowerShellClipboard


class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform == "win32":
            return (
                    context.area.type == "IMAGE_EDITOR"
                    and context.area.spaces.active.image is not None
                    and context.area.spaces.active.image.has_data is True
            )


class SPIO_OT_export_pixel(ImageCopyDefault, bpy.types.Operator):
    """Export as Image Pixel"""
    bl_idname = 'spio.export_pixel'
    bl_label = 'Copy Pixel'

    def execute(self, context):
        active_image = context.area.spaces.active.image
        image_path = os.path.join(bpy.app.tempdir, f'{active_image.name}.png')

        bpy.ops.image.save_as(filepath=image_path, save_as_render=True, copy=True)
        # push to clipboard
        clipboard = PowerShellClipboard()
        clipboard.push_pixel_to_clipboard(path=image_path)

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


class SPIO_OT_export_image(ImageCopyDefault, bpy.types.Operator):
    """Export as Image File"""
    bl_idname = 'spio.export_image'
    bl_label = 'Copy Image'

    def execute(self, context):
        active_image = context.area.spaces.active.image
        image_path = os.path.join(bpy.app.tempdir, f'{active_image.name}.png')

        bpy.ops.image.save_as(filepath=image_path, save_as_render=True, copy=True)

        clipboard = PowerShellClipboard()
        clipboard.push_to_clipboard(paths=[image_path])

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_pixel)
    bpy.utils.register_class(SPIO_OT_export_image)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_pixel)
    bpy.utils.unregister_class(SPIO_OT_export_image)
