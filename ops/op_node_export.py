import bpy
import os
from .op_image_io import get_active_tree, get_nodes_links


def enum_active_node_sockets(self, context):
    if context.active_node and len(context.active_node.outputs) != 0:
        return [(a.name, a.name, a.name) for a in context.active_node.outputs]
    else:
        return [("NONE", "None", ""), ]


def enum_uv(self, context):
    enum_uv = []
    if context.active_object and context.active_object.type == "MESH":
        for uv in context.active_object.data.uv_layers:
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
    bl_options = {'INTERNAL'}

    operator_type: bpy.props.EnumProperty(name='Type',
                                          items=[('NODE', 'Node', 'Export node as texture'),
                                                 ('PBR', 'Principal BSDF (PBR)',
                                                  'Export principal node as pbr textures'), ],
                                          default='NODE')

    socket: bpy.props.EnumProperty(name="Output",
                                   items=enum_active_node_sockets,
                                   options={'SKIP_SAVE'}, )
    uv_map: bpy.props.EnumProperty(name="UV Map",
                                   items=enum_uv, )

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

    custom_resolution: bpy.props.IntProperty(name='Resolution', default=2048, min=2, max=8192)

    samples: bpy.props.IntProperty(name='Samples', default=1, min=1, soft_max=64)
    margin: bpy.props.IntProperty(default=16, name="Margin", step=4)
    extension: bpy.props.EnumProperty(name='Extension',
                                      items=[('png', 'PNG', ''),],
                                      default='png')
    color_space: bpy.props.EnumProperty(name="Color Space",
                                        items=[
                                            ('sRGB', 'sRGB', ''),
                                            ('Non-Color', 'Non-Color', ''),
                                        ],
                                        default='sRGB')

    @classmethod
    def poll(cls, context):
        return (context.area.type == "NODE_EDITOR" and
                context.space_data.edit_tree and
                context.active_node and
                context.active_object and
                len(context.selected_objects) != 0)

    def invoke(self, context, event):
        if bpy.data.filepath == '':
            self.report({'ERROR'}, "Save your file first!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        row = box.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.label(text=context.material.name, icon='MATERIAL')
        if self.operator_type == 'NODE':
            row.label(icon='RIGHTARROW')
            row.label(text=context.active_node.name, icon='NODE')
            row.label(icon='RIGHTARROW')
            row.label(text=self.socket, icon='NODE_SEL')

        box.separator()

        box.prop(self, "operator_type")
        if self.operator_type == 'PBR':
            if context.active_node.bl_idname != 'ShaderNodeBsdfPrincipled':
                box.label(text='Selected node is not a "Principled BSDF" node', icon='ERROR')
        else:
            box.prop(self, "socket")
            row = box.row(align=True)
            row.prop(self, "color_space", expand=True)

        box.prop(self, "uv_map")

        box = layout.box()
        box.prop(self, "device")
        box.prop(self, "samples")
        box.separator(factor=0.5)

        box.separator()

        col = box.column(align=True)
        col.prop(self, "resolution")
        if self.resolution == 'CUSTOM':
            col.prop(self, "custom_resolution", text='Custom')

        row = box.row(align=True)
        # row.prop(self, "extension", expand=True)
        box.prop(self, "margin")

        layout.label(text='This could take a few minutes', icon='INFO')

    def execute(self, context):
        tree, path = get_active_tree(context)
        nodes, links = get_nodes_links(context)

        active_node = context.active_node
        # store origin socket / nodes
        ori_output_socket = None
        ori_uv = None
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

            bake_img_node = self.bake(context, active_node,
                                      resolution=resolution,
                                      bake_type=bake_type,
                                      color_space=self.color_space)


        elif self.operator_type == 'PBR':
            color_socket = active_node.inputs['Base Color']
            roughness_socket = active_node.inputs['Roughness']
            metallic_socket = active_node.inputs['Metallic']
            normal_socket = active_node.inputs['Normal']

            normal_node = self.bake(context, active_node,
                                    resolution=resolution,
                                    bake_type='NORMAL',
                                    extra_channel='Normal',
                                    color_space='Non-Color')

            links.new(emit_node.outputs[0], output_node.inputs[0])

            temp_rgb = None
            if color_socket.is_linked:
                links.new(color_socket.links[0].from_socket, emit_node.inputs[0])
            else:
                temp_rgb = nodes.new(type='ShaderNodeRGB')
                temp_rgb.outputs[0].default_value = color_socket.default_value
                links.new(temp_rgb.outputs[0], emit_node.inputs[0])

            color_node = self.bake(context, active_node,
                                   resolution=resolution,
                                   bake_type='EMIT',
                                   extra_channel='Color')
            if temp_rgb: nodes.remove(temp_rgb)

            temp_value = None
            if roughness_socket.is_linked:
                links.new(roughness_socket.links[0].from_socket, emit_node.inputs[0])
            else:
                temp_value = nodes.new(type='ShaderNodeValue')
                temp_value.outputs[0].default_value = roughness_socket.default_value
                links.new(temp_value.outputs[0], emit_node.inputs[0])

            roughness_node = self.bake(context, active_node,
                                       resolution=resolution,
                                       bake_type='EMIT',
                                       extra_channel='Roughness',
                                       color_space='Non-Color')
            if temp_value: nodes.remove(temp_value)

            temp_value = None
            if metallic_socket.is_linked:
                links.new(metallic_socket.links[0].from_socket, emit_node.inputs[0])
            else:
                temp_value = nodes.new(type='ShaderNodeValue')
                temp_value.outputs[0].default_value = metallic_socket.default_value
                links.new(temp_value.outputs[0], emit_node.inputs[0])

            metallic_node = self.bake(context, active_node,
                                      resolution=resolution,
                                      bake_type='EMIT',
                                      extra_channel='Metallic',
                                      color_space='Non-Color')

            if temp_value: nodes.remove(temp_value)

        # restore
        if ori_output_socket is not None:
            links.new(ori_output_socket, output_node.inputs[0])
        if ori_uv is not None:
            ori_uv.active = True

        # set select
        for node in nodes:
            node.select = False
        nodes.remove(emit_node)
        nodes.active = active_node
        active_node.select = True

        return {'FINISHED'}

    def bake(self, context, active_node, resolution='2048', bake_type="EMIT",
             color_space='sRGB', extra_channel=''):

        nodes, links = get_nodes_links(context)

        if self.operator_type == 'NODE':
            image_name = "_".join([context.material.name, active_node.name, self.resolution])

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
