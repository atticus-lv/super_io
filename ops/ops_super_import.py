import bpy

from ..clipboard.windows import WindowsClipboard as Clipboard
from .utils import get_config
from mathutils import Vector


class VIEW3D_OT_SuperImport(bpy.types.Operator):
    """Paste Model/Images"""

    bl_idname = "view3d.spio_import"
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        clipboard = Clipboard.push()
        config = get_config(check_use=True)

        for file in clipboard.file_urls:
            # custom operator
            ext = file.filepath.split('.')[-1].lower()

            if ext in config:
                ops_config = config[ext]
                bl_idname = ops_config.pop('bl_idname')
                ops_config['filepath'] = file.filepath
                try:
                    exec(f'bpy.ops.{bl_idname}(**{ops_config})')
                except Exception as e:
                    self.report({"ERROR"}, str(e))

            # default setting
            elif ext == 'stl':
                bpy.ops.import_mesh.stl(filepath=file.filepath)
            elif ext == 'dae':
                bpy.ops.wm.collada_import(filepath=file.filepath)
            elif ext == 'abc':
                bpy.ops.wm.alembic_import(filepath=file.filepath)
            elif ext == 'obj':
                bpy.ops.import_scene.obj(filepath=file.filepath)
            elif ext == 'fbx':
                bpy.ops.import_scene.fbx(filepath=file.filepath)
            elif ext in {'glb', 'gltf'}:
                bpy.ops.import_scene.gltf(filepath=file.filepath)
            elif ext in {'x3d', 'wrl'}:
                bpy.ops.import_scene.x3d(filepath=file.filepath)
            elif ext == 'svg':
                bpy.ops.import_curve.svg(filepath=file.filepath)
            else:
                bpy.ops.object.load_reference_image(filepath=file.filepath)

        return {"FINISHED"}

    @classmethod
    def poll(_cls, context):
        return (
                context.area.type == "VIEW_3D"
                and context.area.ui_type == "VIEW_3D"
                and context.mode == "OBJECT"
        )


def register():
    bpy.utils.register_class(VIEW3D_OT_SuperImport)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_SuperImport)
