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
        # return target data type for post process
        return getattr(data_to, self.data_type)

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


from .utils import viewlayer_fix_291
from bpy_extras import view3d_utils


class SPIO_OT_load_and_assign_material(blenderFileDefault, bpy.types.Operator):
    """Import material from a single file and assign it to the mouse position object"""

    link: BoolProperty(default=False)

    material = None  # material that import
    target_obj = None  # object to assign target, detect by raycast

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"

    def invoke(self, context, event):
        # define
        self.load_all = True
        self.data_type = 'materials'

        self.target_obj = self.ray_cast(context, event)
        if not self.target_obj:
            self.report({"INFO"}, f'No Object on mouse position')
            return {"CANCELLED"}
        return self.execute(context)

    def execute(self, context):
        # append material
        materials = self.load_batch()
        if len(materials) == 0:
            self.report({"INFO"}, f'No material in this blend file')
            return {"CANCELLED"}
        # TODO popup menu for multiple material file
        self.material = materials[0]
        if self.target_obj.type == "MESH":
            self.target_obj.active_material = self.material
        elif hasattr(object, 'modifiers'):
            # TODO: Check that if the geo modifier obj can be detect by obj. If so, set set material modifier to it
            pass

        return {'FINISHED'}

    def ray_cast(self, context, event):
        # Get the mouse position
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y
        # Contextual active object, 2D and 3D regions
        scene = context.scene
        region = context.region
        region3D = context.space_data.region_3d

        viewlayer = viewlayer_fix_291(self, context)

        # The direction indicated by the mouse position from the current view
        self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
        # The view point of the user
        self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
        # The 3D location in this direction
        self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)

        result, self.loc, normal, index, hit_object, matrix = scene.ray_cast(viewlayer, self.view_point, self.view_vector)

        if result:
            for obj in context.selected_objects:
                obj.select_set(False)
            # dg = context.evaluated_depsgraph_get()
            # eval_obj = dg.id_eval_get(object)

            # set active
            context.view_layer.objects.active = hit_object.original

            return object


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

    # property to pass in to single blend file loader
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


def unregister():
    bpy.utils.unregister_class(SPIO_OT_append_blend)
    bpy.utils.unregister_class(SPIO_OT_link_blend)
    bpy.utils.unregister_class(SPIO_OT_batch_import_blend)

    bpy.utils.unregister_class(SPIO_OT_open_blend_extra)
    bpy.utils.unregister_class(SPIO_OT_open_blend)

    bpy.utils.unregister_class(SPIO_OT_load_and_assign_material)
