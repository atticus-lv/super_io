import bpy
import re

from bpy.props import (EnumProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)
from bpy.types import PropertyGroup
from .utils import get_pref


class OperatorProperty(PropertyGroup):
    name: StringProperty(name='Property')
    value: StringProperty(name='Value')

    # value_type: EnumProperty(items=[
    #     ('STRING', 'String', 'String'),
    #     ('INT', 'Integer', 'Integer'),
    #     ('FLOAT', 'Float', 'Float'),
    #     ('BOOL', 'Boolean', 'Boolean'),
    # ], default='STRING')
    # value_string:StringProperty(name= 'Value')
    # value_int: IntProperty(name='Value')
    # value_float: FloatProperty(name='Value')
    # value_bool: BoolProperty(name='Value')


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


def get_color_tag_enum_items():
    if bpy.app.version < (2, 93, 0):
        items = [
            (f'COLOR_0{i}',
             '',
             '',
             f'COLORSET_0{i}_VEC' if i != 0 else 'COLORSET_13_VEC', i) for i in range(0, 9)
        ]
    else:
        items = [
            (f'COLOR_0{i}',
             '',
             '',
             f'COLLECTION_COLOR_0{i}' if i != 0 else 'OUTLINER_COLLECTION', i) for i in range(0, 9)
        ]

    return items


enum_color_tag_items = get_color_tag_enum_items()


def enum_operator_type_addon():
    from ..imexporter.default_addon import addon_lib
    from ..imexporter.default_importer import importer_lib
    from ..imexporter.default_exporter import exporter_lib

    enums = []

    enums_addon = []
    enums_import = []
    enums_export = []

    for identifier, d in addon_lib.items():
        item = (identifier, d['name'], d['description'], d['icon'], d['number'])
        enums_addon.append(item)

    for identifier, d in importer_lib.items():
        item = (identifier, d['name'], d['description'], d['icon'], d['number'])
        enums_import.append(item)

    for identifier, d in exporter_lib.items():
        item = (identifier, d['name'], d['description'], d['icon'], d['number'])
        enums_export.append(item)

    enums.append(("", "Import", "Default blender build-in importer", "CUBE", 0), )
    enums += enums_import

    enums.append(("", "Export", "Default blender build-in exporter", "CUBE", 0), )
    enums += enums_export

    enums.append(("", "Import Blend", "Import Blend File", "BLENDER", 0), )

    return enums


def get_prop_args_by_idname(bl_idname: str):
    op = getattr(getattr(bpy.ops, 'wm'), 'alembic_import')

    s = str(op.idname).split(bl_idname)[-1]
    s = s[1:-2] + ','

    rule = r'(.*?)=(.*?),'

    res = re.findall(rule, s)
    prop_val = dict()

    for k, v in res:
        if v in {'True', 'False'}:
            v = eval(v)
        elif v.isdigit():
            v = eval(v)
        elif v == '""':
            v = ''

        prop_val[k] = v

    print(prop_val)


def get_operator_type():
    pass


class ConfigItemProperty(PropertyGroup):
    # USE
    use_config: BoolProperty(name='Use', default=True)
    # UI
    color_tag: EnumProperty(name='Color Tag',
                            items=enum_color_tag_items)
    # IO type
    io_type: EnumProperty(name='IO Type',
                          items=[('IMPORT', 'Import', '', 'IMPORT', 0), ('EXPORT', 'Export', '', 'EXPORT', 1)],
                          default='IMPORT')
    # information
    name: StringProperty(name='Preset Name', update=correct_name)
    description: StringProperty(name='Description',
                                description='Show in the popup operator tips')
    # extension
    extension: StringProperty(name='Extension')

    # custom import match rule
    ###############################
    match_rule: EnumProperty(name='Match Rule',
                             items=[('NONE', 'None (Default)', ''),
                                    ('STARTSWITH', 'Startswith', ''),
                                    ('ENDSWITH', 'Endswith', ''),
                                    ('IN', 'Contain', ''),
                                    ('REGEX', 'Regex (Match or not)', ''), ],
                             default='NONE', description='Matching rule of the name')

    match_value: StringProperty(name='Match Value', default='')

    # custom export temp path
    temporary_directory: StringProperty(name='Temporary Directory', subtype='DIR_PATH',
                                        description="Temporary Directory to store export files.\nIf empty, use blender's default temporary directory")

    # remove grease pencil from default because this design is only allow one default importer
    operator_type: EnumProperty(
        name='Operator Type',
        items=[
            ("", "Import", "Default blender build-in importer", "CUBE", 0),
            None,
            ('DEFAULT_DAE', 'Collada (.dae)', '', 'IMPORT', 99),
            ('DEFAULT_ABC', 'Alembic (.abc)', '', 'IMPORT', 98),
            ('DEFAULT_USD', 'USD (.usd/.usda/.usdc)', '', 'IMPORT', 97),
            ('DEFAULT_SVG', 'SVG (.svg)', '', 'GP_SELECT_POINTS', 96),
            ('DEFAULT_PLY', 'Stanford (.ply)', '', 'IMPORT', 95),
            ('DEFAULT_STL', 'Stl (.stl)', '', 'IMPORT', 94),
            ('DEFAULT_FBX', 'FBX (.fbx)', '', 'IMPORT', 93),
            ('DEFAULT_GLTF', 'glTF 2.0 (.gltf/.glb)', '', 'IMPORT', 92),
            ('DEFAULT_OBJ', 'Wavefront (.obj)', '', 'IMPORT', 91),
            ('DEFAULT_X3D', 'X3D (.x3d/.wrl)', '', 'IMPORT', 90),

            ("", "Export", "Default blender build-in exporter", "CUBE", 0),

            ('EXPORT_DAE', 'Collada (.dae)', '', 'EXPORT', 199),
            ('EXPORT_ABC', 'Alembic (.abc)', '', 'EXPORT', 198),
            ('EXPORT_USD', 'USD (.usd)', '', 'EXPORT', 197),
            ('EXPORT_USDC', 'USD (.usdc)', '', 'EXPORT', 196),
            ('EXPORT_USDA', 'USD (.usda)', '', 'EXPORT', 195),
            ('EXPORT_PLY', 'Stanford (.ply)', '', 'EXPORT', 194),
            ('EXPORT_STL', 'Stl (.stl)', '', 'EXPORT', 193),
            ('EXPORT_FBX', 'FBX (.fbx)', '', 'EXPORT', 192),
            ('EXPORT_GLTF', 'glTF 2.0 (.gltf)', '', 'EXPORT', 191),
            ('EXPORT_OBJ', 'Wavefront (.obj)', '', 'EXPORT', 190),
            ('EXPORT_SVG', 'Grease Pencil (.svg)', '', 'EXPORT', 189),
            None,
            ('EXPORT_BLEND', 'Blend (.blend)', '', 'BLENDER', 200),

            ("", "Import Blend", "Import Blend File", "BLENDER", 0),
            None,
            ('APPEND_BLEND_MATERIAL', 'Append All Materials', 'Append All', 'MATERIAL', 1),
            ('APPEND_BLEND_COLLECTION', 'Append All Collections', 'Append All',
             'OUTLINER_COLLECTION', 2),
            ('APPEND_BLEND_OBJECT', 'Append All Objects', 'Append All', 'OBJECT_DATA', 3),
            ('APPEND_BLEND_WORLD', 'Append All Worlds', 'Append All', 'WORLD', 4),
            ('APPEND_BLEND_NODETREE', 'Append All Node Groups', 'Append All', 'NODETREE', 5),

            None,
            ('LINK_BLEND_MAT', 'Link All Materials', 'Load All', 'MATERIAL', 11),
            ('LINK_BLEND_COLLECTION', 'Link All Collections', 'Load All',
             'OUTLINER_COLLECTION', 12),
            ('LINK_BLEND_OBJECT', 'Link All Objects', 'Load All', 'OBJECT_DATA',
             13),
            ('LINK_BLEND_WORLD', 'Link All Worlds', 'Load All', 'WORLD', 14),
            ('LINK_BLEND_NODE', 'Link All Node Groups', 'Load All', 'NODETREE',
             15),

            None,
            ('ADDONS_BLEND_MATERIAL', 'Append and Assign material',
             'Import material from a single file and assign it to active object', 'MATERIAL', 101),
            ('ADDONS_BLEND_WORLD', 'Append and Assign world',
             'Import world from a single file and set it as context world', 'WORLD', 102),

            ("", "Add-ons", "Custom operator and properties input", "USER", 0),
            # ('ADDONS_SVG', 'Grease Pencil (.svg)', '', 'GP_SELECT_STROKES', 100),

            None,
            ('ADDONS_INSTALL_ADDON', 'Install Addon (.py/.zip)',
             'Import and Install extra_addon', 'COMMUNITY', 103),

            ('ADDONS_IMPORT_IES', 'Import IES (.ies)', 'Import IES file as light', 'LIGHT_SPOT', 104),
            ('ADDONS_IMPORT_PBR_ZIP', 'Import PBR Material (.zip)', 'Import PBR Material', 'MATERIAL', 105),

            None,
            ('CUSTOM', 'Custom', '', 'USER', 666),
        ],
        default='DEFAULT_OBJ', )

    # custom operator
    bl_idname: StringProperty(name='Operator Identifier', update=correct_blidname)
    context: EnumProperty(name="Operator Context",
                          items=[("INVOKE_DEFAULT", "INVOKE_DEFAULT", ''),
                                 ("EXEC_DEFAULT", "EXEC_DEFAULT", ''), ],
                          default='EXEC_DEFAULT')
    context_area: EnumProperty(name="Area",
                               items=[
                                   ("VIEW_3D", "3D View", ''),
                                   ("IMAGE_EDITOR", "Image Editor", ''),
                                   ("NODE_EDITOR", "Node Editor", ''),
                               ],
                               default='VIEW_3D')
    prop_list: CollectionProperty(type=OperatorProperty)
    show_prop_list: BoolProperty(name='Properties', default=True)


def register():
    bpy.utils.register_class(OperatorProperty)
    bpy.utils.register_class(ConfigItemProperty)


def unregister():
    bpy.utils.unregister_class(OperatorProperty)
    bpy.utils.unregister_class(ConfigItemProperty)
