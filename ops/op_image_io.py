import bpy
import os
import sys
import math
from bpy.props import StringProperty, BoolProperty, EnumProperty


class image_io:
    bl_options = {'UNDO_GROUPED'}
    files: StringProperty()  # list of filepath, join with$$

    action = None

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


class SPIO_OT_import_image_as_reference(image_io, bpy.types.Operator):
    bl_idname = "spio.import_image_as_reference"
    bl_label = "Import as Reference"

    def execute(self, context):
        for filepath in self.files.split('$$'):
            bpy.ops.object.load_reference_image(filepath=filepath)

        return {'FINISHED'}


class SPIO_OT_import_image_as_plane(image_io, bpy.types.Operator):
    bl_idname = "spio.import_image_as_plane"
    bl_label = "Import as Plane"

    def execute(self, context):
        filepaths = self.files.split('$$')
        dir = os.path.dirname(filepaths[0]) + '\\'
        files = [{"name": os.path.basename(filepath)} for filepath in
                 filepaths]

        bpy.ops.import_image.to_plane(files=files, directory=dir, offset=True)

        return {'FINISHED'}


class SPIO_OT_import_image_as_nodes(image_io, bpy.types.Operator):
    bl_idname = "spio.import_image_as_nodes"
    bl_label = "Import as Nodes"

    def execute(self, context):
        location_X, location_Y = context.space_data.cursor_location
        for filepath in self.files.split('$$'):
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

        return {'FINISHED'}


def get_active_tree(context):
    tree = context.space_data.node_tree
    path = []
    # Get nodes from currently edited tree.
    # If user is editing a group, space_data.node_tree is still the base level (outside group).
    # context.active_node is in the group though, so if space_data.node_tree.nodes.active is not
    # the same as context.active_node, the user is in a group.
    # Check recursively until we find the real active node_tree:
    if tree.nodes.active:
        while tree.nodes.active != context.active_node:
            tree = tree.nodes.active.node_tree
            path.append(tree)
    return tree, path


def get_nodes_links(context):
    tree, path = get_active_tree(context)
    return tree.nodes, tree.links


class SPIO_OT_import_image_PBR_setup(image_io, bpy.types.Operator):
    bl_idname = "spio.import_image_pbr_setup"
    bl_label = "Import and Setup PBR (Principled)"

    def execute(self, context):
        # from addon_utils import enable
        # enable('node_wrangler')

        filepaths = self.files.split('$$')
        dir = os.path.dirname(filepaths[0]) + '\\'
        files = '$$'.join([os.path.basename(filepath) for filepath in filepaths])

        # print(filepaths[0])
        # print(dir)
        # print(files)

        bpy.ops.spio.create_principled_set_up_material(
            # filepath=filepaths[0],
            directory=dir,
            files=files,
            use_context_space=True)

        return {'FINISHED'}


class SPIO_OT_import_image_as_world(image_io, bpy.types.Operator):
    '''Hold Alt to import as asset'''
    bl_idname = "spio.import_image_as_world"
    bl_label = "Import as World"

    def invoke(self, context, event):
        for filepath in self.files.split('$$'):
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

        return {'FINISHED'}


class SPIO_OT_import_image_as_light_gobos(image_io, bpy.types.Operator):
    '''Hold Alt to import as asset'''
    bl_idname = "spio.import_image_as_light_gobos"
    bl_label = "Import as Light Gobos"

    def invoke(self, context, event):
        for filepath in self.files.split('$$'):
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
            nt.links.new(n_img.outputs[0], n_emi.inputs[0])

            if event.alt:
                light.asset_mark()
                override = context.copy()
                override['id'] = light
                bpy.ops.ed.lib_id_load_custom_preview(override, filepath=filepath)

        return {'FINISHED'}


class SPIO_OT_import_image_as_parallax_material(image_io, bpy.types.Operator):
    '''Hold Alt to import as asset'''
    bl_idname = "spio.import_image_as_parallax_material"
    bl_label = "Import as Parallax Material"

    def invoke(self, context, event):
        for filepath in self.files.split('$$'):
            cur_dir = os.path.dirname(__file__)
            node_group_file = os.path.join(cur_dir, 'templates', "ParallaxMapping_2022_5_9.blend")

            img = self.load_image_by_path(filepath)

            with bpy.data.libraries.load(node_group_file, link=False) as (data_from, data_to):
                data_to.materials = ['ParallaxMapping']

            mat = bpy.data.materials['ParallaxMapping']
            base, sep, ext = img.name.rpartition('.')
            mat.name = base

            for node in mat.node_tree.nodes:
                if node.name == '__IMAGE__':
                    image_group = node.node_tree
                    for sub_node in image_group.nodes:
                        if sub_node.name == '__REPLACE__':
                            sub_node.image = img
                            break
                    break

            if event.alt:
                mat.asset_mark()

        return {'FINISHED'}


from ..clipboard.clipboard import Clipboard as Clipboard, get_dir


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
        image_path = os.path.join(get_dir(), active_image.name + '.png')

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


class SPIO_OT_import_pbr_folders_as_materials(bpy.types.Operator):
    """Hold Alt to import as asset"""
    bl_idname = "spio.import_pbr_folders_as_materials"
    bl_label = "Import PBR Folders as Materials"
    bl_options = {'UNDO_GROUPED'}

    dirs: StringProperty(name='Join Dirs')

    def invoke(self, context, event):
        dirs = self.dirs.split('$$')

        for i, dir in enumerate(dirs):
            # add and set slot
            bpy.ops.spio.create_principled_set_up_material(directory=dir + '/', use_context_space=False,
                                                           mark_asset=event.alt)

        return {'FINISHED'}


import re
from pathlib import Path
from mathutils import Vector
from os import path
from ..preferences.prefs import get_pref


# base on node wrangler

class SPIO_OT_create_principled_set_up_material(bpy.types.Operator):
    bl_idname = "spio.create_principled_set_up_material"
    bl_label = "Principled Texture Setup"
    bl_description = "Add Texture Node Setup for Principled BSDF"
    bl_options = {'UNDO'}

    directory: StringProperty(
        name='Directory',
    )

    relative_path: BoolProperty(
        name='Relative Path',
        description='Set the file path relative to the blend file, when possible',
        default=True
    )

    # file name combine with $$ to split files
    files: StringProperty()
    # to check is single mode or batch mode(multiple dirs)
    use_context_space: BoolProperty(default=False)
    mark_asset: BoolProperty(default=False)

    def create_material(self, name):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        return mat

    def get_mat_nodes_links(self, material):
        tree = material.node_tree
        return tree.nodes, tree.links

    def execute(self, context):
        # create material
        if self.use_context_space:
            nodes, links = get_nodes_links(context)
        else:
            mat = self.create_material(name=os.path.basename(self.directory[:-1]))
            if self.mark_asset:
                mat.asset_mark()  # mark as asset
            nodes, links = self.get_mat_nodes_links(mat)

            # set active node
            for node in nodes:
                if node.bl_idname == 'ShaderNodeBsdfPrincipled':
                    nodes.active = node
                    break

        active_node = nodes.active
        if not active_node or active_node.bl_idname != 'ShaderNodeBsdfPrincipled':
            self.report({'ERROR'}, 'No Principled BSDF node is active')
            return {'CANCELLED'}

        # Helper_functions
        def split_into__components(fname):
            # Split filename into components
            # 'WallTexture_diff_2k.002.jpg' -> ['Wall', 'Texture', 'diff', 'k']
            # Remove extension
            fname = path.splitext(fname)[0]
            # Remove digits
            fname = ''.join(i for i in fname if not i.isdigit())
            # Separate CamelCase by space
            fname = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", fname)
            # Replace common separators with SPACE
            separators = ['_', '.', '-', '__', '--', '#']
            for sep in separators:
                fname = fname.replace(sep, ' ')

            components = fname.split(' ')
            components = [c.lower() for c in components]
            return components

        # Filter textures names for texturetypes in filenames
        # [Socket Name, [abbreviations and keyword list], Filename placeholder]
        tags = get_pref().principled_tags
        normal_abbr = tags.normal.split(' ')
        bump_abbr = tags.bump.split(' ')
        gloss_abbr = tags.gloss.split(' ')
        rough_abbr = tags.rough.split(' ')
        socketnames = [
            ['Displacement', tags.displacement.split(' '), None],
            ['Base Color', tags.base_color.split(' '), None],
            ['Subsurface Color', tags.sss_color.split(' '), None],
            ['Metallic', tags.metallic.split(' '), None],
            ['Specular', tags.specular.split(' '), None],
            ['Roughness', rough_abbr + gloss_abbr, None],
            ['Normal', normal_abbr + bump_abbr, None],
            ['Transmission', tags.transmission.split(' '), None],
            ['Emission', tags.emission.split(' '), None],
            ['Alpha', tags.alpha.split(' '), None],
            ['Ambient Occlusion', tags.ambient_occlusion.split(' '), None],
        ]

        def is_matches(fname, sname):
            filenamecomponents = split_into__components(fname)
            matches = set(sname[1]).intersection(set(filenamecomponents))
            # TODO: ignore basename (if texture is named "fancy_metal_nor", it will be detected as metallic map, not normal map)
            if matches:
                sname[2] = fname
                return True

        # Look through texture_types and set value as filename of first matched file
        def match_files_to_socket_names(directory):
            for sname in socketnames:
                if self.files != '':
                    for fname in self.files.split('$$'):
                        if is_matches(fname, sname):
                            break
                else:
                    for file in os.listdir(directory):
                        if is_matches(file, sname):
                            break

        match_files_to_socket_names(self.directory)
        # Remove socketnames without found files
        socketnames = [s for s in socketnames if s[2]
                       and path.exists(self.directory + s[2])]
        if not socketnames:
            self.report({'INFO'}, 'No matching images found')
            print('No matching images found')
            return {'CANCELLED'}

        # Don't override path earlier as os.path is used to check the absolute path
        import_path = self.directory
        if self.relative_path:
            if bpy.data.filepath:
                try:
                    import_path = bpy.path.relpath(self.directory)
                except ValueError:
                    pass

        # Add found images
        print('\nMatched Textures:')
        texture_nodes = []
        disp_texture = None
        ao_texture = None
        normal_node = None
        roughness_node = None
        for i, sname in enumerate(socketnames):
            print(i, sname[0], sname[2])

            # DISPLACEMENT NODES
            if sname[0] == 'Displacement':
                disp_texture = nodes.new(type='ShaderNodeTexImage')
                img = bpy.data.images.load(path.join(import_path, sname[2]))
                disp_texture.image = img
                disp_texture.label = 'Displacement'
                if disp_texture.image:
                    disp_texture.image.colorspace_settings.is_data = True

                # Add displacement offset nodes
                disp_node = nodes.new(type='ShaderNodeDisplacement')
                # Align the Displacement node under the active Principled BSDF node
                disp_node.location = active_node.location + Vector((100, -700))
                link = links.new(disp_node.inputs[0], disp_texture.outputs[0])

                # TODO Turn on true displacement in the material
                # Too complicated for now

                # Find output node
                output_node = [n for n in nodes if n.bl_idname == 'ShaderNodeOutputMaterial']
                if output_node:
                    if not output_node[0].inputs[2].is_linked:
                        link = links.new(output_node[0].inputs[2], disp_node.outputs[0])

                continue

            # AMBIENT OCCLUSION TEXTURE
            if sname[0] == 'Ambient Occlusion':
                ao_texture = nodes.new(type='ShaderNodeTexImage')
                img = bpy.data.images.load(path.join(import_path, sname[2]))
                ao_texture.image = img
                ao_texture.label = sname[0]
                if ao_texture.image:
                    ao_texture.image.colorspace_settings.is_data = True

                continue

            if not active_node.inputs[sname[0]].is_linked:
                # No texture node connected -> add texture node with new image
                texture_node = nodes.new(type='ShaderNodeTexImage')
                img = bpy.data.images.load(path.join(import_path, sname[2]))
                texture_node.image = img

                # NORMAL NODES
                if sname[0] == 'Normal':
                    # Test if new texture node is normal or bump map
                    fname_components = split_into__components(sname[2])
                    match_normal = set(normal_abbr).intersection(set(fname_components))
                    match_bump = set(bump_abbr).intersection(set(fname_components))
                    if match_normal:
                        # If Normal add normal node in between
                        normal_node = nodes.new(type='ShaderNodeNormalMap')
                        link = links.new(normal_node.inputs[1], texture_node.outputs[0])
                    elif match_bump:
                        # If Bump add bump node in between
                        normal_node = nodes.new(type='ShaderNodeBump')
                        link = links.new(normal_node.inputs[2], texture_node.outputs[0])

                    link = links.new(active_node.inputs[sname[0]], normal_node.outputs[0])
                    normal_node_texture = texture_node

                elif sname[0] == 'Roughness':
                    # Test if glossy or roughness map
                    fname_components = split_into__components(sname[2])
                    match_rough = set(rough_abbr).intersection(set(fname_components))
                    match_gloss = set(gloss_abbr).intersection(set(fname_components))

                    if match_rough:
                        # If Roughness nothing to to
                        link = links.new(active_node.inputs[sname[0]], texture_node.outputs[0])

                    elif match_gloss:
                        # If Gloss Map add invert node
                        invert_node = nodes.new(type='ShaderNodeInvert')
                        link = links.new(invert_node.inputs[1], texture_node.outputs[0])

                        link = links.new(active_node.inputs[sname[0]], invert_node.outputs[0])
                        roughness_node = texture_node

                else:
                    # This is a simple connection Texture --> Input slot
                    link = links.new(active_node.inputs[sname[0]], texture_node.outputs[0])

                # Use non-color for all but 'Base Color' Textures
                if not sname[0] in ['Base Color', 'Emission'] and texture_node.image:
                    texture_node.image.colorspace_settings.is_data = True

            else:
                # If already texture connected. add to node list for alignment
                texture_node = active_node.inputs[sname[0]].links[0].from_node

            # This are all connected texture nodes
            texture_nodes.append(texture_node)
            texture_node.label = sname[0]

        if disp_texture:
            texture_nodes.append(disp_texture)

        if ao_texture:
            # We want the ambient occlusion texture to be the top most texture node
            texture_nodes.insert(0, ao_texture)

        # Alignment
        for i, texture_node in enumerate(texture_nodes):
            offset = Vector((-550, (i * -280) + 200))
            texture_node.location = active_node.location + offset

        if normal_node:
            # Extra alignment if normal node was added
            normal_node.location = normal_node_texture.location + Vector((300, 0))

        if roughness_node:
            # Alignment of invert node if glossy map
            invert_node.location = roughness_node.location + Vector((300, 0))

        # Add texture input + mapping
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = active_node.location + Vector((-1050, 0))
        if len(texture_nodes) > 1:
            # If more than one texture add reroute node in between
            reroute = nodes.new(type='NodeReroute')
            texture_nodes.append(reroute)
            tex_coords = Vector(
                (texture_nodes[0].location.x, sum(n.location.y for n in texture_nodes) / len(texture_nodes)))
            reroute.location = tex_coords + Vector((-50, -120))
            for texture_node in texture_nodes:
                link = links.new(texture_node.inputs[0], reroute.outputs[0])
            link = links.new(reroute.inputs[0], mapping.outputs[0])
        else:
            link = links.new(texture_nodes[0].inputs[0], mapping.outputs[0])

        # Connect texture_coordiantes to mapping node
        texture_input = nodes.new(type='ShaderNodeTexCoord')
        texture_input.location = mapping.location + Vector((-200, 0))
        link = links.new(mapping.inputs[0], texture_input.outputs[2])

        # Create frame around tex coords and mapping
        frame = nodes.new(type='NodeFrame')
        frame.label = 'Mapping'
        mapping.parent = frame
        texture_input.parent = frame
        frame.update()

        # Create frame around texture nodes
        frame = nodes.new(type='NodeFrame')
        frame.label = 'Textures'
        for tnode in texture_nodes:
            tnode.parent = frame
        frame.update()

        # Just to be sure
        active_node.select = False
        nodes.update()
        links.update()
        nodes.id_data.update_tag()
        return {'FINISHED'}


classes = (
    SPIO_OT_import_image_as_reference,
    SPIO_OT_import_image_as_parallax_material,
    SPIO_OT_import_image_as_nodes,
    SPIO_OT_import_image_PBR_setup,
    SPIO_OT_import_image_as_world,
    SPIO_OT_import_image_as_plane,
    SPIO_OT_import_image_as_light_gobos,
    SPIO_OT_import_pbr_folders_as_materials,
    SPIO_OT_create_principled_set_up_material,

    SPIO_OT_export_pixel,
    SPIO_OT_export_image,

)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
