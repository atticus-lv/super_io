import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty

mark_list = []


def redraw_window():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def update_mark_list(self, context):
    global mark_list
    mark_list.clear()

    def mark_obj():
        for obj in context.selected_objects:
            mark_list.append(obj)

    def mark_mat():
        for obj in context.selected_objects:
            for slot in obj.material_slots:
                mat = slot.material
                if mat:
                    if mat not in mark_list:
                        mark_list.append(mat)

    if self.action == 'OBJECT':
        mark_obj()
    elif self.action == 'MATERIAL':
        mark_mat()
    elif self.action == 'ALL':
        mark_obj()
        mark_mat()

    redraw_window()


class object_asset(bpy.types.Operator):
    bl_options = {'UNDO_GROUPED'}

    clear = False

    action: EnumProperty(name='Type', items=[
        ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
        ('MATERIAL', 'Material', '', 'MATERIAL', 1),
        ('ALL', 'All', '', 'MATSHADERBALL', 2),
    ], update=update_mark_list)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, 'action', expand=True)

        col = layout.box().column(align=True)
        if len(mark_list) == 0:
            col.label(text = 'None')
        for obj in mark_list:
            if self.clear:
                if obj.asset_data is None: continue
                col.label(text=obj.name, icon='OBJECT_DATA' if isinstance(obj, bpy.types.Object) else 'MATERIAL')
            else:
                col.label(text=obj.name, icon='OBJECT_DATA' if isinstance(obj, bpy.types.Object) else 'MATERIAL')

    def invoke(self, context, event):
        update_mark_list(self, context)

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for obj in mark_list:
            if not self.clear:
                obj.asset_mark()
                obj.asset_generate_preview()
            else:
                obj.asset_clear()

        redraw_window()

        return {"FINISHED"}


class SPIO_OT_mark_object_asset(object_asset, bpy.types.Operator):
    """Mark Selected Objects As Asset"""
    bl_label = 'Mark Selected Objects As Asset'
    bl_idname = 'spio.mark_object_asset'
    clear = False


class SPIO_OT_clear_object_asset(object_asset, bpy.types.Operator):
    """Clear Selected Asset"""
    bl_label = 'Clear Selected Asset'
    bl_idname = 'spio.clear_object_asset'
    clear = True


def register():
    bpy.utils.register_class(SPIO_OT_mark_object_asset)
    bpy.utils.register_class(SPIO_OT_clear_object_asset)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_mark_object_asset)
    bpy.utils.unregister_class(SPIO_OT_clear_object_asset)
