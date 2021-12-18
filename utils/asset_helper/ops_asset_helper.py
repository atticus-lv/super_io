import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty


class SPIO_OT_object_asset(bpy.types.Operator):
    bl_label = 'Object Asset'
    bl_idname = 'spio.object_asset'
    bl_options = {'UNDO_GROUPED'}

    clear: BoolProperty(name='Clear', default=False)
    action: EnumProperty(name='Type', items=[
        ('OBJECT', 'Object Only', '', 'OBJECT_DATA', 0),
        ('MATERIAL', 'Material Only', '', 'MATERIAL', 1),
        ('ALL', 'All', '', 'MATSHADERBALL', 2),
    ])

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'action')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for obj in context.selected_objects:
            # mark material
            if self.action in {'ALL', "MATERIAL"}:
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat and not self.clear:
                        mat.asset_mark()
                        mat.asset_generate_preview()
                    elif mat and self.clear:
                        mat.asset_clear()

            if self.action in {'ALL','OBJECT'}:
                if not self.clear:
                    obj.asset_mark()
                    obj.asset_generate_preview()
                else:
                    obj.asset_clear()

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_object_asset)
    # bpy.utils.register_class(SPIO_OT_material_asset)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_object_asset)
    # bpy.utils.unregister_class(SPIO_OT_material_asset)
