import bpy
import os
from bpy.props import EnumProperty
from ..ui.icon_utils import RSN_Preview


class SPIO_OT_copy_c4d_plugin(bpy.types.Operator):
    bl_idname = 'spio.copy_c4d_plugin'
    bl_label = 'Get Cinema 4d Plugin'

    def execute(self, context):
        file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", 'third_party_addons', 'Super IO for Cinema 4d'))
        full_path = os.path.abspath(file)

        bpy.ops.wm.path_open(filepath=full_path)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout.box()
        layout.label(text='This is a plugin suitable for c4d R23+')
        layout.label(text="Copy the plugin folder under c4d's /plugins/")
        layout.label(text='You can find it in extension menu')
        layout.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'tutorial')


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """Copy to clipboard
复制到剪切板"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Get Houdini Script'

    file: EnumProperty(name='Script', items=[
        ('houdini_spio_import.py', 'Import (Shelf Tool)', ''),
        ('houdini_spio_export.py', 'Export (Shelf Tool)', ''),
        ('houdini_spio_export_radius.py', 'Export (Radial Menu)', ''),
    ])

    def execute(self, context):
        with open(os.path.join(os.path.dirname(__file__), '..', 'third_party_addons', 'houdini', self.file), 'r') as f:
            text = f.read()
            if self.file in bpy.data.texts: bpy.data.texts.remove(bpy.data.texts[self.file])

            t = bpy.data.texts.new(name=self.file)
            t.write(text)

        bpy.ops.spio.pop_editor(editor_text=self.file)

        self.report({'INFO'}, 'Houdini tool shelf file has been copied to clipboard!')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout.box()
        layout.prop(self, 'file')

        layout.label(text='This is a script suitable for houdini 18+(python3)')
        layout.label(text='You can find the icon in the folder and assign it at the shelf tool')
        layout.label(text='You can copy the shelf tool script and assign the script to a new shelf tool')
        layout.label(text='Then assign Shortcut for it')
        layout.operator('wm.path_open', text='Install Tutorial', icon='QUESTION').filepath = os.path.join(
            os.path.dirname(__file__),
            '..', 'third_party_addons',
            'tutorial')


def register():
    bpy.utils.register_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.register_class(SPIO_OT_copy_houdini_script)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.unregister_class(SPIO_OT_copy_houdini_script)
