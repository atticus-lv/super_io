import bpy
# from .pyassimp import load, release # 相对包路径
from pyassimp import load, release
from bpy.props import StringProperty

from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image


class SPIO_OT_PureImport(bpy.types.Operator):
    """Use pyassimp to import obj"""

    bl_idname = "import_scene.spio_pure_import"
    bl_label = "Pure import(WIP)"
    bl_options = {"REGISTER", "UNDO"}

    filepath: StringProperty()

    def execute(self, context):
        scene = load(self.filepath)
        if len(scene.meshes) == 0: return {"CANCELLED"}

        for mesh in scene.meshes[0]:
            mesh_data = bpy.data.meshes.new('mesh_data')
            mesh_data.from_pydata(mesh.vertices.tolist(), [], mesh.faces.tolist())
            obj = bpy.data.objects.new('new_object', mesh_data)
            context.collection.objects.link(obj)

        release(scene)

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_PureImport)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_PureImport)
