import bpy
import os
from bpy.props import EnumProperty
from ..ui.icon_utils import RSN_Preview


class SPIO_OT_copy_c4d_plugin(bpy.types.Operator):
    bl_idname = 'spio.copy_c4d_plugin'
    bl_label = 'Get Cinema 4d Plugin'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout.box()
        layout.use_property_split = True

        layout.label(text='This is a plugin suitable for c4d R23+')
        layout.label(text="Copy the plugin folder under c4d's /plugins/")
        layout.label(text='You can find it in extension menu')

        row = layout.row()

        row.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'tutorial')

        file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", 'third_party_addons', 'Super IO for Cinema 4d'))
        full_path = os.path.abspath(file)

        row.operator('wm.path_open', text='Open', icon='FILEBROWSER').filepath = full_path


class SPIO_OT_load_text(bpy.types.Operator):
    bl_idname = 'spio.load_text'
    bl_label = 'Load Text'

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        with open(self.filepath, 'r') as f:
            filename = os.path.basename(self.filepath)
            text = f.read()
            if filename in bpy.data.texts: bpy.data.texts.remove(bpy.data.texts[filename])

            t = bpy.data.texts.new(name=filename)
            t.write(text)

        bpy.ops.spio.pop_editor(editor_text=filename)

        return {'FINISHED'}


item = [
    ('houdini_spio_import', 'Import (Shelf Tool)', ''),
    ('houdini_spio_export', 'Export (Shelf Tool)', ''),
    ('houdini_spio_export_radius', 'Export (Radial Menu)', ''),
]


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """Copy to clipboard
复制到剪切板"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Get Houdini Script'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout.box()
        layout.use_property_split = True

        layout.label(text='This is a script suitable for houdini 18+(python3)')
        layout.label(text='You can find the icon in the folder and assign it at the shelf tool')
        layout.label(text='Then assign Shortcut for it')

        row = layout.row()
        col = row.column()
        col.scale_y = 3
        col.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'tutorial')

        col = row.column()
        for file, label, des in item:
            filepath = os.path.join(os.path.dirname(__file__), '..', 'third_party_addons', 'houdini', file)
            col.operator('spio.load_text', text=label, icon='FILEBROWSER').filepath = filepath


def register():
    bpy.utils.register_class(SPIO_OT_load_text)
    bpy.utils.register_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.register_class(SPIO_OT_copy_houdini_script)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_load_text)
    bpy.utils.unregister_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.unregister_class(SPIO_OT_copy_houdini_script)
