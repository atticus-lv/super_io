import bpy
import os


class SPIO_OT_copy_c4d_plugin(bpy.types.Operator):
    bl_idname = 'spio.copy_c4d_plugin'
    bl_label = 'Get Cinema 4d Plugin'

    def execute(self, context):
        cur_dir = os.path.split(os.path.realpath(__file__))[0]
        plug_f = [file for file in os.listdir(cur_dir) if file.startswith('SPIO for Cinema 4d')][0]
        full_path = os.path.join(cur_dir, plug_f)

        from ..clipboard.windows import PowerShellClipboard as Clipboard
        clipboard = Clipboard()
        clipboard.push_to_clipboard([full_path])

        self.report({'INFO'}, 'C4d Plugin has been copied to clipboard!')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_copy_c4d_plugin)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_copy_c4d_plugin)


for file in os.listdir(os.getcwd()):
    print(file)
