import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty


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


def register():
    bpy.utils.register_class(SPIO_OT_load_and_assign_material)
    bpy.utils.register_class(SPIO_OT_load_and_assign_world)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_load_and_assign_material)
    bpy.utils.unregister_class(SPIO_OT_load_and_assign_world)
