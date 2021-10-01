import bpy
import json
import os

from .utils import get_config, get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper


class SPIO_OT_ConfigImport(bpy.types.Operator, ImportHelper):
    """Paste Model/Images"""

    bl_idname = "spio.config_import"
    bl_label = "Import Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    def execute(self, context):
        pref = get_pref()
        exist_config = get_config(check_use=False)

        with open(self.filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            for ext, values in data.items():
                if ext not in exist_config:
                    item = pref.extension_list.add()

                    item.name = values.pop('extension')
                    item.bl_idname = values.pop('bl_idname')

                    for prop, prop_value in values.items():
                        prop_item = item.prop_list.add()
                        prop_item.name = prop
                        prop_item.value = str(prop_value)

            self.report({"INFO"}, f'Load config from "{self.filepath}"')

        return {"FINISHED"}


class SPIO_OT_ConfigExport(bpy.types.Operator, ExportHelper):
    """Paste Model/Images"""

    bl_idname = "spio.config_export"
    bl_label = "Export Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    # use_filter_folder = True

    def execute(self, context):
        config = get_config()
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
