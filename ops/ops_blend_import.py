import bpy
import subprocess
import os

from bpy.props import StringProperty, BoolProperty, EnumProperty


class blenderFileDefault:
    bl_label = 'blenderFileDefault'
    bl_options = {'UNDO_GROUPED'}

    filepath: StringProperty()
    sub_path: StringProperty()

    # batch mode
    load_all: BoolProperty(default=False)
    data_type: StringProperty()

    # link
    link = False

    def load_batch(self):
        with bpy.data.libraries.load(self.filepath, link=self.link) as (data_from, data_to):
            if self.data_type in {'materials', 'worlds'}:
                setattr(data_to, self.data_type, getattr(data_from, self.data_type))

            elif self.data_type == 'collections':
                data_to.collections = [name for name in data_from.collections]

            elif self.data_type == 'objects':
                data_to.objects = [name for name in data_from.objects]

        for coll in data_to.collections:
            bpy.context.scene.collection.children.link(coll)

        for obj in data_to.objects:
            bpy.context.collection.objects.link(obj)

    def load_with_ui(self):
        if self.link:
            bpy.ops.wm.link('INVOKE_DEFAULT',
                            filepath=self.filepath if self.sub_path == '' else os.path.join(self.filepath,
                                                                                            self.sub_path))
        else:
            bpy.ops.wm.append('INVOKE_DEFAULT',
                              filepath=self.filepath if self.sub_path == '' else os.path.join(self.filepath,
                                                                                              self.sub_path))

    def invoke(self, context, event):
        self.load_all = True if event.alt or self.load_all else False
        # self.link = event.shift
        return self.execute(context)

    def execute(self, context):
        # seem need to return set for invoke
        if not self.load_all:
            self.load_with_ui()
            return {'FINISHED'}
        else:
            self.load_batch()
            self.report({"INFO"}, f'Load all {self.data_type} from {self.filepath}')
            return {'FINISHED'}



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
    """Batch import all from all files"""
    bl_idname = 'wm.spio_batch_import_blend'
    bl_label = 'Batch Import'

    # action
    action: EnumProperty(items=[
        ('LINK', 'Link', ''),
        ('APPEND', 'Append', ''),
        ('OPEN', 'Open Extra', ''),
    ])
    # filepath join with $$
    files: StringProperty()

    # property to pass in to single blend file loader
    sub_path: StringProperty()
    load_all: BoolProperty(default=True)
    data_type: StringProperty()

    def execute(self, context):
        for filepath in self.files.split('$$'):
            if self.action == 'LINK':
                bpy.ops.wm.spio_link_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)
            elif self.action == 'APPEND':
                bpy.ops.wm.spio_append_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)
            elif self.action == 'OPEN':
                bpy.ops.wm.spio_open_blend_extra(filepath=filepath)

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
