import bpy
import os
from bpy.props import EnumProperty


class SPIO_OT_copy_c4d_plugin(bpy.types.Operator):
    bl_idname = 'spio.copy_c4d_plugin'
    bl_label = 'Get Cinema 4d Plugin'

    def execute(self, context):
        file = os.path.join(os.path.dirname(__file__), "..", 'third_party_addons', 'Super IO for Cinema 4d')
        full_path = os.path.abspath(file)

        from ..clipboard.windows import PowerShellClipboard as Clipboard
        clipboard = Clipboard()
        clipboard.push_to_clipboard([full_path])

        self.report({'INFO'}, 'C4d Plugin has been copied to clipboard!')

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self,width = 500)

    def draw(self, context):
        layout = self.layout.box()
        layout.label(text='This is a plugin suitable for c4d R23+')
        layout.label(text='After clicking confirm, the plugin folder will be copied to the clipboard for pasting')
        layout.label(text='Paste it under c4d plugins folder')
        layout.label(text='You can find it in extension menu')


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """Copy to clipboard
复制到剪切板"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Get Houdini Script'

    file: EnumProperty(name='Script', items=[
        ('houdini_spio_import.py', 'Import', ''),
        ('houdini_spio_export.py', 'Export', ''),
    ])

    def execute(self, context):
        file = os.path.join(os.path.dirname(__file__), "..", 'third_party_addons', 'Super IO for Houdini')

        from ..clipboard.windows import PowerShellClipboard as Clipboard
        clipboard = Clipboard()
        clipboard.push_to_clipboard([file])

        self.report({'INFO'}, 'Houdini tool shelf file has been copied to clipboard!')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self,width = 500)

    def draw(self, context):
        layout = self.layout.box()
        layout.label(text='This is a plugin suitable for houdini 18+(python3)')
        layout.label(text='After clicking confirm, the shelf tool folder will be copied to the clipboard for pasting')
        layout.label(text=r'Please paste it to "C:/Users/{User-Name}/Documents/houdini{version}/toolbar/"')
        layout.label(text='You can find the icon in the folder and assign it at the shelf tool')

def register():
    bpy.utils.register_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.register_class(SPIO_OT_copy_houdini_script)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_copy_c4d_plugin)
    bpy.utils.unregister_class(SPIO_OT_copy_houdini_script)
