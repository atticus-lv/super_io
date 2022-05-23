import bpy
from . import (op_blend_export, op_node_export, op_model_export, op_model_import, ops_super_export, ops_super_import,
               ops_blend_import, ops_config_io, op_image_io, op_get_plugin, op_read_preset)

classes = (
    op_blend_export,
    op_node_export,
    op_model_export,
    op_model_import,
    ops_super_export,
    ops_super_import,
    ops_blend_import,
    ops_config_io,
    op_image_io,
    op_get_plugin,
    op_read_preset

)


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in classes:
        cls.unregister()
