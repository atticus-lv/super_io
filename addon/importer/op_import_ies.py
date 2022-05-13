import bpy
import os
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty


class SPIO_OT_import_ies(bpy.types.Operator):
    """Import IES file as light"""

    bl_idname = 'spio.import_ies'
    bl_label = 'Import IES file as light'

    filepath: StringProperty()  # list of filepath, join with$$

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return (
                    context.area.ui_type == "VIEW_3D"
                    and context.mode == "OBJECT")

    def execute(self, context):
        for i, file in enumerate(self.filepath.split('$$')):
            with open(file, 'r') as f:
                data = f.read()

            filename = os.path.basename(file)[:-4]
            # create blender text file
            ies_file = bpy.data.texts.new(name=filename)
            ies_file.write(data)

            # create light
            bpy.ops.object.light_add(type='POINT')
            light = context.object
            light.name = filename
            light.location = i * 8, 0, 0

            d = light.data
            d.shadow_soft_size = 0.05 # set a small shadow soft size to get clear shapes
            d.use_nodes = True
            nt = d.node_tree

            # create nodes
            n_emi = nt.nodes['Emission']

            n_ies = nt.nodes.new('ShaderNodeTexIES')
            n_ies.location = -200, 300
            n_ies.ies = ies_file

            n_map = nt.nodes.new('ShaderNodeMapping')
            n_map.location = -400, 300

            n_tc = nt.nodes.new('ShaderNodeTexCoord')
            n_tc.location = -600, 300

            # create links
            nt.links.new(n_tc.outputs[1], n_map.inputs[0])
            nt.links.new(n_map.outputs[0], n_ies.inputs[0])
            nt.links.new(n_ies.outputs[0], n_emi.inputs[1])

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_import_ies)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_ies)
