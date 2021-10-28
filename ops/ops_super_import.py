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
from ..loader.default_importer import model_lib
from ..loader.default_blend import blend_lib

import_icon = RSN_Preview(image='import.bip', name='import_icon')


class SuperImport(bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # dependant class
    #################
    dep_classes = []  # for easier manage, helpful for batch register and un register

    # data
    #################
    clipboard = None  # clipboard data
    file_list = []  # store clipboard urls for importing
    CONFIGS = None  # config list from user preference
    ext = ''  # only support one file extension at a time, set as global parm

    # state
    ###############
    use_custom_config = False  # if there is more then one config that advance user define
    config_list_index: IntProperty()  # index for reading pref config list

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

        self.CONFIGS = ConfigHelper(check_use=True, filter=self.ext)
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

        # when there is more than one config, set up a  menu for user to select
        elif self.CONFIGS.is_more_than_one_config():
            self.config_list_index = index_list[0]
            return self.import_custom_dynamic(context)

    def execute(self, context):
        with MeasureTime() as start_time:
            if self.use_custom_config is False:
                self.import_default(context)
            else:
                self.import_custom(context)

            self.report_time(start_time)

        return {"FINISHED"}

    def report_time(self, start_time):
        if get_pref().report_time: self.report({"INFO"},
                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

    # menu
    ##############
    def import_custom_dynamic(self, context):
        # unregister_class
        for cls in self.dep_classes:
            bpy.utils.unregister_class(cls)
        self.dep_classes.clear()

        # no match list
        file_list = self.file_list
        # match dict
        match_file_op_dict = dict()
        # match index :exclude from popup importer
        match_index_list = list()

        for index in self.CONFIGS.index_list:
            # set config for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)
            match_rule = ITEM.match_rule
            rule = ITEM.rule

            if match_rule == 'NONE':
                match_files = list()
            elif match_rule == 'STARTSWITH':
                match_files = [file for file in file_list if os.path.basename(file).startswith(rule)]
            elif match_rule == 'ENDSWITH':
                match_files = [file for file in file_list if
                               os.path.basename(file).removesuffix('.' + self.ext).endswith(rule)]
            elif match_rule == 'IN':
                match_files = [file for file in file_list if os.path.basename(file) in rule]
            elif match_rule == 'REGEX':
                import re
                match_files = [file for file in file_list if re.search(rule, os.path.basename(file))]

            if len(match_files) > 0:
                for file in match_files:
                    match_file_op_dict[file] = ITEM
                match_index_list.append(index)

        print(match_file_op_dict, match_index_list, file_list)
        # dynamic operator
        ##################
        for index in self.CONFIGS.index_list:
            if index in match_index_list: continue  # not register those match config
            # only for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)

            # define exec
            def execute(self, context):
                # use pre-define index to call config
                ITEM = self.ITEM

                op_callable, ops_args = ITEM.get_operator_and_args()

                if op_callable:
                    with MeasureTime() as start_time:
                        for file_path in file_list:
                            if file_path in match_file_op_dict: continue
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
                           "bl_label": ITEM.name,
                           "bl_description": ITEM.description,
                           "execute": execute,
                           # custom pass in
                           'ITEM': ITEM, },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        ############################
        # execute
        ############################

        # first import all matching rule files
        if len(match_file_op_dict) > 0:
            with MeasureTime() as start_time:
                for filepath, item_helper in match_file_op_dict.items():
                    op_callable, ops_args = item_helper.get_operator_and_args()
                    ops_args['filepath'] = filepath
                    try:
                        op_callable(**ops_args)
                    except Exception as e:
                        self.report({"ERROR"}, str(e))

                if get_pref().report_time: self.report_time(start_time)
        # then popup menu to select the remain not matching file
        remain = len(file_list) - len(match_file_op_dict)
        if len(self.dep_classes) > 0 and remain > 0:
            # set draw menu
            import_op = self

            def draw_custom_menu(self, context):
                self.layout.label(text=f'Remain {remain} files')
                for cls in import_op.dep_classes:
                    self.layout.operator(cls.bl_idname)

            context.window_manager.popup_menu(draw_custom_menu, title=f'Super Import {self.ext.upper()}',
                                              icon='FILEBROWSER')

        return {'FINISHED'}

    def import_blend_default(self, context):

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
    def import_custom(self, context):
        """import users' custom configs"""
        config_item = get_pref().config_list[self.config_list_index]
        ITEM = ConfigItemHelper(config_item)

        # get match rule, if rule is match, execute the operator, else popup menu/panel
        match_rule = ITEM.match_rule
        rule = ITEM.rule
        operator_type = ITEM.operator_type

        # custom operator
        if operator_type == 'CUSTOM':
            # custom operator
            bl_idname = ITEM.bl_idname
            op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
            ops_args = ITEM.prop_list
        # default operator
        elif operator_type.startswith('DEFAULT'):
            bl_idname = model_lib.get(operator_type.removeprefix('DEFAULT_').lower())
            op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
            ops_args = dict()

        if op_callable:
            for file_path in self.file_list:
                ops_args['filepath'] = file_path
                try:
                    op_callable(**ops_args)
                except Exception as e:
                    self.report({"ERROR"}, str(e))

    def import_default(self, context):
        """Import with blender's default setting"""
        pass


class WM_OT_SuperImport(SuperImport):
    """Load files/models/images from clipboard"""
    bl_idname = "wm.spio_import"
    bl_label = "Super Import"

    def import_default(self, context):
        ext = self.ext
        if ext in model_lib:
            for file_path in self.file_list:
                bl_idname = model_lib.get(ext)
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
                op_callable(filepath=file_path)
        else:
            join_paths = '$$'.join(self.file_list)

            if context.area.type == "VIEW_3D":
                def draw_3dview_menu(cls, context):
                    layout = cls.layout
                    layout.operator_context = "INVOKE_DEFAULT"
                    # only one blend need to deal with
                    col = layout.column()
                    op = col.operator('wm.spio_import_image', text=f'Import as reference')
                    op.action = 'REF'
                    op.files = join_paths

                    op = col.operator('wm.spio_import_image', text=f'Import as Plane')
                    op.action = 'PLANE'
                    op.files = join_paths

                context.window_manager.popup_menu(draw_3dview_menu,
                                                  title=f'Super Import Image ({len(self.file_list)} files)',
                                                  icon='IMAGE_DATA')
            elif context.area.type == "NODE_EDITOR":
                bpy.ops.wm.spio_import_image(action='NODES', files=join_paths)


def file_context_menu(self, context):
    layout = self.layout
    layout.operator('wm.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def node_context_menu(self, context):
    layout = self.layout
    layout.operator('node.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def register():
    import_icon.register()

    bpy.utils.register_class(WM_OT_SuperImport)

    # Global ext
    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')
    # Menu append
    bpy.types.NODE_MT_context_menu.prepend(node_context_menu)


def unregister():
    import_icon.unregister()

    bpy.types.NODE_MT_context_menu.remove(node_context_menu)

    bpy.utils.unregister_class(WM_OT_SuperImport)
