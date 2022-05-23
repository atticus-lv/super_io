import bpy
from . import op_import_ies, op_import_zip, ops_addon_import, op_blend_import_and_assign

classes = (
    op_import_ies,
    op_import_zip,
    ops_addon_import,
    op_blend_import_and_assign,

)


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in classes:
        cls.unregister()
