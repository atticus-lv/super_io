import time

import bpy
import os

# from .pyassimp import load, release # 相对包路径
from pyassimp import load, release
from bpy.props import StringProperty

from ..ops.utils import MeasureTime


class SPIO_OT_PureImport(bpy.types.Operator):
    """Use pyassimp to import obj"""

    bl_idname = "import_scene.spio_pure_import"
    bl_label = "Pure import(WIP)"
    bl_options = {"REGISTER", "UNDO"}

    filepath: StringProperty()

    def execute(self, context):
        with MeasureTime() as start_time:
            scene = load(self.filepath)
            print(f'Loading cost {time.time() - start_time}s')

        if len(scene.meshes) == 0: return {"CANCELLED"}

        with MeasureTime() as start_time:
            for mesh in scene.meshes:
                mesh_data = bpy.data.meshes.new('mesh_data')
                mesh_data.from_pydata(mesh.vertices.tolist(), [], mesh.faces.tolist())
                obj = bpy.data.objects.new(os.path.basename(self.filepath), mesh_data)
                context.collection.objects.link(obj)
            print(f'Building mesh cost {time.time() - start_time}s')

        release(scene)

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_PureImport)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_PureImport)
