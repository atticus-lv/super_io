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
                                           ('512', '512', ''),
                                           ('1024', '1024', ''),
                                           ('2048', '2048', ''),
                                           ('4096', '4096', ''),
                                           ('8192', '8192', ''),
                                           ('CUSTOM', 'Custom', ''),
                                       ], default='2048')

    custom_resolution: bpy.props.IntProperty(name='Resolution', default=2048, min=2, max=8192)

    samples: bpy.props.IntProperty(name='Samples', default=1, min=1, soft_max=64)
    margin: bpy.props.IntProperty(default=16, name="Margin", step=4)

    @classmethod
    def poll(cls, context):
        return (context.area.type == "NODE_EDITOR" and
                context.space_data.edit_tree and
                context.active_node and
                context.active_object)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.label(text=context.material.name, icon='MATERIAL')
        row.label(icon='RIGHTARROW')
        row.label(text=context.active_node.name, icon='NODE')
        row.label(icon='RIGHTARROW')
        row.label(text=self.socket, icon='NODE_SEL')
        layout.separator(factor=0.5)

        box = layout.box()
        box.prop(self, "socket")
        box.prop(self, "uv_map")

        box = layout.box()
        box.prop(self, "device")
        box.prop(self, "samples")
        box.separator(factor=0.5)
        box.prop(self, "resolution")
        if self.resolution == 'CUSTOM':
            box.prop(self, "custom_resolution")
        box.prop(self, "margin")

        layout.label(text='This could take a few minutes', icon='INFO')

    def invoke(self, context, event):
        if bpy.data.filepath == '':
            self.report({'ERROR'}, "Save your file first!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self,width = 350)

    def execute(self, context):
        tree, path = get_active_tree(context)
        nodes, links = get_nodes_links(context)

        active_node = context.active_node
        # store origin socket / nodes
        ori_output_socket = None
        ori_uv = None
        ori_margin = context.scene.render.bake.margin
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
        links.new(active_node.outputs[self.socket], emit_node.inputs[0])
        links.new(emit_node.outputs[0], output_node.inputs[0])

        # bake texture
        resolution = str(self.custom_resolution) if self.resolution == 'CUSTOM' else self.resolution
        bake_type = "COMBINED" if active_node.outputs[self.socket].type == "SHADER" else 'EMIT'

        bake_img_node = self.bake(context, active_node,
                                  resolution=resolution,
                                  device=self.device,
                                  samples=self.samples,
                                  bake_type=bake_type)

        # restore
        if ori_output_socket is not None:
            links.new(ori_output_socket, output_node.inputs[0])
        if ori_uv is not None:
            ori_uv.active = True
        context.scene.render.bake.margin = ori_margin

        # set select
        for node in nodes:
            node.select = False
        bake_img_node.select = True
        nodes.active = bake_img_node
        nodes.remove(emit_node)

        return {'FINISHED'}

    def bake(self, context, active_node, resolution='2048', device='GPU', samples=1, bake_type="EMIT"):
        nodes, links = get_nodes_links(context)

        image_name = context.material.name + "_" + active_node.name + "_" + resolution
        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])

        # create image
        img = bpy.data.images.new(image_name,
                                  width=int(resolution), height=int(resolution),
                                  alpha=True, float_buffer=True)

        # create texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'Texture_Bake_Node'
        texture_node.location = active_node.location[0] - 400, active_node.location[1]

        # set active node to bake
        texture_node.select = True
        texture_node.image = img
        nodes.active = texture_node

        # set property
        ori_engine = context.scene.render.engine
        ori_device = context.scene.cycles.device
        ori_direct = context.scene.render.bake.use_pass_direct
        ori_indirect = context.scene.render.bake.use_pass_indirect
        ori_samples = context.scene.cycles.samples

        # set property
        if bake_type == 'COMBINED':
            context.scene.render.bake.use_pass_direct = False
            context.scene.render.bake.use_pass_indirect = False
        else:
            context.scene.render.bake.use_pass_direct = True
            context.scene.render.bake.use_pass_indirect = True

        context.scene.render.engine = 'CYCLES'
        context.scene.cycles.samples = samples
        context.scene.cycles.device = device

        bpy.ops.object.bake(type='EMIT')

        # restore property
        context.scene.render.bake.use_pass_direct = ori_direct
        context.scene.render.bake.use_pass_indirect = ori_indirect
        context.scene.cycles.samples = ori_samples
        context.scene.render.engine = ori_engine
        context.scene.cycles.device = ori_device

        # save external
        dir = os.path.join(os.path.dirname(bpy.data.filepath), 'textures')
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = os.path.join(dir, image_name + '.png')
        img.save_render(filename, scene=None)

        return texture_node


def register():
    bpy.utils.register_class(SPIO_OT_export_shader_node_as_texture)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_shader_node_as_texture)
