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

    def restore(self):
        """restore value for the next popup"""
        self.filepath = ''
        self.sub_path = ''
        self.load_all = False
        self.data_type = ''

    def load_batch(self):
        with bpy.data.libraries.load(self.filepath, link=self.link) as (data_from, data_to):
            if self.data_type in {'materials', 'worlds', 'node_groups'}:
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
        self.load_all = True if event.alt or self.load_all is True else False
        # self.link = event.shift
        return self.execute(context)

    def execute(self, context):
        # seem need to return set for invoke
        if not self.load_all:
            self.load_with_ui()

            self.restore()
            return {'FINISHED'}
        else:
            self.load_batch()
            self.report({"INFO"}, f'Load all {self.data_type} from {self.filepath}')

            self.restore()
            return {'FINISHED'}


class SPIO_OT_append_blend(blenderFileDefault, bpy.types.Operator):
    """Append files for clipboard blend file\nAlt to append all data of chosen type"""

    bl_idname = 'spio.append_blend'
    bl_label = 'Append...'

    link = False


class SPIO_OT_link_blend(blenderFileDefault, bpy.types.Operator):
    """Link files for clipboard blend file\nAlt to link all data of chosen type"""

    bl_idname = 'spio.link_blend'
    bl_label = 'Link...'

    link = True


class load_and_assign:
    bl_options = {'UNDO_GROUPED'}

    filepath: StringProperty()
    link = False

    world = None
    material = None  # material that import
    object = None  # object to assign target, detect by raycast

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D" and context.active_object


class SPIO_OT_load_and_assign_material(load_and_assign, bpy.types.Operator):
    """Import material from a single file and assign it to active object"""

    bl_idname = 'spio.load_and_assign_material'
    bl_label = 'Import and Assign Material '

    def execute(self, context):
        self.object = context.active_object
        # append material
        with bpy.data.libraries.load(self.filepath, link=self.link) as (data_from, data_to):
            data_to.materials = [name for name in data_from.materials]

        if len(data_to.materials) == 0:
            self.report({"ERROR"}, f'No material in this blend file')
            return {"CANCELLED"}

        self.material = [mat for mat in data_to.materials if mat.is_grease_pencil is False][0]
        self.object.active_material = self.material
        return {'FINISHED'}


class SPIO_OT_load_and_assign_world(load_and_assign, bpy.types.Operator):
    """Import material from a single file and assign it to active object"""

    bl_idname = 'spio.load_and_assign_world'
    bl_label = 'Import and Assign World '

    def execute(self, context):
        # append material
        with bpy.data.libraries.load(self.filepath, link=self.link) as (data_from, data_to):
            data_to.worlds = [name for name in data_from.worlds]

        if len(data_to.worlds) == 0:
            self.report({"ERROR"}, f'No world in this blend file')
            return {"CANCELLED"}

        context.scene.world = data_to.worlds[0]
        return {'FINISHED'}


class SPIO_OT_batch_import_blend(bpy.types.Operator):
    """Batch import all from all files"""
    bl_idname = 'spio.batch_import_blend'
    bl_label = 'Batch Import'

    # action
    action: EnumProperty(items=[
        ('LINK', 'Link', ''),
        ('APPEND', 'Append', ''),
        ('OPEN', 'Open Extra', ''),
    ])
    # filepath join with $$
    files: StringProperty()

    # property to pass in to single blend file importer
    sub_path: StringProperty()
    load_all: BoolProperty(default=True)
    data_type: StringProperty()

    def execute(self, context):
        for filepath in self.files.split('$$'):
            if self.action == 'LINK':
                bpy.ops.spio.link_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)
            elif self.action == 'APPEND':
                bpy.ops.spio.append_blend(filepath=filepath, data_type=self.data_type, load_all=self.load_all)
            elif self.action == 'OPEN':
                bpy.ops.spio.open_blend_extra(filepath=filepath)

        return {'FINISHED'}


class SPIO_OT_open_blend(blenderFileDefault, bpy.types.Operator):
    """Open file with current blender"""
    bl_idname = 'spio.open_blend'
    bl_label = 'Open...'

    def execute(self, context):
        bpy.ops.wm.open_mainfile(filepath=self.filepath)
        return {"FINISHED"}


class SPIO_OT_open_blend_extra(blenderFileDefault, bpy.types.Operator):
    """Open file with another blender"""
    bl_idname = 'spio.open_blend_extra'
    bl_label = 'Open'

    def execute(self, context):
        subprocess.Popen([bpy.app.binary_path, self.filepath])
        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_append_blend)
    bpy.utils.register_class(SPIO_OT_link_blend)
    bpy.utils.register_class(SPIO_OT_batch_import_blend)

    bpy.utils.register_class(SPIO_OT_open_blend)
    bpy.utils.register_class(SPIO_OT_open_blend_extra)

    bpy.utils.register_class(SPIO_OT_load_and_assign_material)
    bpy.utils.register_class(SPIO_OT_load_and_assign_world)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_append_blend)
    bpy.utils.unregister_class(SPIO_OT_link_blend)
    bpy.utils.unregister_class(SPIO_OT_batch_import_blend)

    bpy.utils.unregister_class(SPIO_OT_open_blend_extra)
    bpy.utils.unregister_class(SPIO_OT_open_blend)

    bpy.utils.unregister_class(SPIO_OT_load_and_assign_material)
    bpy.utils.unregister_class(SPIO_OT_load_and_assign_world)
