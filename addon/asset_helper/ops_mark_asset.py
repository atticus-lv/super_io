import os.path

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty
from bpy.types import PropertyGroup

mark_list = []


def redraw_window():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def update_mark_list(self, context):
    global mark_list
    mark_list.clear()
    self.match_obj_list.clear()

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

    for obj in mark_list:
        item = self.match_obj_list.add()
        item.name = obj.name

        if isinstance(obj, bpy.types.Object):
            item.icon = 'OBJECT_DATA'
        elif isinstance(obj, bpy.types.Material):
            item.icon = 'MATERIAL'
        elif isinstance(obj, bpy.types.World):
            item.icon = 'WORLD'

    redraw_window()


class ObjectProps(bpy.types.PropertyGroup):
    name: StringProperty(name="Name", default="")
    mark: BoolProperty(name="Mark", default=True)
    icon: StringProperty(name="Icon", default="OBJECT_DATA")


class SPIO_OT_mark_helper(bpy.types.Operator):
    """Mark Helper"""
    bl_label = 'Mark Helper'
    bl_idname = 'spio.mark_helper'
    bl_options = {'UNDO_GROUPED'}

    clear: BoolProperty(name="Clear Asset", default=False)

    action: EnumProperty(name='Type', items=[
        ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
        ('MATERIAL', 'Material', '', 'MATERIAL', 1),
        ('ALL', 'Separate', '', 'MATSHADERBALL', 2),
        ('WORLD', 'World', '', 'WORLD', 4),
    ], update=update_mark_list)

    match_obj_list: CollectionProperty(type=ObjectProps)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'action')
        layout.prop(self, 'clear', toggle=False)

        if self.action == 'OBJECT':
            layout.label(text='Selected objects', icon='INFO')
        elif self.action == 'MATERIAL':
            layout.label(text="Selected materials (Exclude objects)", icon='INFO')
        elif self.action == 'ALL':
            layout.label(text='Objects and materials separately', icon='INFO')
        elif self.action == 'WORLD':
            layout.label(text='Selected worlds', icon='INFO')

        col = layout.box().column(align=True)
        col.alert = self.clear

        if len(mark_list) == 0:
            col.label(text='None')

        for item in self.match_obj_list:
            row = col.row(align=True)
            row.label(text=item.name, icon=item.icon)
            row.prop(item, 'mark', text='')

    def invoke(self, context, event):
        update_mark_list(self, context)
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        for item in self.match_obj_list:
            if not item.mark: continue
            if item.icon == 'OBJECT_DATA':
                obj = bpy.data.objects[item.name]
            elif item.icon == 'MATERIAL':
                obj = bpy.data.materials[item.name]
            elif item.icon == 'WORLD':
                obj = bpy.data.worlds[item.name]

            if not self.clear:
                obj.asset_mark()
                obj.asset_generate_preview()
            else:
                obj.asset_clear()

        redraw_window()

        return {"FINISHED"}


class SPIO_OT_mark_node_group_as_asset(bpy.types.Operator):
    bl_label = 'Mark Node Group as Asset'
    bl_idname = 'spio.mark_node_group_as_asset'
    bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(self, context):
        return (context.space_data.type == 'NODE_EDITOR' and
                context.space_data.edit_tree and
                context.active_node and
                context.active_node.type == 'GROUP')

    def execute(self, context):
        node = context.active_node
        node.node_tree.asset_mark()
        self.report({'INFO'}, f'Marked {node.node_tree.name} as asset')
        redraw_window()

        return {'FINISHED'}


class SPIO_OT_mark_edit_tree_as_asset(bpy.types.Operator):
    bl_label = 'Mark Edit Tree as Asset'
    bl_idname = 'spio.mark_edit_tree_as_asset'
    bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(self, context):
        return (context.space_data.type == 'NODE_EDITOR' and
                context.space_data.edit_tree and
                context.area.ui_type == 'GeometryNodeTree')

    def execute(self, context):
        tree = context.space_data.edit_tree
        tree.asset_mark()

        self.report({'INFO'}, f'Marked {tree.name} as asset')
        redraw_window()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ObjectProps)
    bpy.utils.register_class(SPIO_OT_mark_helper)
    bpy.utils.register_class(SPIO_OT_mark_node_group_as_asset)
    bpy.utils.register_class(SPIO_OT_mark_edit_tree_as_asset)


def unregister():
    bpy.utils.unregister_class(ObjectProps)
    bpy.utils.unregister_class(SPIO_OT_mark_helper)
    bpy.utils.unregister_class(SPIO_OT_mark_node_group_as_asset)
    bpy.utils.unregister_class(SPIO_OT_mark_edit_tree_as_asset)
