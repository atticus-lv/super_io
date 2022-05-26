import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty


class selected_assets:
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_asset_files') and context.selected_asset_files

    def get_local_selected_assets(self, context):
        current_library_name = context.area.spaces.active.params.asset_library_ref
        match_obj = [asset_file.local_id for asset_file in context.selected_asset_files if
                     current_library_name == "LOCAL"]

        return match_obj


class SPIO_OT_clear_selected_assets(selected_assets, bpy.types.Operator):
    bl_idname = "spio.clear_selected_assets"
    bl_label = "Clear Selected Assets"

    set_fake_user: BoolProperty(name='Set Fake User', default=False)

    def execute(self, context):
        match_obj = self.get_local_selected_assets(context)
        for obj in match_obj:
            obj.asset_clear()
            if self.set_fake_user:
                obj.use_fake_user = True

        return {'FINISHED'}


class SPIO_OT_add_tag_to_selected_assets(selected_assets, bpy.types.Operator):
    bl_idname = "spio.add_tag_to_selected_assets"
    bl_label = "Add Tag to Selected Assets"

    tag: StringProperty(name="Tag", default="tag")

    def execute(self, context):
        match_obj = self.get_local_selected_assets(context)

        for obj in match_obj:
            obj.asset_data.tags.new(self.tag)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SPIO_OT_add_author_to_selected_assets(selected_assets, bpy.types.Operator):
    bl_idname = "spio.add_author_to_selected_assets"
    bl_label = "Add Author to Selected Assets"

    author: StringProperty(name="Author", default="author")

    def execute(self, context):
        match_obj = self.get_local_selected_assets(context)

        for obj in match_obj:
            obj.asset_data.author = self.author

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SPIO_OT_remove_tag_from_selected_assets(selected_assets, bpy.types.Operator):
    bl_idname = "spio.remove_tag_from_selected_assets"
    bl_label = "Remove Tag from Selected Assets"
    bl_options = {'REGISTER', 'UNDO'}

    tag: StringProperty(name="Tag", default="tag")

    def execute(self, context):
        match_obj = self.get_local_selected_assets(context)

        for obj in match_obj:
            if self.tag in obj.asset_data.tags:
                tag = obj.asset_data.tags[self.tag]
                obj.asset_data.tags.remove(tag)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


def draw_context_menu_prepend(self, context):
    from ...preferences.prefs import get_pref
    if get_pref().asset_helper and bpy.app.version >= (3, 0, 0):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator(SPIO_OT_add_author_to_selected_assets.bl_idname, icon='OUTLINER_OB_FONT')
        layout.separator()

        layout.operator(SPIO_OT_add_tag_to_selected_assets.bl_idname, icon='BOOKMARKS')
        layout.operator(SPIO_OT_remove_tag_from_selected_assets.bl_idname, icon='REMOVE')

        layout.separator()

        op = layout.operator(SPIO_OT_clear_selected_assets.bl_idname, icon='X')
        op.set_fake_user = False
        op = layout.operator(SPIO_OT_clear_selected_assets.bl_idname,
                             text='Clear Selected Assets (Set Fake User)', icon='FAKE_USER_ON')
        op.set_fake_user = True

        layout.separator()


def register():
    bpy.utils.register_class(SPIO_OT_clear_selected_assets)
    bpy.utils.register_class(SPIO_OT_add_tag_to_selected_assets)
    bpy.utils.register_class(SPIO_OT_remove_tag_from_selected_assets)
    bpy.utils.register_class(SPIO_OT_add_author_to_selected_assets)
    if bpy.app.version >= (3, 0, 0):
        bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu_prepend)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_clear_selected_assets)
    bpy.utils.unregister_class(SPIO_OT_add_tag_to_selected_assets)
    bpy.utils.unregister_class(SPIO_OT_remove_tag_from_selected_assets)
    bpy.utils.unregister_class(SPIO_OT_add_author_to_selected_assets)
    if bpy.app.version >= (3, 0, 0):
        bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu_prepend)
