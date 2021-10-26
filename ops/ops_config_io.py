import bpy
import json
import os

from bpy.props import StringProperty
from .utils import ConfigHelper, get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper


class SPIO_OT_ConfigImport(bpy.types.Operator, ImportHelper):
    """Import config from a json file"""

    bl_idname = "spio.config_import"
    bl_label = "Import Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        pref = get_pref()
        CONFIG = ConfigHelper()
        exist_config, index_list = CONFIG.config_list, CONFIG.index_list

        with open(self.filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            for name, config_dict in data.items():
                if name not in exist_config:
                    item = pref.config_list.add()

                    for key, value in config_dict.items():
                        # apply normal attribute
                        if key != 'prop_list':
                            setattr(item, key, config_dict.get(key))
                        # apply prop list
                        for prop, prop_value in config_dict.get('prop_list').items():
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

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    # use_filter_folder = True

    def execute(self, context):
        CONFIG = ConfigHelper()
        config, index_list = CONFIG.config_list, CONFIG.index_list
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
