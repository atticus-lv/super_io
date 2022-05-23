import bpy

from bpy.props import StringProperty
from ..imexporter.default_importer import get_importer
from ..preferences.prefs import get_pref


class SPIO_OT_import_model(bpy.types.Operator):
    """Import Model with blender's default importer"""

    bl_idname = 'spio.import_model'
    bl_label = 'Import Model'
    bl_options = {'UNDO_GROUPED'}

    files: StringProperty()  # list of filepath, join with$$

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return (
                    context.area.ui_type == "VIEW_3D"
                    and context.mode == "OBJECT")

        elif context.area.type == "NODE_EDITOR":
            return (
                    context.area.type == "NODE_EDITOR"
                    and context.area.ui_type in {'GeometryNodeTree', "ShaderNodeTree"}
                    and context.space_data.edit_tree is not None
            )

    def execute(self, context):
        importer = get_importer(cpp_obj_importer=get_pref().cpp_obj_importer)

        for filepath in self.files.split('$$'):
            ext = filepath.split('.')[-1]
            if ext in importer:
                bl_idname = importer.get(ext)
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
                op_callable(filepath=filepath)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_import_model)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_model)
