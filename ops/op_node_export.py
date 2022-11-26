import bpy
import os
from .op_image_io import get_active_tree, get_nodes_links


def enum_active_node_sockets(self, context):
    if context.active_node and len(context.active_node.outputs) != 0:
        return [(a.name, a.name, a.name, 'NODE_SEL', i) for i, a in enumerate(context.active_node.outputs)]
    else:
        return [("NONE", "None", ""), ]


def enum_uv(self, context):
    enum_uv = []
    if context.active_object and context.active_object.type == "MESH":
        for i, uv in enumerate(context.active_object.data.uv_layers):
            enum_uv.append((uv.name, uv.name, ''))
    else:
        return [("NONE", "None", ""), ]

    if len(enum_uv) == 0:
        return [("NONE", "None", ""), ]

    return enum_uv


class SPIO_OT_export_shader_node_as_texture(bpy.types.Operator):
    """Select a node and export it as a texture\nSelect active object first"""
    bl_idname = "spio.export_shader_node_as_texture"
    bl_label = "Export Node as Texture"
    bl_options = {'INTERNAL', 'UNDO_GROUPED'}

    operator_type: bpy.props.EnumProperty(name='Type',
                                          items=[('NODE', 'Node', 'Export node as texture'),
                                                 ('PBR', 'PBR',
                                                  'Export principal node as pbr textures'), ],
                                          default='NODE')
    # source
    socket: bpy.props.EnumProperty(name="Output",
                                   items=enum_active_node_sockets,
                                   options={'SKIP_SAVE'}, )
    uv_map: bpy.props.EnumProperty(name="UV Map",
                                   items=enum_uv, )

    # bake selected to active
    use_selected_to_active: bpy.props.BoolProperty(name="Selected to Active")

    # render
    device: bpy.props.EnumProperty(name='Device',
                                   items=[
                                       ('CPU', 'CPU', 'CPU'),
                                       ('GPU', 'GPU', 'GPU'),
                                   ], default='GPU')

    resolution: bpy.props.EnumProperty(name='Resolution',
                                       items=[
                                           ('1024', '1k', ''),
                                           ('2048', '2k', ''),
                                           ('4096', '4k', ''),
                                           ('8192', '8k', ''),
                                           ('CUSTOM', 'Custom', ''), ],
                                       default='2048')
    # image output
    custom_resolution: bpy.props.IntProperty(name='Resolution', default=2048, min=2, max=8192)

    samples: bpy.props.IntProperty(name='Samples', default=1, min=1, soft_max=64)
    margin: bpy.props.IntProperty(default=16, name="Margin", min=0)
    extension: bpy.props.EnumProperty(name='Extension',
                                      items=[('png', 'PNG', ''), ],
                                      default='png')
    # node mode
    color_space: bpy.props.EnumProperty(name="Color Space",
                                        items=[
                                            ('sRGB', 'sRGB', ''),
                                            ('Non-Color', 'Non-Color', ''),
                                        ],
                                        default='sRGB')
    # pbr mode
    skip_pbr_unlinked: bpy.props.BoolProperty(name="Skip Unlinked Socket", default=True)
    replace: bpy.props.BoolProperty(name="Link to bake images", default=True)

    # sequence (only node mode)
    sequence: bpy.props.BoolProperty(name='Sequence', default=False)
    frame_start: bpy.props.IntProperty(name='Frame Start')
    frame_end: bpy.props.IntProperty(name='Frame End')
    frame_step: bpy.props.IntProperty(name='Frame Step', min=1)

    @classmethod
    def poll(cls, context):
        return (context.area.type == "NODE_EDITOR" and
                context.space_data.edit_tree and
                context.active_node and
                context.active_object)

    def invoke(self, context, event):
        if bpy.data.filepath == '':
            self.report({'ERROR'}, "Save your file first!")
            return {'CANCELLED'}

        # sequence
        self.frame_step = context.scene.frame_step
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        row = box.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.label(text=context.material.name, icon='MATERIAL')
        row.label(icon='RIGHTARROW_THIN')
        row.label(text=context.active_node.name, icon='NODE')

        if self.operator_type == 'PBR':
            if context.active_node.bl_idname != 'ShaderNodeBsdfPrincipled':
                col = box.column()
                col.alert = True
                col.label(text="Not a 'Principled BSDF' node", icon='ERROR')

        row = box.row(align=True)
        row.prop(self, "operator_type", expand=True)

        if self.operator_type != 'PBR':
            box.prop(self, "socket")
            row = box.row(align=True)
            row.prop(self, "color_space", expand=True)

        box.prop(self, "uv_map")
        box.prop(self, "use_selected_to_active")

        if self.use_selected_to_active:
            subbox = box.box().column(align=True)
            subbox.prop(context.scene.render.bake, "use_cage")
            subbox.prop(context.scene.render.bake, "cage_extrusion")
            subbox.prop(context.scene.render.bake, "max_ray_distance")

        box = layout.box()
        box.prop(self, "device")
        box.prop(self, "samples")
        box.separator(factor=0.5)

        col = box.column(align=True)
        col.prop(self, "resolution")
        if self.resolution == 'CUSTOM':
            col.prop(self, "custom_resolution", text='Custom')

        # row = box.row(align=True)
        # row.prop(self, "extension", expand=True)
        box.prop(self, "margin")
        if self.operator_type == 'PBR':
            box = layout.box()
            box.prop(self, "skip_pbr_unlinked")
            box.prop(self, "replace")
        else:
            box = layout.box()
            box.prop(self, 'sequence')
            if self.sequence:
                col = box.column(align=True)
                col.prop(self, 'frame_start')
                col.prop(self, 'frame_end')
                col.prop(self, 'frame_step')

        layout.label(text='This could take a few minutes', icon='INFO')

    def execute(self, context):
        tree, path = get_active_tree(context)
        nodes, links = get_nodes_links(context)

        active_node = context.active_node
        # store origin socket / nodes
        ori_output_socket = None
        ori_uv = None
        ori_selected_to_active = context.scene.render.bake.use_selected_to_active
        if not self.use_selected_to_active:
            context.scene.render.bake.use_selected_to_active = False

        output_node = None

        # set origin socket
        for node in nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial' and node.inputs[0].is_linked:
                output_node = node
                ori_output_socket = node.inputs[0].links[0].from_socket
                break

        # check necessary
        if self.socket == 'NONE':
            self.report({'ERROR'}, "No output socket selected")
            return {'CANCELLED'}

        elif output_node is None:
            self.report({'ERROR'}, "No output node found")
            return {'CANCELLED'}

        elif self.uv_map == 'NONE':
            self.report({'ERROR'}, "No UV map selected")
            return {'CANCELLED'}
        elif len(context.selected_objects) == 0:
            self.report({'ERROR'}, "Select at least one object")
            return {'CANCELLED'}

        # set active uv
        for uv_layer in context.active_object.data.uv_layers:
            if uv_layer.active:
                ori_uv = uv_layer
                break

        for uv_layer in context.active_object.data.uv_layers:
            if uv_layer.name == self.uv_map:
                uv_layer.active = True
                break

        # create emit node for render
        emit_node = nodes.new("ShaderNodeEmission")

        # bake texture
        resolution = str(self.custom_resolution) if self.resolution == 'CUSTOM' else self.resolution

        # bake simple socket
        if self.operator_type == 'NODE':
            links.new(active_node.outputs[self.socket], emit_node.inputs[0])
            links.new(emit_node.outputs[0], output_node.inputs[0])

            if active_node.outputs[self.socket].type == 'SHADER':
                bake_type = 'COMBINED'
            else:
                bake_type = 'EMIT'

            if not self.sequence:
                bake_img_node = self.bake(context, active_node,
                                          resolution=resolution,
                                          bake_type=bake_type,
                                          color_space=self.color_space)
            else:
                if self.frame_end < self.frame_start:
                    self.frame_end = self.frame_start

                frame_duration = int((self.frame_end + 1 - self.frame_start) / self.frame_step)

                for i in range(frame_duration):
                    context.scene.frame_current = self.frame_start + i * self.frame_step

                    bake_img_node = self.bake(context, active_node,
                                              resolution=resolution,
                                              bake_type=bake_type,
                                              color_space=self.color_space)
                    # open dir for getting process
                    if i == 0:
                        bpy.ops.wm.path_open(filepath=os.path.dirname(bake_img_node.image.filepath))
                        bake_img_node.image.source = 'SEQUENCE'
                        bake_img_node.image_user.frame_duration = frame_duration
                        bake_img_node.image_user.use_cyclic = True
                        bake_img_node.image_user.use_auto_refresh = True
                    else:
                        bpy.data.images.remove(bake_img_node.image)
                        nodes.remove(bake_img_node)

        elif self.operator_type == 'PBR':
            # get bake socket
            color_socket = active_node.inputs['Base Color']
            roughness_socket = active_node.inputs['Roughness']
            metallic_socket = active_node.inputs['Metallic']
            normal_socket = active_node.inputs['Normal']

            # bake normal
            if normal_socket.is_linked or (
                    not normal_socket.is_linked and not self.skip_pbr_unlinked) or self.use_selected_to_active:
                normal_node = self.bake(context, active_node,
                                        resolution=resolution,
                                        bake_type='NORMAL',
                                        extra_channel='Normal',
                                        color_space='Non-Color')

                normal_node.location = active_node.location[0] - 600, active_node.location[1] - 700

                if self.replace:
                    normal_map_node = nodes.new("ShaderNodeNormalMap")

                    normal_map_node.location = normal_node.location[0] + 300, normal_node.location[1]

                    links.new(normal_node.outputs[0], normal_map_node.inputs[1])
                    links.new(normal_map_node.outputs[0], normal_socket)

            links.new(emit_node.outputs[0], output_node.inputs[0])

            # bake color
            temp_value = self.create_temp_node_from_socket(nodes, color_socket, type='ShaderNodeRGB')
            if color_socket.is_linked:
                links.new(color_socket.links[0].from_socket, emit_node.inputs[0])
            elif not self.skip_pbr_unlinked:
                links.new(temp_value.outputs[0], emit_node.inputs[0])

            if color_socket.is_linked or (not color_socket.is_linked and not self.skip_pbr_unlinked):
                color_node = self.bake(context, active_node,
                                       resolution=resolution,
                                       bake_type='EMIT',
                                       extra_channel='Color')

                color_node.location = active_node.location[0] - 300, active_node.location[1]

                if self.replace:
                    links.new(color_node.outputs[0], color_socket)

            nodes.remove(temp_value)

            # bake roughness
            temp_value = self.create_temp_node_from_socket(nodes, roughness_socket)
            if roughness_socket.is_linked:
                links.new(roughness_socket.links[0].from_socket, emit_node.inputs[0])
            elif not self.skip_pbr_unlinked:
                temp_value = nodes.new(type='ShaderNodeValue')
                temp_value.outputs[0].default_value = roughness_socket.default_value
                links.new(temp_value.outputs[0], emit_node.inputs[0])

            if roughness_socket.is_linked or (not roughness_socket.is_linked and not self.skip_pbr_unlinked):
                roughness_node = self.bake(context, active_node,
                                           resolution=resolution,
                                           bake_type='EMIT',
                                           extra_channel='Roughness',
                                           color_space='Non-Color')
                roughness_node.location = active_node.location[0] - 300, active_node.location[1] - 400

                if self.replace:
                    links.new(roughness_node.outputs[0], roughness_socket)

            nodes.remove(temp_value)

            # bake metallic
            temp_value = self.create_temp_node_from_socket(nodes, metallic_socket)
            if metallic_socket.is_linked:
                links.new(metallic_socket.links[0].from_socket, emit_node.inputs[0])
            elif not self.skip_pbr_unlinked:
                links.new(temp_value.outputs[0], emit_node.inputs[0])

            if metallic_socket.is_linked or (not metallic_socket.is_linked and not self.skip_pbr_unlinked):
                metallic_node = self.bake(context, active_node,
                                          resolution=resolution,
                                          bake_type='EMIT',
                                          extra_channel='Metallic',
                                          color_space='Non-Color')

                metallic_node.location = active_node.location[0] - 300, active_node.location[1] - 300

                if self.replace:
                    links.new(metallic_node.outputs[0], metallic_socket)

            nodes.remove(temp_value)

        # restore
        if ori_output_socket is not None:
            links.new(ori_output_socket, output_node.inputs[0])
        if ori_uv is not None:
            ori_uv.active = True

        context.scene.render.bake.use_selected_to_active = ori_selected_to_active

        # set select
        for node in nodes:
            node.select = False
        nodes.remove(emit_node)
        nodes.active = active_node
        active_node.select = True

        return {'FINISHED'}

    def create_temp_node_from_socket(self, nodes, socket, type='ShaderNodeValue'):
        temp_node = nodes.new(type)
        temp_node.outputs[0].default_value = socket.default_value

        return temp_node

    def bake(self, context, active_node, resolution='2048', bake_type="EMIT",
             color_space='sRGB', extra_channel=''):

        nodes, links = get_nodes_links(context)

        if self.operator_type == 'NODE':
            image_name = "_".join([context.material.name, active_node.name, self.resolution])
            if self.sequence:
                suffix = f'{context.scene.frame_current}'.zfill(4)
                image_name += '_' + suffix
        else:
            image_name = "_".join([context.material.name, extra_channel, self.resolution])

        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])

        # create image
        # know issue with float_buffer, a normal map should not be a 32 bit image, or will convert the color space from linear to srgb
        # https://developer.blender.org/T94446
        float_buffer = True
        if self.extension == 'png' or self.extension == 'tga':
            float_buffer = False

        img = bpy.data.images.new(image_name,
                                  width=int(resolution), height=int(resolution),
                                  alpha=True, float_buffer=float_buffer)
        # set color space
        img.colorspace_settings.name = color_space
        # create texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'Texture_Bake_Node'
        texture_node.location = active_node.location[0], active_node.location[1] + 200

        # set active node to bake
        for node in nodes:
            node.select = False

        texture_node.select = True
        texture_node.image = img
        nodes.active = texture_node

        # set property
        ori_engine = context.scene.render.engine
        ori_device = context.scene.cycles.device
        ori_direct = context.scene.render.bake.use_pass_direct
        ori_indirect = context.scene.render.bake.use_pass_indirect
        ori_samples = context.scene.cycles.samples
        ori_margin = context.scene.render.bake.margin
        # ori_view_transform = context.scene.view_settings.view_transform

        # set property
        if bake_type == 'COMBINED':
            context.scene.render.bake.use_pass_direct = False
            context.scene.render.bake.use_pass_indirect = False
        else:
            context.scene.render.bake.use_pass_direct = True
            context.scene.render.bake.use_pass_indirect = True

        context.scene.render.engine = 'CYCLES'
        context.scene.cycles.samples = self.samples
        context.scene.cycles.device = self.device
        # context.scene.view_settings.view_transform = 'Standard'
        # bake
        bpy.ops.object.bake(type=bake_type, use_clear=True)

        # restore property
        context.scene.render.bake.use_pass_direct = ori_direct
        context.scene.render.bake.use_pass_indirect = ori_indirect
        context.scene.cycles.samples = ori_samples
        context.scene.render.engine = ori_engine
        context.scene.cycles.device = ori_device
        context.scene.render.bake.margin = ori_margin
        # context.scene.view_settings.view_transform = ori_view_transform

        # save external
        dir = os.path.join(os.path.dirname(bpy.data.filepath), 'textures')
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = os.path.join(dir, image_name + '.' + self.extension)
        img.filepath_raw = filename
        img.save()  # save image without render setting's color space

        return texture_node


def register():
    bpy.utils.register_class(SPIO_OT_export_shader_node_as_texture)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_shader_node_as_texture)
