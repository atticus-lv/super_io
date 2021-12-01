import bpy

from .utils import PopupExportMenu
from .ops_super_import import import_icon


class WM_OT_super_export(bpy.types.Operator):
    """Export to Clipboard"""

    bl_idname = 'wm.super_export'
    bl_label = 'Super Export'

    def execute(self, context):
        popup = PopupExportMenu(temp_path=None, context=context)
        if context.area.type == "VIEW_3D":
            popup.default_blend_menu()
        elif context.area.type == "IMAGE_EDITOR":
            popup.default_image_menu()
        return {'FINISHED'}


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('wm.super_export', icon_value=import_icon.get_image_icon_id())


def register():
    bpy.utils.register_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(WM_OT_super_export)

    bpy.types.IMAGE_MT_image.remove(draw_menu)
