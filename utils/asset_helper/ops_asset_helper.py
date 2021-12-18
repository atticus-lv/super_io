import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty


class SPIO_OT_object_asset(bpy.types.Operator):
    bl_label = 'Object Asset'
    bl_idname = 'spio.object_asset'
    bl_options = {'UNDO_GROUPED'}

    clear: BoolProperty(name='Clear', default=False)

    def execute(self, context):
        for obj in context.selected_objects:
            if not self.clear:
                obj.asset_mark()
            else:
                obj.asset_clear()

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {"FINISHED"}


# class SPIO_OT_material_asset(bpy.types.Operator):
#     bl_label = 'Material Asset'
#     bl_idname = 'spio.material_asset'
#     bl_options = {'UNDO_GROUPED'}
#
#     clear:BoolProperty(name = 'Clear',default=False)
#
#     def execute(self, context):
#         for obj in context.selected_objects:
#             for slot in obj.material_slots:
#                 mat = slot.material
#
#                 if not self.clear:
#                     mat.asset_mark()
#                     mat.asset_generate_preview()
#                 else:
#                     mat.asset_clear()
#
#         for window in bpy.context.window_manager.windows:
#             for area in window.screen.areas:
#                 area.tag_redraw()
#
#        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_object_asset)
    # bpy.utils.register_class(SPIO_OT_material_asset)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_object_asset)
    # bpy.utils.unregister_class(SPIO_OT_material_asset)
