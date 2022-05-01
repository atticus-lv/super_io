import bpy
import os
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty


class SPIO_OT_import_image(bpy.types.Operator):
    """Import all image as reference/plane/nodes/world"""

    bl_idname = 'spio.import_image'
    bl_label = 'Import Image'

    files: StringProperty()  # list of filepath, join with$$
    action: EnumProperty(items=[
        ('REF', 'Reference', ''),
        ('PLANE', 'PLANE', ''),
        ('NODES', 'NodeTree', ''),
        ('WORLD', 'World', ''),
    ])

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return (
                    context.area.ui_type == "VIEW_3D"
                    and context.mode == "OBJECT")

        elif context.area.type == "NODE_EDITOR":
            return (
                    context.area.type == "NODE_EDITOR"
                    and context.area.ui_type in {'GeometryNodeTree', "ShaderNodeTree", 'CompositorNodeTree'}
                    and context.space_data.edit_tree is not None
            )

    def load_image_by_path(self, path):
        src_images = list(bpy.data.images)

        # use built-in ops instead of bpy.data.images.load to detect sequence and UDIM
        bpy.ops.image.open(filepath=path)
        # if image already load in, reload it
        images = [img for img in bpy.data.images if img not in src_images] + [
            bpy.data.images.get(os.path.basename(path))]

        image = images[0]

        return image

    def execute(self, context):
        if self.action == 'NODES':
            location_X, location_Y = context.space_data.cursor_location

        for filepath in self.files.split('$$'):
            ### Plane
            if self.action == 'PLANE':
                bpy.ops.import_image.to_plane(files=[{"name": filepath}])

            ### References Empty
            elif self.action == 'REF':
                bpy.ops.object.load_reference_image(filepath=filepath)

            ### Nodes
            elif self.action == 'NODES':
                image = self.load_image_by_path(filepath)

                bpy.ops.node.select_all(action='DESELECT')
                nt = context.space_data.edit_tree

                if context.area.ui_type == 'ShaderNodeTree':
                    if context.space_data.shader_type == 'WORLD':
                        node_type = 'ShaderNodeTexEnvironment'
                    else:
                        node_type = 'ShaderNodeTexImage'
                elif context.area.ui_type == 'GeometryNodeTree':
                    node_type = 'GeometryNodeImageTexture'
                elif context.area.ui_type == 'CompositorNodeTree':
                    node_type = 'CompositorNodeImage'

                tex_node = nt.nodes.new(node_type)
                tex_node.location = location_X, location_Y

                location_Y -= 50
                location_X += 25

                tex_node.select = True
                nt.nodes.active = tex_node

                if node_type in {'ShaderNodeTexImage', 'ShaderNodeTexEnvironment', 'CompositorNodeImage'}:
                    tex_node.image = image
                elif node_type == 'GeometryNodeImageTexture':
                    tex_node.inputs['Image'].default_value = image

            # Worlds
            elif self.action == 'WORLD':
                # get preset node group
                cur_dir = os.path.dirname(__file__)
                addon_dir = os.path.dirname(cur_dir)
                node_group_file = os.path.join(addon_dir,'imexporter','templates', "World.blend")

                img = self.load_image_by_path(filepath)

                with bpy.data.libraries.load(node_group_file, link=False) as (data_from, data_to):
                    setattr(data_to, 'worlds', getattr(data_from, 'worlds'))

                world = data_to.worlds[0]
                world.name = img.name

                for node in world.node_tree.nodes:
                    if node.name == 'Environment Texture':
                        node.image = img

        return {'FINISHED'}


from ..clipboard.clipboard import Clipboard as Clipboard


class ImageCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform in {"darwin", "win32"}:
            return (
                    context.area.type == "IMAGE_EDITOR"
                    and context.area.spaces.active.image is not None
                    and context.area.spaces.active.image.has_data is True
            )

    attr = [
        'file_format',
        'color_mode',
        'color_depth',
        'compression',
    ]

    def set_format(self, restore=False):
        settings = bpy.context.scene.render.image_settings
        for a in self.attr:
            if restore:
                setattr(settings, a, getattr(self, a))
            else:
                setattr(self, a, getattr(settings, a))

    action = 'pixel'

    def execute(self, context):
        active_image = context.area.spaces.active.image
        image_path = os.path.join(bpy.app.tempdir, f'{active_image.name}.png')

        self.set_format()

        bpy.ops.image.save_as(filepath=image_path, save_as_render=True, copy=True)
        # push to clipboard
        clipboard = Clipboard()
        if self.action == 'pixel':
            clipboard.push_pixel_to_clipboard(path=image_path)
        else:
            clipboard.push_to_clipboard(paths=[image_path])

        self.set_format(restore=True)

        self.report({'INFO'}, f'{active_image.name} has been copied to Clipboard')

        return {'FINISHED'}


class SPIO_OT_export_pixel(ImageCopyDefault, bpy.types.Operator):
    """Export as Image Pixel"""
    bl_idname = 'spio.export_pixel'
    bl_label = 'Copy Pixel'

    action = 'pixel'


class SPIO_OT_export_image(ImageCopyDefault, bpy.types.Operator):
    """Export as Image File"""
    bl_idname = 'spio.export_image'
    bl_label = 'Copy Image'

    action = 'file'


def register():
    bpy.utils.register_class(SPIO_OT_import_image)
    bpy.utils.register_class(SPIO_OT_export_pixel)
    bpy.utils.register_class(SPIO_OT_export_image)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_image)
    bpy.utils.unregister_class(SPIO_OT_export_pixel)
    bpy.utils.unregister_class(SPIO_OT_export_image)
