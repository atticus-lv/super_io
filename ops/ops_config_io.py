import bpy
import json
import os

from .utils import get_config, get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper


class SPIO_OT_ConfigImport(bpy.types.Operator, ImportHelper):
    """Import config from a json file"""

    bl_idname = "spio.config_import"
    bl_label = "Import Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    def execute(self, context):
        pref = get_pref()
        exist_config,index_list = get_config(pref.config_list)

        with open(self.filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            for name, values in data.items():
                if name not in exist_config:
                    item = pref.config_list.add()

                    item.name = name
                    item.extension = values.pop('extension')
                    item.description = values.pop('description')
                    item.bl_idname = values.pop('bl_idname')

                    for prop, prop_value in values['prop_list'].items():
                        prop_item = item.prop_list.add()
                        prop_item.name = prop
                        prop_item.value = str(prop_value)

            self.report({"INFO"}, f'Load config from "{self.filepath}"')

        return {"FINISHED"}


class SPIO_OT_ConfigExport(bpy.types.Operator, ExportHelper):
    """Export all configs to a json file"""

    bl_idname = "spio.config_export"
    bl_label = "Export Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    # use_filter_folder = True

    def execute(self, context):
        config_list = get_pref().config_list
        config,index_list = get_config(config_list)
        with open(self.filepath, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            self.report({"INFO"}, f'Save config to "{self.filepath}"')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_ConfigImport)
    bpy.utils.register_class(SPIO_OT_ConfigExport)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_ConfigImport)
    bpy.utils.unregister_class(SPIO_OT_ConfigExport)
