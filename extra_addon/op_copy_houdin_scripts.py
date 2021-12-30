import bpy
import os
from bpy.props import StringProperty


class SPIO_OT_copy_houdini_script(bpy.types.Operator):
    """Copy to clipboard
复制到剪切板"""
    bl_idname = 'spio.copy_houdini_script'
    bl_label = 'Get Houdini Script'

    def execute(self, context):
        cur_dir = os.path.split(os.path.realpath(__file__))[0]
        hou_file = os.path.join(cur_dir, 'SPIO for Houdini', 'houdini_spio_import.py')
        with open(hou_file, 'r') as f:
            data = f.readlines()
            context.window_manager.clipboard = ''.join(data)
            self.report({'INFO'}, 'Houdini Scripts has been copied to clipboard!')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_copy_houdini_script)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_copy_houdini_script)
