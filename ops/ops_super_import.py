from __future__ import annotations

import os.path
import sys

import bpy
from bpy.props import (StringProperty)

from .dynamic_io import IO_Base
from .core import MeasureTime, ConfigItemHelper, ConfigHelper
from .core import get_pref

from ..preferences.data_icon import G_ICON_ID


class SuperImport(IO_Base, bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # Build-in
    ############
    def invoke(self, context, event):
        self.restore()

        from ..clipboard.clipboard import Clipboard as Clipboard
        # get Clipboard
        self.clipboard = Clipboard()
        file_list = self.clipboard.pull_files_from_clipboard(force_unicode=get_pref().force_unicode)

        del self.clipboard  # release clipboard

        if len(file_list) == 0:
            self.report({"ERROR"}, "No file found in clipboard!")
            return {"CANCELLED"}

        for file_path in file_list:
            if os.path.isdir(file_path):
                self.dir_list.append(file_path)  # add dir list for batch import folder's files
                continue
            elif not os.path.exists(file_path):
                self.report({"ERROR"}, f"{file_path} not exist!")

            # pass extra file
            extension = file_path.split('.')[-1].lower()
            if extension in {'mtl'}:
                continue

            self.file_list.append(file_path)
        # count ext type
        ext_list = [file.split('.')[-1].lower() for file in self.file_list]
        # report if more than one extension is selected
        if len(set(ext_list)) > 1:
            self.report({"WARNING"}, "More than one format of file is copied!")
            # return {"CANCELLED"}
        ext_count_dict = dict()

        for ext in ext_list:
            if ext not in ext_count_dict:
                ext_count_dict[ext] = 1
            else:
                ext_count_dict[ext] += 1

        # set the main ext
        for key, value in ext_count_dict.items():
            if (value == max(ext_count_dict.values())):
                self.ext = key
                break

        # call for match configs
        self.CONFIGS = ConfigHelper(check_use=True, filter=self.ext, io_type='IMPORT')

        # import default if not custom config for this file extension
        if self.CONFIGS.is_empty():
            self.use_custom_config = False

            if self.ext == 'blend':
                self.import_blend_default(context)
                return {'FINISHED'}
            else:
                return self.execute(context)

        self.use_custom_config = True

        return self.import_custom_dynamic(context)

    def execute(self, context):
        with MeasureTime() as start_time:
            self.import_default(context)
            self.report_time(start_time)

        return {"FINISHED"}

    # Import Method (Popup)
    def import_custom_dynamic(self, context):
        # unregister_class
        self.unregister_dep_classes()
        self.dep_classes.clear()

        # no match list
        file_list = self.file_list
        dir_list = self.dir_list
        # match dict
        match_file_op_dict = dict()
        # match index :exclude from popup importer
        match_index_list = list()

        for index in self.CONFIGS.index_list:
            # set config for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)
            if not ITEM.is_config_item_poll(context.area.type): continue

            match_files = ITEM.get_match_files(file_list)

            if len(match_files) > 0:
                for file in match_files:
                    match_file_op_dict[file] = ITEM
                match_index_list.append(index)

        # dynamic operator
        ##################
        from .dynamic_io import DynamicImport
        from ..imexporter.default_importer import get_importer

        importer = get_importer(cpp_obj_importer=get_pref().cpp_obj_importer)

        for index in self.CONFIGS.index_list:
            if index in match_index_list: continue  # not register those match config
            # only for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)
            if not ITEM.is_config_item_poll(context.area.type): continue

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": ITEM.name,
                           "bl_description": ITEM.description,
                           "execute": DynamicImport.execute,
                           # custom pass in
                           'ITEM': ITEM,
                           'file_list': file_list,
                           'dir_list': dir_list,
                           'match_file_op_dict': match_file_op_dict,
                           },
                          )

            self.dep_classes.append(op_cls)

        # register
        self.register_dep_classes()

        ############################
        # execute
        ############################

        # first import all matching rule files
        if len(match_file_op_dict) > 0:
            with MeasureTime() as start_time:
                for filepath, item_helper in match_file_op_dict.items():
                    op_callable, ops_args, op_context = item_helper.get_operator_and_args()
                    ops_args['filepath'] = filepath
                    try:
                        if op_context:
                            op_callable(op_context, **ops_args)
                        else:
                            op_callable(**ops_args)

                    except Exception as e:
                        self.report({"ERROR"}, str(e))

                if get_pref().report_time: self.report_time(start_time)

        # then popup menu to select the remain not matching file
        remain_list = list()
        for file in file_list:
            # file match ext but not in config
            if file not in match_file_op_dict:
                remain_list.append(file)
            # file not match ext
            if file.split('.')[-1] != self.ext:
                remain_list.append(file)

        # menu title
        if len(match_file_op_dict) > 0:
            title = f'Match {self.ext.upper()} import finish (Import {len(match_file_op_dict)} files)'
        else:
            title = f'Super Import {self.ext.upper()}'

        if len(remain_list) > 0:
            # set draw menu
            from .core import PopupImportMenu
            import_op = self
            ext = self.ext

            def draw_custom_menu(self, context):
                layout = self.layout
                if len(match_file_op_dict) > 0:
                    layout.label(text=f'Remain {len(remain_list)} files')

                if len(import_op.dep_classes) > 0:
                    for cls in import_op.dep_classes:
                        layout.operator(cls.bl_idname)

                layout.separator()
                # default popup
                if ext in importer:
                    layout.operator('spio.import_model').files = '$$'.join(
                        remain_list)
                elif ext == 'blend':
                    pop = PopupImportMenu(file_list=remain_list,
                                          dir_list=dir_list,
                                          context=context)
                    menu = pop.default_blend_menu(return_menu=True)
                    if menu: menu(self, context)
                else:
                    pop = PopupImportMenu(file_list=remain_list,
                                          dir_list=dir_list,
                                          context=context)
                    menu = pop.default_image_menu(return_menu=True)
                    if menu: menu(self, context)

            context.window_manager.popup_menu(draw_custom_menu, title=title, icon='FILEBROWSER')

        return {'FINISHED'}


class WM_OT_super_import(SuperImport):
    """Load files/models/images from clipboard"""
    bl_idname = "wm.super_import"
    bl_label = "Super Import"

    def import_blend_default(self, context):
        """Import with default popup"""
        from .core import PopupImportMenu
        popup = PopupImportMenu(file_list=self.file_list,
                                dir_list=self.dir_list,
                                context=context)
        popup.default_blend_menu()

    def import_default(self, context):
        from ..imexporter.default_importer import get_importer

        importer = get_importer(cpp_obj_importer=get_pref().cpp_obj_importer)

        ext = self.ext
        if ext in importer:
            for file_path in self.file_list:
                bl_idname = importer.get(ext)
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
                op_callable(filepath=file_path)
        else:
            from .core import PopupImportMenu

            popup = PopupImportMenu(self.file_list, self.dir_list, context)
            popup.default_image_menu()


def file_context_menu(self, context):
    layout = self.layout
    layout.operator('wm.super_import', icon_value=G_ICON_ID['import'])
    layout.separator()


def node_context_menu(self, context):
    layout = self.layout
    layout.operator('node.spio_import', icon_value=G_ICON_ID['import'])
    layout.separator()


def register():
    bpy.utils.register_class(WM_OT_super_import)

    # Global ext
    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')
    bpy.types.WindowManager.spio_cache_import = StringProperty()
    # Menu append
    bpy.types.NODE_MT_context_menu.prepend(node_context_menu)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(node_context_menu)

    bpy.utils.unregister_class(WM_OT_super_import)

    del bpy.types.Scene.spio_ext
    del bpy.types.WindowManager.spio_cache_import
