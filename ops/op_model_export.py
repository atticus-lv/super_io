import bpy
import os
import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty

from .ops_super_import import import_icon
from ..clipboard.windows import PowerShellClipboard
from ..exporter.default_exporter import default_exporter


class ModeCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform == "win32":
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_object is not None
                    and context.active_object.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )


class SPIO_OT_export_model(ModeCopyDefault, bpy.types.Operator):
    """Export Selected obj as model file"""
    bl_idname = 'spio.export_model'
    bl_label = 'Copy Model'

    extension: StringProperty()

    def execute(self, context):
        if self.extension not in default_exporter: return {"CANCELLED"}
        # win temp file
        ori_dir = context.preferences.filepaths.temporary_directory
        temp_dir = ori_dir
        if ori_dir == '':
            temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')

        bl_idname = default_exporter.get(self.extension)
        op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

        # export with args
        filepath = os.path.join(temp_dir, context.active_object.name + f'.{self.extension}')
        op_args = {'filepath': filepath,
                   'use_selection': True}

        op_callable(**op_args)

        clipboard = PowerShellClipboard()
        clipboard.push_to_clipboard(path=filepath)

        self.report({'INFO'}, f'{context.active_object.name}.{self.extension} has been copied to Clipboard')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_model)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_model)
