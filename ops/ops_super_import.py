from __future__ import annotations
import sys
import time

import bpy
from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from .op_dynamic_io import IO_Base
from .core import MeasureTime, ConfigItemHelper, ConfigHelper
from .core import is_float, get_pref, convert_value

from ..importer.default_importer import default_importer

from ..ui.icon_utils import RSN_Preview

import_icon = RSN_Preview(image='import.bip', name='import_icon')


class SuperImport(IO_Base, bpy.types.Operator):
    """Paste Model/Images"""
    bl_label = "Super Import"
    bl_options = {"UNDO_GROUPED"}

    # Build-in
    ############
    def invoke(self, context, event):
        self.restore()

        if sys.platform == "win32":
            from ..clipboard.windows import WintypesClipboard as Clipboard
        elif sys.platform == "darwin":
            from ..clipboard.darwin.mac import MacClipboard as Clipboard
        # get Clipboard
        self.clipboard = Clipboard()
        self.file_list = self.clipboard.pull(force_unicode=get_pref().force_unicode)

        del self.clipboard  # release clipboard

        if len(self.file_list) == 0:
            self.report({"ERROR"}, "No file found in clipboard!")
            return {"CANCELLED"}

        for file_path in self.file_list:
            extension = file_path.split('.')[-1].lower()
            if self.ext is None:
                self.ext = extension
            elif self.ext != extension:
                self.report({"ERROR"}, "Only one type of file can be imported at a time")
                return {"CANCELLED"}

        self.CONFIGS = ConfigHelper(check_use=True, filter=self.ext, io_type='IMPORT')
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
        return self.import_custom_dynamic(context)

    def execute(self, context):
        with MeasureTime() as start_time:
            self.import_default(context)
            self.report_time(start_time)

        return {"FINISHED"}

    # Import Method (Popup)
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

            match_files = ITEM.get_match_files(file_list)

            if len(match_files) > 0:
                for file in match_files:
                    match_file_op_dict[file] = ITEM
                match_index_list.append(index)

        # dynamic operator
        ##################
        from .op_dynamic_io import DynamicImport

        for index in self.CONFIGS.index_list:
            if index in match_index_list: continue  # not register those match config
            # only for register
            config_item = get_pref().config_list[index]
            ITEM = ConfigItemHelper(config_item)

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.spio_config_{index}',
                           "bl_label": ITEM.name,
                           "bl_description": ITEM.description,
                           "execute": DynamicImport.execute,
                           # custom pass in
                           'ITEM': ITEM,
                           'file_list': file_list,
                           'match_file_op_dict': match_file_op_dict,
                           },
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
        remain_list = [file for file in file_list if file not in match_file_op_dict]
        # menu title
        if len(match_file_op_dict) > 0:
            title = f'Match {self.ext.upper()} import finish (Import {len(match_file_op_dict)} files)'
        else:
            title = f'Super Import {self.ext.upper()} ({len(remain_list)} files)'

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
                if ext in default_importer:
                    layout.operator('spio.import_model').files = '$$'.join(
                        remain_list)
                elif ext == 'blend':
                    pop = PopupImportMenu(file_list=remain_list, context=context)
                    menu = pop.default_blend_menu(return_menu=True)
                    if menu: menu(self, context)
                else:
                    pop = PopupImportMenu(file_list=remain_list, context=context)
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
        popup = PopupImportMenu(file_list=self.file_list, context=context)
        popup.default_blend_menu()

    def import_default(self, context):
        ext = self.ext
        if ext in default_importer:
            for file_path in self.file_list:
                bl_idname = default_importer.get(ext)
                op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])
                op_callable(filepath=file_path)
        else:
            from .core import PopupImportMenu

            popup = PopupImportMenu(self.file_list, context)
            popup.default_image_menu()


def file_context_menu(self, context):
    layout = self.layout
    layout.operator('wm.super_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def node_context_menu(self, context):
    layout = self.layout
    layout.operator('node.spio_import', icon_value=import_icon.get_image_icon_id())
    layout.separator()


def register():
    import_icon.register()

    bpy.utils.register_class(WM_OT_super_import)

    # Global ext
    bpy.types.Scene.spio_ext = StringProperty(name='Filter extension', default='')
    bpy.types.WindowManager.spio_cache_import = StringProperty()
    # Menu append
    bpy.types.NODE_MT_context_menu.prepend(node_context_menu)


def unregister():
    import_icon.unregister()

    bpy.types.NODE_MT_context_menu.remove(node_context_menu)

    bpy.utils.unregister_class(WM_OT_super_import)

    del bpy.types.Scene.spio_ext
    del bpy.types.WindowManager.spio_cache_import
