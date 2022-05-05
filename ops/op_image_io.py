import bpy
import os
import sys
import math
from bpy.props import StringProperty, BoolProperty, EnumProperty


class SPIO_OT_import_image(bpy.types.Operator):
    """Import all image as reference/plane/nodes/world/light
Alt Click to mark asset(world and light)"""

    bl_idname = 'spio.import_image'
    bl_label = 'Import Image'
    bl_options = {'UNDO_GROUPED'}

    files: StringProperty()  # list of filepath, join with$$
    action: EnumProperty(items=[
        ('REF', 'Reference', ''),
        ('PLANE', 'PLANE', ''),
        ('NODES', 'NodeTree', ''),
        ('PBR_SETUP', 'PBR Set Up', ''),
        ('WORLD', 'World', ''),
        ('GOBOS', 'Light Gobos', ''),
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
        elif context.area.type == 'FILE_BROWSER':
            return context.area.ui_type == 'ASSETS'

    def load_image_by_path(self, path):
        src_images = list(bpy.data.images)

        # use built-in ops instead of bpy.data.images.load to detect sequence and UDIM
        bpy.ops.image.open(filepath=path)
        # if image already load in, reload it
        images = [img for img in bpy.data.images if img not in src_images] + [
            bpy.data.images.get(os.path.basename(path))]

        image = images[0]

        return image

    def invoke(self, context, event):
        if self.action == 'NODES':
            location_X, location_Y = context.space_data.cursor_location

        if self.action == 'PBR_SETUP':
            # from addon_utils import enable
            # enable('node_wrangler')

            filepaths = self.files.split('$$')
            dir = os.path.dirname(filepaths[0]) + '\\'
            files = [{"name": os.path.basename(filepath)} for filepath in
                     filepaths]

            # print(filepaths[0])
            # print(dir)
            # print(files)

            bpy.ops.node.nw_add_textures_for_principled(
                filepath=filepaths[0],
                directory=dir,
                files=files,
                relative_path=True)

            return {'FINISHED'}

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
                node_group_file = os.path.join(cur_dir, 'templates', "World.blend")

                img = self.load_image_by_path(filepath)

                with bpy.data.libraries.load(node_group_file, link=False) as (data_from, data_to):
                    setattr(data_to, 'worlds', getattr(data_from, 'worlds'))

                world = data_to.worlds[0]
                base, sep, ext = img.name.rpartition('.')
                world.name = base

                for node in world.node_tree.nodes:
                    if node.name == 'Environment Texture':
                        node.image = img

                if event.alt:
                    world.asset_mark()

            # Light Gobos
            elif self.action == 'GOBOS':
                img = self.load_image_by_path(filepath)

                bpy.ops.object.light_add(type='AREA')
                light = context.object
                light.name = ".".join(os.path.basename(filepath).split('.')[:-1])  # get file name without extension

                d = light.data
                d.shadow_soft_size = 1  # set a small shadow soft size to get clear shapes
                d.use_nodes = True
                d.spread = math.radians(2)  # 2 degrees spread angle
                nt = d.node_tree

                # create nodes
                n_emi = nt.nodes['Emission']

                n_img = nt.nodes.new('ShaderNodeTexImage')
                n_img.location = -200, 300
                n_img.image = img

                n_geo = nt.nodes.new('ShaderNodeNewGeometry')
                n_geo.location = -400, 300

                # create links
                nt.links.new(n_geo.outputs[5], n_img.inputs[0])
                nt.links.new(n_img.outputs[0], n_emi.inputs[1])

                if event.alt:
                    light.asset_mark()
                    override = context.copy()
                    override['id'] = light
                    bpy.ops.ed.lib_id_load_custom_preview(override, filepath=filepath)

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
