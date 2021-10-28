import os
import time
import subprocess

import bpy
from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from ..clipboard.wintypes import WintypesClipboard as Clipboard
from .utils import ConfigHelper, MeasureTime, ConfigItemHelper
from .utils import is_float, get_pref, convert_value

from ..ui.icon_utils import RSN_Preview

import_icon = RSN_Preview(image='import.bip', name='import_icon')


class TEMP_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        row.prop(item, 'name', text='', emboss=False)
        row.prop(item, 'bl_idname', text='', emboss=False)

    def draw_filter(self, context, layout):
        # hide to prevent edit by user
        pass

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        ordered = []
        filtered = [self.bitflag_filter_item] * len(items)

        # get current filter extension
        ext = context.scene.spio_ext

        for i, item in enumerate(items):
            if item['extension'] == ext:
                filtered[i] &= ~self.bitflag_filter_item

        if filtered:
            show_flag = self.bitflag_filter_item & ~self.bitflag_filter_item
            for i, bitflag in enumerate(filtered):
                if bitflag == show_flag:
                    filtered[i] = self.bitflag_filter_item
                else:
                    filtered[i] &= ~self.bitflag_filter_item
        try:
            ordered = bpy.types.UI_UL_list.sort_items_helper(items, lambda i: len(i['extension' == ext]),
                                                             True)
        except:
            pass

        return filtered, ordered


class SuperImport(bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # dependant
    dep_classes = []
    # data
    clipboard = None
    file_list = []
    CONFIGS = None
    ext = ''
    # action
    load_image_as_plane = False
    # state
    use_custom_config = False
    config_list_index: IntProperty(name='Active Index')
    # UI
    show_urls: BoolProperty(default=False, name='Show Files')
    show_property: BoolProperty(default=False, name='Edit Property')

    # draw panel
    ############
    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        row = layout.row()
        row.alignment = "LEFT"
        row.prop(self, 'show_urls', text=f'Import {len(self.file_list)} {self.ext} Object',
                 icon_value=import_icon.get_image_icon_id(), emboss=False)
        row.separator()
        row.prop(self, 'update')

        if self.show_urls:
            col = layout.column(align=True)
            for file_path in self.file_list:
                col.label(text=str(file_path))

        layout.template_list(
            "TEMP_UL_ConfigList", "Config List",
            pref, "config_list",
            self, "config_list_index", rows=4)

        item = pref.config_list[self.config_list_index]

        box = layout.box().split().column()

        row = box.split(factor=0.25)
        row.prop(self, 'show_property', icon='TRIA_DOWN' if self.show_property else "TRIA_RIGHT", emboss=False,
                 text=item.name)
        row = row.row(align=True)

        row.label(text=item.description)
        c = row.operator('spio.config_list_copy', text='', icon='DUPLICATE')
        c.index = self.config_list_index

        if not self.show_property: return

        if item.bl_idname != '':
            row = box.row()
            if len(item.prop_list) != 0:
                row.label(text='Property')
                row.label(text='Value')
            for prop_index, prop_item in enumerate(item.prop_list):
                row = box.row()
                row.prop(prop_item, 'name', text='')
                row.prop(prop_item, 'value', text='')

                d = row.operator('wm.spio_operator_prop_remove', text='', icon='PANEL_CLOSE', emboss=False)
                d.config_list_index = self.config_list_index
                d.prop_index = prop_index

        row = box.row(align=True)
        row.alignment = 'LEFT'
        d = row.operator('wm.spio_operator_prop_add', text='Add Property', icon='ADD', emboss=False)
        d.config_list_index = self.config_list_index

    def restore(self):
        self.file_list.clear()
        self.clipboard = None
        self.ext = None

    # Pre
    ############
    def invoke(self, context, event):
        self.restore()

        # get Clipboard
        self.clipboard = Clipboard()
        self.file_list = self.clipboard.push(force_unicode=get_pref().force_unicode)

        del self.clipboard  # release clipboard

        if len(self.file_list) == 0:
            self.report({"ERROR"}, "No file found in clipboard")
            return {"CANCELLED"}

        for file_path in self.file_list:
            extension = file_path.split('.')[-1].lower()
            if self.ext is None:
                self.ext = extension
            elif self.ext != extension:
                self.report({"ERROR"}, "Only one type of file can be imported at a time")
                return {"CANCELLED"}

        # set extension filter for ui panel
        context.scene.spio_ext = self.ext

        self.CONFIGS = ConfigHelper(check_use=True, filter=context.scene.spio_ext)
        config_list, index_list = self.CONFIGS.config_list, self.CONFIGS.index_list

        # import default if not custom config for this file extension
        if self.CONFIGS.is_empty():
            self.use_custom_config = False

            if self.ext == 'blend':
                self.import_blend_default(context)
                return {'FINISHED'}
            else:
                return self.execute(context)

        self.use_custom_config = True
        # set default index to prevent default index is not in the filter list ui
        self.config_list_index = index_list[0]

        # when there is only one config, regard it as the default setting
        if self.CONFIGS.is_only_one_config():
            return self.execute(context)

        # when there is more than one config, set up a panel / menu for user to select
        elif self.CONFIGS.is_more_than_one_config():
            self.config_list_index = index_list[0]
            if get_pref().import_style == 'PANEL':
                return context.window_manager.invoke_props_dialog(self, width=450)
            return self.import_custom_dynamic(context)

    def execute(self, context):
        with MeasureTime() as start_time:
            if self.use_custom_config is False:
                self.import_default()
            else:
                self.import_custom()

            self.report_time(start_time)

        return {"FINISHED"}

    def report_time(self, start_time):
        if get_pref().report_time: self.report({"INFO"},
                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

    # menu
    ##############
    def import_custom_dynamic(self, context):
        # clear
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)
        self.dep_classes.clear()

        file_list = self.file_list

        for index in self.CONFIGS.index_list:
            # set config for register
            config_item = get_pref().config_list[index]

            # dynamic operator
            ##################
            def execute(self, context):
                # use pre-define index to call config
                config_item = get_pref().config_list[self.idx]
                bl_idname = config_item.bl_idname
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

                ops_args = dict()

                for prop_item in config_item.prop_list:
                    prop, value = prop_item.name, prop_item.value
                    if prop == '' or value == '': continue
                    ops_args[prop] = convert_value(value)

                if op_callable:
                    with MeasureTime() as start_time:
                        for file_path in file_list:
                            ops_args['filepath'] = file_path
                            try:
                                op_callable(**ops_args)
                            except Exception as e:
                                self.report({"ERROR"}, str(e))

                        if get_pref().report_time: self.report({"INFO"},
                                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
                else:
                    self.report({"ERROR"}, f'{op_callable} Error!!!')

                return {"FINISHED"}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": config_item.name,
                           "bl_description": config_item.description,
                           "execute": execute,
                           # custom
                           'idx': index,
                           'CONFIG': self.CONFIGS, },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        # set draw menu
        import_op = self

        def draw_custom_menu(self, context):
            for cls in import_op.dep_classes:
                self.layout.operator(cls.bl_idname)

        context.window_manager.popup_menu(draw_custom_menu, title=f'Super Import {self.ext.upper()}',
                                          icon='FILEBROWSER')

        return {'FINISHED'}

    def import_blend_default(self, context):
        from ..loader.default_blend import blend_lib

        path = self.file_list[0]
        join_paths = '$$'.join(self.file_list)

        def draw_blend_menu(cls, context):
            pref = get_pref()
            layout = cls.layout
            layout.operator_context = "INVOKE_DEFAULT"
            # only one blend need to deal with
            if len(self.file_list) == 1:
                open = layout.operator('wm.spio_open_blend', icon='FILEBROWSER')
                open.filepath = path

                open = layout.operator('wm.spio_open_blend_extra', icon='ADD')
                open.filepath = path

                if pref.simple_blend_menu:
                    layout.operator('wm.spio_append_blend', icon='APPEND_BLEND')
                    layout.operator('wm.spio_link_blend', icon='LINK_BLEND')
                    return None

                col = layout.column()

                col.separator()
                col.operator('wm.spio_append_blend', icon='APPEND_BLEND')
                for dir, lib in blend_lib.items():
                    op = col.operator('wm.spio_append_blend', text=dir)
                    op.filepath = path
                    op.sub_path = dir
                    op.data_type = lib

                col.separator()
                col.operator('wm.spio_link_blend', icon='LINK_BLEND')
                for dir, lib in blend_lib.items():
                    op = col.operator('wm.spio_link_blend', text=dir)
                    op.filepath = path
                    op.sub_path = dir
                    op.data_type = lib

            else:
                col = layout.column()
                op = col.operator('wm.spio_batch_import_blend', text=f'Batch Open')
                op.action = 'OPEN'
                op.files = join_paths

                for dir, lib in blend_lib.items():
                    op = col.operator('wm.spio_batch_import_blend', text=f'Batch Append {dir}')
                    op.action = 'APPEND'
                    op.files = join_paths
                    op.sub_path = dir
                    op.data_type = lib

                col.separator()
                for dir, lib in blend_lib.items():
                    op = col.operator('wm.spio_batch_import_blend', text=f'Batch Link {dir}')
                    op.action = 'LINK'
                    op.files = join_paths
                    op.sub_path = dir
                    op.data_type = lib

        context.window_manager.popup_menu(draw_blend_menu,
                                          title=f'Super Import Blend ({len(self.file_list)} files)',
                                          icon='FILE_BLEND')

    # Advance Panel
    ################
    def import_custom(self):
        """import users' custom configs"""
        config_item = get_pref().config_list[self.config_list_index]
        ITEM = ConfigItemHelper(config_item)

        # get match rule, if rule is match, execute the operator, else popup menu/panel
        match_rule = ITEM.match_rule
        rule = ITEM.rule
        operator_type = ITEM.operator_type

        # default operator

        # custom operator
        bl_idname = ITEM.bl_idname
        op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
        ops_args = ITEM.prop_list

        if op_callable:
            for file_path in self.file_list:
                ops_args['filepath'] = file_path
                try:
                    op_callable(**ops_args)
                except Exception as e:
                    self.report({"ERROR"}, str(e))

    def import_default(self):
        """Import with blender's default setting"""
        pass


from ..loader.default_importer import default_model_import_dict as model


class VIEW3D_OT_SuperImport(SuperImport):
    """Load files/models/images from clipboard
Allow to load one format at the same time
Support batch load all models/images (Alt click to call import image as plane)
Blend file is only allow to load only one(as library)"""
    bl_idname = "view3d.spio_import"
    bl_label = "Super Import View3D"

    @classmethod
    def poll(_cls, context):
        if context.area.type == "VIEW_3D":
            return context.area.ui_type == "VIEW_3D" and context.mode == "OBJECT"

    def import_default(self):
        ext = self.ext
        unregister_list = list()

        for file_path in self.file_list:
            if ext in model:
                bl_idname = model.get(ext)
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
                op_callable(filepath=file_path)
            else:
                pass

        # if len(unregister_list) !=0 :
        #
        #     def draw_img_menu(self,context):
        #         layout = self.layout
        #         layout.operator('object.load_reference_image').filepath =
        #         pass
        #
        #     bpy.context.window_manager.popup_menu(draw_img_menu,
        #                                       title=f'Super Import Blend ({len(self.file_list)} files)',
        #                                       icon='FILE_BLEND')
        #
        #     bpy.ops.object.load_reference_image(filepath=file_path)


class NODE_OT_SuperImport(SuperImport):
    """Load files/images from clipboard
Allow to load one format at the same time"""
    bl_idname = "node.spio_import"
    bl_label = "Super Import ShaderNodeTree"

    @classmethod
    def poll(_cls, context):
        return (
                context.area.type == "NODE_EDITOR"
                and context.area.ui_type in {'GeometryNodeTree', "ShaderNodeTree"}
                and context.space_data.edit_tree is not None
        )

    def import_default(self):
        nt = bpy.context.space_data.edit_tree
        location_X, location_Y = bpy.context.space_data.cursor_location

        if bpy.context.area.ui_type == 'ShaderNodeTree':
            node_type = 'ShaderNodeTexImage'
        elif bpy.context.area.ui_type == 'GeometryNodeTree':
            node_type = 'GeometryNodeImageTexture'

        for file_path in self.file_list:
            tex_node = nt.nodes.new(node_type)
            tex_node.location = location_X, location_Y
            # tex_node.hide = True
            location_Y += 250

            path = file_path
            image_name = os.path.basename(path)
            image = bpy.data.images.get(image_name) if image_name in bpy.data.images else bpy.data.images.load(
                filepath=path)

            if node_type == 'ShaderNodeTexImage':
                tex_node.image = image
            elif node_type == 'GeometryNodeImageTexture':
                tex_node.inputs['Image'].default_value = image


def file_context_menu(self, context):
    layout = self.layout
    layout.operator('view3d.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def node_context_menu(self, context):
    layout = self.layout
    layout.operator('node.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def register():
    import_icon.register()

    bpy.utils.register_class(TEMP_UL_ConfigList)
    bpy.utils.register_class(VIEW3D_OT_SuperImport)
    bpy.utils.register_class(NODE_OT_SuperImport)

    # Global ext
    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')
    # Menu append
    bpy.types.NODE_MT_context_menu.prepend(node_context_menu)


def unregister():
    import_icon.unregister()

    bpy.types.NODE_MT_context_menu.remove(node_context_menu)

    bpy.utils.unregister_class(TEMP_UL_ConfigList)
    bpy.utils.unregister_class(VIEW3D_OT_SuperImport)
    bpy.utils.unregister_class(NODE_OT_SuperImport)
