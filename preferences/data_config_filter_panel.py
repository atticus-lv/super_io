import bpy
from bpy.props import (EnumProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)
from bpy.types import PropertyGroup
from .prefs import get_pref
from .data_config_prop import enum_color_tag_items
from .data_icon import get_color_tag_icon

class ConfigListFilterProperty(PropertyGroup):
    filter_type: EnumProperty(name='Filter Type', items=[
        ('name', 'Name', ''),
        ('extension', 'Extension', ''),
        ('match_rule', 'Match Rule', ''),
        ('color_tag', 'Color Tag', ''),
    ], default='name')
    filter_name: StringProperty(default='', name="Name")

    filter_extension: StringProperty(default='', name="Extension")

    filter_match_rule: EnumProperty(name='Match Rule',
                                    items=[('NONE', 'None (Default)', ''),
                                           ('STARTSWITH', 'Startswith', ''),
                                           ('ENDSWITH', 'Endswith', ''),
                                           ('IN', 'Contain', ''),
                                           ('REGEX', 'Regex (Match or not)', ''), ],
                                    default='NONE', description='Matching rule of the name')

    filter_color_tag: EnumProperty(name='Color Tag',
                                   items=enum_color_tag_items)

    reverse: BoolProperty(name="Reverse", default=False,
                          options=set(),
                          description="Reverse", )

    show_import: BoolProperty(name='Show Import', default=True)
    show_export: BoolProperty(name='Show Export', default=True)


class SPIO_OT_color_tag_selector(bpy.types.Operator):
    bl_idname = 'spio.color_tag_selector'
    bl_label = 'Color Tag'

    index: IntProperty(name='Config list Index')

    dep_classes = []

    @classmethod
    def poll(cls, context):
        return len(get_pref().config_list) != 0

    def execute(self, context):
        # clear
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)
        self.dep_classes.clear()

        pref = get_pref()
        item = pref.config_list[self.index]

        for i in range(0, 9):
            # set color tag
            def execute(self, context):
                self.item.color_tag = f'COLOR_0{self.index}'
                context.area.tag_redraw()
                return {'FINISHED'}

            # define
            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_color_tag_{i}',
                           "bl_label": 'Select',
                           "bl_description": f'Color {i}',
                           "execute": execute,
                           # custom pass in
                           'index': i,
                           'item': item, },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        def draw(cls, context):
            layout = cls.layout
            row = cls.layout.row(align=True)
            row.scale_x = 1.12
            for i in range(0, 9):
                row.operator(f'wm.spio_color_tag_{i}', text='',
                             icon=get_color_tag_icon(i))

        context.window_manager.popup_menu(draw, title="Color", icon='OUTLINER_COLLECTION' if bpy.app.version > (
            2, 93, 0) else 'COLORSET_13_VEC')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ConfigListFilterProperty)
    bpy.utils.register_class(SPIO_OT_color_tag_selector)

    bpy.types.WindowManager.spio_filter = PointerProperty(type=ConfigListFilterProperty)


def unregister():
    bpy.utils.unregister_class(ConfigListFilterProperty)
    bpy.utils.unregister_class(SPIO_OT_color_tag_selector)

    del bpy.types.WindowManager.spio_filter
