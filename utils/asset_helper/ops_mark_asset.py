import os.path

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty

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

    def mark_world():
        for world in bpy.data.worlds:
            mark_list.append(world)

    if self.action == 'OBJECT':
        mark_obj()
    elif self.action == 'MATERIAL':
        mark_mat()
    elif self.action == 'ALL':
        mark_obj()
        mark_mat()
    elif self.action == 'WORLD':
        mark_world()

    redraw_window()

    return mark_list


class object_asset(bpy.types.Operator):
    bl_options = {'UNDO_GROUPED'}

    clear = False

    action: EnumProperty(name='Type', items=[
        ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
        ('MATERIAL', 'Material', '', 'MATERIAL', 1),
        ('ALL', 'Separate', '', 'MATSHADERBALL', 2),
        ('WORLD', 'World', '', 'WORLD', 4),
    ], update=update_mark_list)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, 'action', expand=True)

        if self.action == 'OBJECT':
            layout.label(text='Selected objects', icon='INFO')
        elif self.action == 'MATERIAL':
            layout.label(text="Selected materials (Exclude objects)", icon='INFO')
        elif self.action == 'ALL':
            layout.label(text='Objects and materials separately', icon='INFO')
        elif self.action == 'WORLD':
            layout.label(text='All worlds', icon='INFO')

        col = layout.box().column(align=True)
        if len(mark_list) == 0:
            col.label(text='None')

        # split list every 30 items
        item_lists = []
        n = 3
        for i in range(0, len(mark_list), n):
            item_lists.append(mark_list[i:i + n])
        for item_list in item_lists:
            row1 = col.row(align=True)
            for obj in item_list:
                sub = row1.column(align=True)
                if isinstance(obj, bpy.types.Object):
                    icon = 'OBJECT_DATA'
                elif isinstance(obj, bpy.types.Material):
                    icon = 'MATERIAL'
                elif isinstance(obj, bpy.types.World):
                    icon = 'WORLD'
                else:
                    icon = 'X'

                if self.clear:
                    if obj.asset_data is None: continue
                    sub.label(text=obj.name, icon=icon)
                else:
                    sub.label(text=obj.name, icon=icon)

    def invoke(self, context, event):
        l = 600
        return context.window_manager.invoke_props_dialog(self, width=l)

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
    """Mark Helper"""
    bl_label = 'Mark as Asset'
    bl_idname = 'spio.mark_object_asset'
    clear = False


class SPIO_OT_clear_object_asset(object_asset, bpy.types.Operator):
    """Clear"""
    bl_label = 'Clear Selected Asset'
    bl_idname = 'spio.clear_object_asset'
    clear = True


def register():
    bpy.utils.register_class(SPIO_OT_mark_object_asset)
    bpy.utils.register_class(SPIO_OT_clear_object_asset)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_mark_object_asset)
    bpy.utils.unregister_class(SPIO_OT_clear_object_asset)
