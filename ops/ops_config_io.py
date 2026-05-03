import bpy
import json
import os

from bpy.props import StringProperty, BoolProperty
from .core import get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper
from ..preferences.data_config_store import (
    apply_config_to_item,
    get_config_data,
    normalize_document,
    write_runtime_config,
)


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
        config_data = get_config_data(context)
        existing = {
            item.identifier or item.name
            for item in config_data.config_list
        }

        with open(self.filepath, "r", encoding='utf-8') as f:
            document = normalize_document(json.load(f))

        imported_count = 0
        for config in document["configs"]:
            key = config.get("identifier") or config.get("name")
            if key in existing:
                continue
            item = config_data.config_list.add()
            apply_config_to_item(item, config)
            existing.add(key)
            imported_count += 1

        write_runtime_config(context=context)
        self.report({"INFO"}, f'Load {imported_count} config(s) from "{self.filepath}"')

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

        CONFIG = ConfigHelper(check_use=not self.export_all, io_type="ALL")
        config, index_list = CONFIG.config_list, CONFIG.index_list
        config_data = get_config_data(context)
        configs = [
            config_data.config_list[index]
            for index in index_list
        ]
        from ..preferences.data_config_store import config_document_from_items

        document = config_document_from_items(configs)
        with open(self.filepath, "w", encoding='utf-8') as f:
            json.dump(document, f, indent=4, ensure_ascii=False)
            self.report({"INFO"}, f'Save config to "{self.filepath}"')

        return {"FINISHED"}


class SPIO_OT_save_config(bpy.types.Operator):
    """Save runtime config to the extension JSON store"""

    bl_idname = "spio.save_config"
    bl_label = "Save Config"
    bl_options = {"REGISTER"}

    def execute(self, context):
        path = write_runtime_config(context=context)
        self.report({"INFO"}, f'Save config to "{path}"')
        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_import_config)
    bpy.utils.register_class(SPIO_OT_export_config)
    bpy.utils.register_class(SPIO_OT_save_config)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_save_config)
    bpy.utils.unregister_class(SPIO_OT_import_config)
    bpy.utils.unregister_class(SPIO_OT_export_config)
