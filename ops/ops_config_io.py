import bpy
import json
import os

from bpy.props import StringProperty, BoolProperty
from .core import get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper


class SPIO_OT_import_config(bpy.types.Operator, ImportHelper):
    """Import config from a json file"""

    bl_idname = "spio.import_config"
    bl_label = "Import Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        from .core import ConfigHelper

        pref = get_pref()
        CONFIG = ConfigHelper(io_type='ALL')
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


class SPIO_OT_export_config(bpy.types.Operator, ExportHelper):
    """wm.super_importExport marked configs to a json file"""

    bl_idname = "spio.export_config"
    bl_label = "Export Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    export_all: BoolProperty(name='Export All', default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'export_all')

    def execute(self, context):
        from .core import ConfigHelper

        CONFIG = ConfigHelper(check_use=self.export_all,io_type="ALL")
        config, index_list = CONFIG.config_list, CONFIG.index_list
        print(config)
        with open(self.filepath, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            self.report({"INFO"}, f'Save config to "{self.filepath}"')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_import_config)
    bpy.utils.register_class(SPIO_OT_export_config)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_config)
    bpy.utils.unregister_class(SPIO_OT_export_config)
