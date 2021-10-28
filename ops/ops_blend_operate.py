import bpy
import subprocess

import json

from bpy.props import StringProperty, BoolProperty
from ..loader.default_blend import blenderFileDefault


class SPIO_OT_AppendBlend(blenderFileDefault, bpy.types.Operator):
    """Append files for clipboard blend file
Alt to append all data of the type"""
    bl_idname = 'wm.spio_append_blend'
    bl_label = 'Append...'

    link = False


class SPIO_OT_LinkBlend(blenderFileDefault, bpy.types.Operator):
    """Link files for clipboard blend file
Alt to link all data of the type"""
    bl_idname = 'wm.spio_link_blend'
    bl_label = 'Link...'

    link = True


class SPIO_OT_BatchImportBlend(bpy.types.Operator):
    bl_idname = 'wm.spio_batch_import_blend'
    bl_label = 'Batch Import'

    link: BoolProperty()
    # filepath join with $$
    files: StringProperty()

    # property to pass in to single blend file loader
    sub_path: StringProperty()
    load_all: BoolProperty(default=True)
    data_type: StringProperty()

    def execute(self, context):
        for filepath in self.files.split('$$'):
            if self.link:
                bpy.ops.wm.spio_link_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)
            else:
                bpy.ops.wm.spio_append_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)

        return {'FINISHED'}


class SPIO_OT_OpenBlend(blenderFileDefault, bpy.types.Operator):
    """Open file with current blender"""
    bl_idname = 'wm.spio_open_blend'
    bl_label = 'Open...'

    def execute(self, context):
        bpy.ops.wm.open_mainfile(filepath=self.filepath)
        return {"FINISHED"}


class SPIO_OT_OpenBlendExtra(blenderFileDefault, bpy.types.Operator):
    """Open file with another blender"""
    bl_idname = 'wm.spio_open_blend_extra'
    bl_label = 'Open'

    def execute(self, context):
        subprocess.Popen([bpy.app.binary_path, self.filepath])
        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_AppendBlend)
    bpy.utils.register_class(SPIO_OT_LinkBlend)
    bpy.utils.register_class(SPIO_OT_BatchImportBlend)

    bpy.utils.register_class(SPIO_OT_OpenBlend)
    bpy.utils.register_class(SPIO_OT_OpenBlendExtra)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_AppendBlend)
    bpy.utils.unregister_class(SPIO_OT_LinkBlend)
    bpy.utils.unregister_class(SPIO_OT_BatchImportBlend)

    bpy.utils.unregister_class(SPIO_OT_OpenBlendExtra)
    bpy.utils.unregister_class(SPIO_OT_OpenBlend)
