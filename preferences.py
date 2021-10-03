import bpy
import os
from bpy.props import (EnumProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)
from bpy.types import PropertyGroup

from . import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


class OperatorProperty(PropertyGroup):
    name: StringProperty(name='Property')
    value: StringProperty(name='Value')


def correct_blidname(self, context):
    if self.bl_idname.startswith('bpy.ops.'):
        self.bl_idname = self.bl_idname[8:]
    if self.bl_idname.endswith('()'):
        self.bl_idname = self.bl_idname[:-2]


def correct_name(self, context):
    pref = get_pref()
    names = [item.name for item in pref.config_list if item.name == self.name and item.name != '']
    if len(names) != 1:
        self.name += '(1)'


class ExtensionOperatorProperty(PropertyGroup):
    # UI
    expand_panel: BoolProperty(name='Expand Panel', default=True)
    # USE
    use_config: BoolProperty(name='Use', default=True)

    name: StringProperty(name='Preset Name', update=correct_name)
    extension: StringProperty(name='Extension')
    bl_idname: StringProperty(name='Operator Identifier', update=correct_blidname)
    prop_list: CollectionProperty(type=OperatorProperty)


class SPIO_OT_OperatorInputAction(bpy.types.Operator):
    """Add / Remove current prop"""
    bl_idname = "wm.spio_operator_input_action"
    bl_label = "Operator Props Operate"
    bl_options = {'REGISTER', 'UNDO'}

    config_list_index: IntProperty()
    prop_index: IntProperty()
    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
    ])

    def execute(self, context):
        pref = get_pref()
        item = pref.config_list[self.config_list_index]

        if self.action == 'ADD':
            item.prop_list.add()
        else:
            item.prop_list.remove(self.prop_index)

        return {'FINISHED'}


class SPIO_OT_ExtensionListAction(bpy.types.Operator):
    """Add / Remove current config"""
    bl_idname = "wm.spio_config_list_action"
    bl_label = "Config Operate"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty()
    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
    ])

    def execute(self, context):
        pref = get_pref()
        if self.action == 'ADD':
            item = pref.config_list.add()
            item.name = f'Config{len(pref.config_list)}'
        else:
            pref.config_list.remove(self.index)

        return {'FINISHED'}


class SPIO_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    force_unicode: BoolProperty(name='Force Unicode', description='Force to use "utf-8" to decode filepath')
    config_list: CollectionProperty(type=ExtensionOperatorProperty)

    def draw(self, context):
        layout = self.layout.column()
        layout.prop(self, 'force_unicode')

        row = layout.row()
        row.alignment = 'CENTER'
        row.scale_y = 1.25
        row.operator('spio.config_import', icon='IMPORT')
        row.operator('spio.config_export', icon='EXPORT')

        row = layout.row(align=True)
        row.alignment = 'LEFT'

        for config_list_index, item in enumerate(self.config_list):
            col = layout.box().column()

            row = col.split(factor=0.7)

            row.prop(item, 'expand_panel', text=item.name + ' : ' + item.extension,
                     icon='TRIA_DOWN' if item.expand_panel else 'TRIA_RIGHT',
                     emboss=False)

            sub = row.row(align=True)
            sub.prop(item, 'use_config')
            d = sub.operator('wm.spio_config_list_action', text='', icon='PANEL_CLOSE', emboss=False)
            d.action = 'REMOVE'
            d.index = config_list_index

            if not item.expand_panel: continue

            col.use_property_split = True
            col.prop(item, 'name')
            col.prop(item, 'extension')

            col.prop(item, 'bl_idname')

            box = col.box().column()
            box.label(text='Operator Property', icon='PROPERTIES')

            if item.bl_idname == '':
                box.alert = True
                box.label(text='Fill in Operator Identifier First', icon='ERROR')
                continue

            for prop_index, prop_item in enumerate(item.prop_list):
                col = box.box().column()

                row = col.row(align=True)
                row.prop(prop_item, 'name')
                col.prop(prop_item, 'value')

                d = row.operator('wm.spio_operator_input_action', text='', icon='PANEL_CLOSE', emboss=False)
                d.action = 'REMOVE'
                d.config_list_index = config_list_index
                d.prop_index = prop_index

            col = box.box().column()
            row = col.row()
            row.alignment = 'LEFT'
            d = row.operator('wm.spio_operator_input_action', text='Add Property', icon='ADD', emboss=False)
            d.action = 'ADD'
            d.config_list_index = config_list_index

        row = layout.box().row(align=True)
        row.alignment = 'LEFT'
        row.operator('wm.spio_config_list_action', text='Add Extension Config', icon='FILE_NEW',
                     emboss=False).action = 'ADD'


def register():
    bpy.utils.register_class(OperatorProperty)
    bpy.utils.register_class(SPIO_OT_OperatorInputAction)
    bpy.utils.register_class(ExtensionOperatorProperty)
    bpy.utils.register_class(SPIO_OT_ExtensionListAction)
    bpy.utils.register_class(SPIO_Preference)


def unregister():
    bpy.utils.unregister_class(OperatorProperty)
    bpy.utils.unregister_class(SPIO_OT_OperatorInputAction)
    bpy.utils.unregister_class(ExtensionOperatorProperty)
    bpy.utils.unregister_class(SPIO_OT_ExtensionListAction)
    bpy.utils.unregister_class(SPIO_Preference)
