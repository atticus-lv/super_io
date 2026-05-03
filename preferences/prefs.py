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

from .. import __folder_name__
import rna_keymap_ui
from .data_config_store import get_config_data, get_config_list, set_config_index, write_runtime_config
from .operator_inspector import (
    default_property_value,
    get_operator_description,
    get_operator_label,
    iter_operator_properties,
    iter_registered_operators,
    operator_exists,
)


def get_pref():
    """get preferences of this plugin"""
    addon = bpy.context.preferences.addons.get(__folder_name__)
    if addon is not None:
        return addon.preferences
    return None


class OperatorPropAction:
    bl_label = "Operator Props Operate"
    bl_options = {'INTERNAL', 'UNDO'}

    config_list_index: IntProperty()
    prop_index: IntProperty()
    action = None

    def execute(self, context):
        item = get_config_list(context)[self.config_list_index]

        if self.action == 'ADD':
            item.prop_list.add()
        elif self.action == 'REMOVE':
            item.prop_list.remove(self.prop_index)

        write_runtime_config(context=context)
        return {'FINISHED'}


class SPIO_OT_OperatorPropAdd(OperatorPropAction, bpy.types.Operator):
    bl_idname = "wm.spio_operator_prop_add"
    bl_label = "Add Prop"

    action = 'ADD'


class SPIO_OT_OperatorPropRemove(OperatorPropAction, bpy.types.Operator):
    bl_idname = "wm.spio_operator_prop_remove"
    bl_label = "Remove Prop"

    action = 'REMOVE'


class SPIO_OT_OperatorSelector(bpy.types.Operator):
    bl_idname = "spio.operator_selector"
    bl_label = "Select Operator"
    bl_property = "enum_idname"
    bl_options = {'INTERNAL'}

    config_list_index: IntProperty()
    _enum_items = []

    def get_operator_items(self, context):
        enum_items = self.__class__._enum_items
        enum_items.clear()
        for bl_idname, label, description in iter_registered_operators():
            enum_items.append((bl_idname, f"{label} ({bl_idname})", description))
        return enum_items

    enum_idname: EnumProperty(name="Operator", items=get_operator_items)

    def execute(self, context):
        item = get_config_list(context)[self.config_list_index]
        item.bl_idname = self.enum_idname
        item.operator_type = "CUSTOM"
        if item.name == "" or item.name.startswith("Config"):
            item.name = get_operator_label(item.bl_idname)
        if item.description == "":
            item.description = get_operator_description(item.bl_idname)
        write_runtime_config(context=context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class SPIO_OT_OperatorPropertyAddFromRNA(bpy.types.Operator):
    bl_idname = "spio.operator_property_add_from_rna"
    bl_label = "Add from RNA Properties"
    bl_property = "property_name"
    bl_options = {'INTERNAL', 'UNDO'}

    config_list_index: IntProperty()
    _property_items = []

    def get_property_items(self, context):
        enum_items = self.__class__._property_items
        enum_items.clear()
        item = get_config_list(context)[self.config_list_index]
        existing = {prop.name for prop in item.prop_list}
        for prop in iter_operator_properties(item.bl_idname):
            identifier = prop["identifier"]
            if identifier in existing:
                continue
            enum_items.append((identifier, f"{prop['name']} ({identifier})", prop["description"]))
        if not enum_items:
            enum_items.append(("__NONE__", "No editable properties", ""))
        return enum_items

    property_name: EnumProperty(name="Property", items=get_property_items)

    def execute(self, context):
        if self.property_name == "__NONE__":
            return {'CANCELLED'}
        item = get_config_list(context)[self.config_list_index]
        prop_info = next(
            (prop for prop in iter_operator_properties(item.bl_idname) if prop["identifier"] == self.property_name),
            None,
        )
        prop_item = item.prop_list.add()
        prop_item.name = self.property_name
        prop_item.value = default_property_value(prop_info or {})
        write_runtime_config(context=context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class SPIO_OT_ConfigListAction:
    """Add / Remove / Copy current config"""
    bl_label = "Config Operate"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty()
    action = None

    def execute(self, context):
        config_data = get_config_data(context)
        config_list = config_data.config_list

        if self.action == 'ADD':
            new_item = config_list.add()
            new_item.name = f'Config{len(config_list)}'
            # correct index
            old_index = config_data.config_list_index
            new_index = len(config_list) - 1
            config_data.config_list_index = new_index

            for i in range(old_index, new_index - 1):
                bpy.ops.spio.config_list_move_up()

        elif self.action == 'REMOVE':
            config_list.remove(self.index)
            set_config_index(self.index - 1 if self.index != 0 else 0, context)

        elif self.action == 'COPY':
            src_item = config_list[self.index]

            new_item = config_list.add()

            for key in src_item.__annotations__.keys():
                value = getattr(src_item, key)
                if key != 'prop_list':
                    setattr(new_item, key, value)
            new_item.identifier = ''
            # prop list
            if len(src_item.prop_list) != 0:
                for prop_index, src_prop_item in enumerate(src_item.prop_list):
                    prop, value = src_prop_item.name, src_prop_item.value
                    # skip if the prop is not filled
                    if prop == '' or value == '': continue
                    prop_item = new_item.prop_list.add()
                    prop_item.name = prop
                    prop_item.value = value

            old_index = config_data.config_list_index
            new_index = len(config_list) - 1
            config_data.config_list_index = len(config_list) - 1

            for i in range(old_index, new_index - 1):
                bpy.ops.spio.config_list_move_up()

        write_runtime_config(context=context)
        return {'FINISHED'}


class SPIO_OT_ConfigListMove:
    bl_label = "Config Move"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty()
    action = None

    def execute(self, context):
        config_data = get_config_data(context)
        my_list = config_data.config_list
        index = config_data.config_list_index
        neighbor = index + (-1 if self.action == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index(context)
        write_runtime_config(context=context)

        return {'FINISHED'}

    def move_index(self, context):
        config_data = get_config_data(context)
        index = config_data.config_list_index
        new_index = index + (-1 if self.action == 'UP' else 1)
        config_data.config_list_index = max(0, min(new_index, len(config_data.config_list) - 1))


class SPIO_OT_ConfigListAdd(SPIO_OT_ConfigListAction, bpy.types.Operator):
    bl_idname = "spio.config_list_add"
    bl_label = "Add Config"

    action = 'ADD'


class SPIO_OT_ConfigListRemove(SPIO_OT_ConfigListAction, bpy.types.Operator):
    bl_idname = "spio.config_list_remove"
    bl_label = "Remove Config"

    action = 'REMOVE'


class SPIO_OT_ConfigListCopy(SPIO_OT_ConfigListAction, bpy.types.Operator):
    bl_idname = "spio.config_list_copy"
    bl_label = "Copy Config"

    action = 'COPY'


class SPIO_OT_ConfigListMoveUP(SPIO_OT_ConfigListMove, bpy.types.Operator):
    bl_idname = "spio.config_list_move_up"
    bl_label = 'Move Up'

    action = 'UP'


class SPIO_OT_ConfigListMoveDown(SPIO_OT_ConfigListMove, bpy.types.Operator):
    bl_idname = "spio.config_list_move_down"
    bl_label = 'Move Down'

    action = 'DOWN'


from .data_icon import get_color_tag_icon


class PREF_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        row.operator('spio.color_tag_selector', text='',
                     icon=get_color_tag_icon(int(item.color_tag[-1:]))).index = index
        row.prop(item, 'name', text='', emboss=False)
        row.prop(item, 'extension', text='', emboss=False, icon=item.io_type)
        row.prop(item, 'use_config', text='')

    def draw_filter(self, context, layout):
        pass

    def filter_items(self, context, data, propname):
        filter = context.window_manager.spio_filter

        items = getattr(data, propname)
        ordered = []

        filtered = [self.bitflag_filter_item] * len(items)

        for i, item in enumerate(items):
            if item.io_type == 'IMPORT' and not filter.show_import:
                filtered[i] &= ~self.bitflag_filter_item

        for i, item in enumerate(items):
            if item.io_type == 'EXPORT' and not filter.show_export:
                filtered[i] &= ~self.bitflag_filter_item

        ################################################
        if filter.filter_type == 'extension':
            for i, item in enumerate(items):
                if item.extension != filter.filter_extension and filter.filter_extension != '':
                    filtered[i] &= ~self.bitflag_filter_item

        elif filter.filter_type == 'match_rule':
            for i, item in enumerate(items):
                if item.match_rule != filter.filter_match_rule and filter.filter_match_rule != '':
                    filtered[i] &= ~self.bitflag_filter_item

        elif filter.filter_type == 'color_tag':
            for i, item in enumerate(items):
                if item.color_tag != filter.filter_color_tag and filter.filter_color_tag != '':
                    filtered[i] &= ~self.bitflag_filter_item

        elif filter.filter_type == 'name':
            for i, item in enumerate(items):
                if item.name != filter.filter_color_tag and filter.filter_name != '':
                    filtered[i] &= ~self.bitflag_filter_item

        # invert
        if filtered and filter.reverse:
            show_flag = self.bitflag_filter_item & ~self.bitflag_filter_item
            for i, bitflag in enumerate(filtered):
                if bitflag == show_flag:
                    filtered[i] = self.bitflag_filter_item
                else:
                    filtered[i] &= ~self.bitflag_filter_item
        try:
            ordered = bpy.types.UI_UL_list.sort_items_helper(items,
                                                             lambda i: len(getattr(i, filter.filter_type[7:]), True))
        except:
            pass

        return filtered, ordered


class SPIO_MT_ConfigIOMenu(bpy.types.Menu):
    bl_label = "Config Import/Export"
    bl_idname = "SPIO_MT_ConfigIOMenu"

    def draw(self, context):
        layout = self.layout
        layout.operator('spio.import_config', icon='IMPORT')
        layout.operator('spio.export_config', icon='EXPORT')
        layout.operator('spio.save_config', icon='FILE_TICK')


class NWPrincipledPreferences(bpy.types.PropertyGroup):
    base_color: StringProperty(
        name='Base Color',
        default='diffuse diff albedo base col color basecolor',
        description='Naming Components for Base Color maps')
    sss_color: StringProperty(
        name='Subsurface Color',
        default='sss subsurface',
        description='Naming Components for Subsurface Color maps')
    metallic: StringProperty(
        name='Metallic',
        default='metallic metalness metal mtl',
        description='Naming Components for metallness maps')
    specular: StringProperty(
        name='Specular',
        default='specularity specular spec spc',
        description='Naming Components for Specular maps')
    normal: StringProperty(
        name='Normal',
        default='normal nor nrm nrml norm',
        description='Naming Components for Normal maps')
    bump: StringProperty(
        name='Bump',
        default='bump bmp',
        description='Naming Components for bump maps')
    rough: StringProperty(
        name='Roughness',
        default='roughness rough rgh',
        description='Naming Components for roughness maps')
    gloss: StringProperty(
        name='Gloss',
        default='gloss glossy glossiness',
        description='Naming Components for glossy maps')
    displacement: StringProperty(
        name='Displacement',
        default='displacement displace disp dsp height heightmap',
        description='Naming Components for displacement maps')
    transmission: StringProperty(
        name='Transmission',
        default='transmission transparency',
        description='Naming Components for transmission maps')
    emission: StringProperty(
        name='Emission',
        default='emission emissive emit',
        description='Naming Components for emission maps')
    alpha: StringProperty(
        name='Alpha',
        default='alpha opacity',
        description='Naming Components for alpha maps')
    ambient_occlusion: StringProperty(
        name='Ambient Occlusion',
        default='ao ambient occlusion',
        description='Naming Components for AO maps')


def change_panel_category():
    from ..ui import ui_panel
    pref = get_pref()
    if pref is None:
        return

    for panel in ui_panel.panels:
        if "bl_rna" not in panel.__dict__:
            panel.bl_category = pref.category
        else:
            bpy.utils.unregister_class(panel)
            panel.bl_category = pref.category
            bpy.utils.register_class(panel)


def update_category(self, context):
    try:
        change_panel_category()

    except(Exception) as e:
        self.report({'ERROR'}, f'Category change failed:\n{e}')


from .data_config_prop import ConfigItemProperty


class SPIO_Preference(bpy.types.AddonPreferences):
    bl_idname = __folder_name__

    # Tab
    ui: EnumProperty(name='UI', items=[
        ('SETTINGS', 'Settings', '', 'PREFERENCES', 0),
        ('CONFIG', 'Config', '', 'PRESET', 1),
    ], default='CONFIG')
    settings_ui: EnumProperty(name='UI', items=[
        ('IO', 'IO', '', 'FILE_CACHE', 0),
        ('UI', 'User Interface', '', 'WINDOW', 1),
        ('KEYMAP', 'Keymap', '', 'KEYINGSET', 2),
        ('ADDONS', 'Addons', '', 'EXPERIMENTAL', 3),
        ('URL', 'Url', '', 'HELP', 4),

    ], default='IO')

    category: StringProperty(name="Category", default="SPIO", update=update_category)

    # Settings
    force_unicode: BoolProperty(name='Force Unicode',
                                description="Force to use 'utf-8' to decode filepath \nOnly enable when your system coding 'utf-8'",
                                default=False)
    # addon
    asset_helper: BoolProperty(name='Asset Helper', default=True)
    # asset helper batch import pbr tags
    show_principled_lists: BoolProperty(name='Show Principled naming tags', default=False)
    principled_tags: bpy.props.PointerProperty(type=NWPrincipledPreferences)

    experimental: BoolProperty(name='Experimental', default=False)

    # Export
    extend_export_menu: BoolProperty(name='Extend Export Menu', default=False)

    post_open_dir: BoolProperty(name='Open Dir After Export',
                                description='Open the target directory after export', default=False)
    post_push_to_clipboard: BoolProperty(name='Copy After Export',
                                         description='Copy files to clipboard after export models / images (Mac Only Support One file)',
                                         default=True)

    # UI
    report_time: BoolProperty(name='Report Time',
                              description='Report import time', default=True)

    disable_warning_rules: BoolProperty(name='Close Warning Rules', default=False)
    # Preset
    config_list: CollectionProperty(type=ConfigItemProperty)
    config_list_index: IntProperty(min=0, default=0)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop(self, 'ui', expand=True)

        row.separator(factor=1)
        row.menu(SPIO_MT_ConfigIOMenu.bl_idname, text='', icon='FILE_TICK')

        row.separator(factor=1)

        col = layout.column()
        if self.ui == 'SETTINGS':
            self.draw_settings(context, col)

        elif self.ui == 'CONFIG':
            self.draw_config(context, col)

    def draw_url(self, context, layout):
        box = layout.box()
        box.label(text='Help', icon='QUESTION')
        row = box.row()
        box.operator('wm.url_open', text='Manual', icon='URL').url = 'http://atticus-lv.gitee.io/super_io/#/'

        box = layout.box()
        box.label(text='Sponsor: 只剩一瓶辣椒酱', icon='FUND')
        box.operator('wm.url_open', text='斑斓魔法CG官网', icon='URL').url = 'https://www.blendermagic.cn/'
        box.row(align=True).operator('wm.url_open', text='辣椒B站频道',
                                     icon='URL').url = 'https://space.bilibili.com/35723238'

        box.label(text='Developer: Atticus', icon='SCRIPT')
        box.operator('wm.url_open', text='Atticus Github', icon='URL').url = 'https://github.com/atticus-lv'
        box.row(align=True).operator('wm.url_open', text='AtticusB站频道',
                                     icon='URL').url = 'https://space.bilibili.com/1509173'

    def draw_addons(self, context, layout):
        box = layout.box()
        box.label(text='Addons', icon='EXPERIMENTAL')
        box.prop(self, 'asset_helper')
        box.prop(self, 'experimental')

        box = layout.box()
        box.label(text='Third-party', icon='SCRIPT')
        box.operator('spio.copy_c4d_plugin', icon='EVENT_C')
        box.operator('spio.copy_houdini_script', icon='EVENT_H')
        box.label(text='Support Paste Vector Patterns copied from Illustrator', icon='EVENT_A')
        box.label(text='Support Paste Selection copied from Photoshop', icon='EVENT_P')

        # box.label(text= 'Extra')
        # box.operator('wm.url_open', text='import_3dm by jesterKing', icon='URL').url = 'https://github.com/jesterKing/import_3dm'

    def draw_settings(self, context, layout):
        s = layout.row(align=False)
        col = s.column(align=True)
        col.scale_x = 1.5
        col.scale_y = 1.5
        col.prop(self, 'settings_ui', expand=True, text='')

        col = s.column(align=True).box()
        col.use_property_split = True

        def draw_io():
            #### Import ####
            box = col.box()
            box.label(text='Import', icon="IMPORT")
            row = box.row(align=True)
            row.alert = True
            row.prop(self, 'force_unicode', text='')
            row.label(text='Force Unicode')

            #### PBR Tags ####
            box = box.box()
            subcol = box.column(align=True)
            subcol.use_property_split = False
            subcol.prop(self, 'show_principled_lists',
                        icon='TRIA_RIGHT' if not self.show_principled_lists else 'TRIA_DOWN', emboss=False)
            subcol.separator()
            if self.show_principled_lists:
                tags = self.principled_tags

                subcol.prop(tags, "base_color")
                subcol.prop(tags, "sss_color")
                subcol.prop(tags, "metallic")
                subcol.prop(tags, "specular")
                subcol.prop(tags, "rough")
                subcol.prop(tags, "gloss")
                subcol.prop(tags, "normal")
                subcol.prop(tags, "bump")
                subcol.prop(tags, "displacement")
                subcol.prop(tags, "transmission")
                subcol.prop(tags, "emission")
                subcol.prop(tags, "alpha")
                subcol.prop(tags, "ambient_occlusion")

            #### Export ####

            box = col.box()
            box.label(text='Export', icon="EXPORT")
            row = box.row(align=True)
            row.prop(context.preferences.filepaths, 'temporary_directory', text="Temporary Files")

            row = box.row(align=True)
            row.prop(self, 'extend_export_menu')

            row = box.row(align=True)
            row.prop(self, 'post_open_dir')

            row = box.row(align=True)
            row.prop(self, 'post_push_to_clipboard')

        def draw_ui():
            box = col.box()
            box.label(text='User Interface', icon='WINDOW')

            row = box.row(align=True)
            row.prop(self, 'category')

            row = box.row(align=True)
            row.prop(self, 'report_time', text='')
            row.label(text='Report Time')

            row = box.row(align=True)
            row.prop(self, 'disable_warning_rules', text='')
            row.label(text='Close Warning Rules')

        if self.settings_ui == 'IO':
            draw_io()
        elif self.settings_ui == 'UI':
            draw_ui()
        elif self.settings_ui == 'KEYMAP':
            self.draw_keymap(context, col)
        elif self.settings_ui == 'ADDONS':
            self.draw_addons(context, col)
        elif self.settings_ui == 'URL':
            self.draw_url(context, col)

    def draw_keymap(self, context, layout):
        col = layout.box().column()
        col.label(text="Keymap", icon="KEYINGSET")
        km = None
        wm = context.window_manager
        kc = wm.keyconfigs.user

        old_km_name = ""
        get_kmi_l = []

        from .data_keymap import addon_keymaps

        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname and kmi_add.name == kmi_con.name:
                    get_kmi_l.append((km, kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                col.label(text=str(km.name), icon="DOT")

            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

            old_km_name = km.name

    def draw_config(self, context, layout):
        config_data = get_config_data(context)
        config_index = config_data.config_list_index

        row = layout.column().row(align=False)
        row.alignment = 'CENTER'

        row.scale_y = 1.25
        row.scale_x = 1.5

        row.menu(SPIO_MT_ConfigIOMenu.bl_idname, text='', icon='FILE_TICK')
        # filter panel
        filter = context.window_manager.spio_filter
        if filter.filter_type == 'extension':
            row.prop(filter, 'filter_extension', text="", icon='VIEWZOOM')
        elif filter.filter_type == 'name':
            row.prop(filter, "filter_name", text="", icon='VIEWZOOM')
        elif filter.filter_type == 'match_rule':
            row.prop(filter, "filter_match_rule", icon='SHORTDISPLAY', text='')
        elif filter.filter_type == 'color_tag':
            row.prop(filter, 'filter_color_tag', expand=True)

        row.popover(panel="SPIO_PT_ListFilterPanel", icon="FILTER", text='')

        # split left and right
        row = layout.column(align=True).row()
        row_left = row

        row_l = row_left.row(align=False)
        col_list = row_l.column(align=True)
        col_btn = row_l.column(align=True)

        col_list.template_list(
            "PREF_UL_ConfigList", "Config List",
            config_data, "config_list",
            config_data, "config_list_index")

        col_btn.operator('spio.config_list_add', text='', icon='ADD')

        d = col_btn.operator('spio.config_list_remove', text='', icon='REMOVE')
        d.index = config_index

        col_btn.separator()

        col_btn.operator('spio.config_list_move_up', text='', icon='TRIA_UP')
        col_btn.operator('spio.config_list_move_down', text='', icon='TRIA_DOWN')

        col_btn.separator()

        c = col_btn.operator('spio.config_list_copy', text='', icon='DUPLICATE')
        c.index = config_index

        if len(config_data.config_list) == 0: return
        item = config_data.config_list[config_index]
        if not item: return

        col = layout.column()
        box = col.box().column()
        box.label(text=item.name, icon='EDITMODE_HLT')

        box.use_property_split = True
        box1 = box.box()

        row = box1.row(align=True)
        row.prop(item, 'io_type', expand=True)

        box1.prop(item, 'name')
        box1.prop(item, 'description')

        f = box1
        f.alert = (item.extension == '')
        f.prop(item, 'extension')

        if item.io_type == 'IMPORT':
            box2 = box.box()
            box2.prop(item, 'match_rule')
            if item.match_rule != 'NONE':
                box2.prop(item, 'match_value', text='Match Value' if item.match_rule != 'REGEX' else 'Expression')
                if not self.disable_warning_rules:
                    box3 = box2.box().column(align=True)
                    box3.alert = True
                    sub_row = box3.row()
                    sub_row.label(text="Warning", icon='ERROR')
                    sub_row.prop(self, 'disable_warning_rules', toggle=True)
                    box4 = box3
                    # box4.alert = False
                    box4.label(text="1. If file name not matching this rule")
                    box4.label(text="   It will search for the next config which match")
                    box4.label(text="2. If no config’s rule is matched")
                    box4.label(
                        text="   It will popup all available importer in a menu after import all file that match a rule")

        elif item.io_type == 'EXPORT':
            box2 = box.box()
            box2.prop(item, 'temporary_directory')

        box3 = box.box()
        box3.alert = not operator_exists(item.bl_idname)
        box3.label(text=get_operator_label(item.bl_idname), icon='TOOL_SETTINGS')
        row = box3.row(align=True)
        row.prop(item, 'bl_idname')
        selector = row.operator('spio.operator_selector', text='', icon='VIEWZOOM')
        selector.config_list_index = config_index

        if item.bl_idname == '':
            box3.label(text='No Operator Found', icon='ERROR')
        elif not operator_exists(item.bl_idname):
            box3.label(text=f'Operator "{item.bl_idname}" is not registered', icon='ERROR')

        box3.prop(item, 'context')

        # context area
        if get_pref().experimental:
            box3.prop(item, 'context_area')

        col = box3.box().column()
        col.use_property_split = False
        row = col.row(align=False)
        row.prop(item, 'show_prop_list', icon='TRIA_DOWN' if item.show_prop_list else 'TRIA_RIGHT', emboss=False)
        row.operator('spio.read_preset', icon='PRESET').bl_idname_input = item.bl_idname
        prop_selector = row.operator('spio.operator_property_add_from_rna', text='', icon='ADD')
        prop_selector.config_list_index = config_index

        if item.bl_idname != '' and item.show_prop_list:

            row = col.row()
            if len(item.prop_list) != 0:
                row.label(text='Property')
                row.label(text='Value')

            for prop_index, prop_item in enumerate(item.prop_list):
                row = col.row()
                row.prop(prop_item, 'name', text='')
                row.prop(prop_item, 'value', text='')

                d = row.operator('wm.spio_operator_prop_remove', text='', icon='PANEL_CLOSE', emboss=False)
                d.config_list_index = config_index
                d.prop_index = prop_index
            col.separator()
            row = col.row(align=False)
            d = row.operator('wm.spio_operator_prop_add', text='Add Property', icon='ADD', emboss=False)
            d.config_list_index = config_index


class SPIO_PT_ListFilterPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_category = ''
    bl_label = "Filter Type"
    bl_idname = "SPIO_PT_ListFilterPanel"

    def draw(self, context):
        """UI code for the filtering/sorting/search area."""
        filter = context.window_manager.spio_filter
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(filter, 'show_import')
        layout.prop(filter, 'show_export')

        col = layout.column(align=True)
        col.prop(filter, 'filter_type', icon='FILTER', expand=True)

        layout.prop(filter, "reverse")


classes = [
    SPIO_PT_ListFilterPanel,

    SPIO_OT_OperatorPropAdd, SPIO_OT_OperatorPropRemove,
    SPIO_OT_OperatorSelector, SPIO_OT_OperatorPropertyAddFromRNA,

    SPIO_OT_ConfigListAdd, SPIO_OT_ConfigListRemove, SPIO_OT_ConfigListCopy, SPIO_OT_ConfigListMoveUP,
    SPIO_OT_ConfigListMoveDown,

    PREF_UL_ConfigList,
    SPIO_MT_ConfigIOMenu,
    NWPrincipledPreferences,
    SPIO_Preference
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    try:
        change_panel_category()

    except(Exception) as e:
        print(e)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
