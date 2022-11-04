import bpy
import json
import os
import platform

from .. import bl_info
from bpy.props import StringProperty, BoolProperty
from .core import get_pref
from bpy_extras.io_utils import ExportHelper, ImportHelper


def load_config_json(filepath, exist_config, pref):
    """
    旧版本config.json导入
    """
    with open(filepath, "r", encoding='utf-8') as f:
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


def load_config_yaml(filepath, exist_config, pref):
    """
    version: 0.1
    """
    import yaml

    with open(filepath, "r", encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

        version = data.get('version')
        software = data.get('software')
        addon_version = bl_info.get('addon_version')
        config_list = data.get('config')

        for config_dict in config_list:
            name = config_dict.get('name')
            if name in exist_config: continue

            item = pref.config_list.add()
            item.name = name

            for key, value in config_dict.items():
                if key != 'prop_list':
                    setattr(item, key, value)
                else:
                    for prop, prop_value in config_dict.get('prop_list').items():
                        prop_item = item.prop_list.add()
                        prop_item.name = prop
                        prop_item.value = str(prop_value)


class SPIO_OT_import_config(bpy.types.Operator, ImportHelper):
    """Import config from a json file"""

    bl_idname = "spio.import_config"
    bl_label = "Import Config"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: StringProperty(
        default="*.yaml;*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        from .core import ConfigHelper

        pref = get_pref()
        CONFIG = ConfigHelper(io_type='ALL')
        exist_config, index_list = CONFIG.config_list, CONFIG.index_list

        if self.filepath.endswith('.json'):
            load_config_json(self.filepath, exist_config, pref)
        elif self.filepath.endswith('.yaml'):
            load_config_yaml(self.filepath, exist_config, pref)
        else:
            self.report({"ERROR"}, f'Unsupported file type: {self.filepath}')
            return {'CANCELLED'}

        self.report({"INFO"}, f'Load config from "{self.filepath}"')

        return {"FINISHED"}


class SPIO_OT_export_config(bpy.types.Operator, ExportHelper):
    """wm.super_importExport marked configs to a json file"""

    bl_idname = "spio.export_config"
    bl_label = "Export Config"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".yaml"

    filter_glob: StringProperty(
        default="*.yaml",
        options={'HIDDEN'}
    )

    export_all: BoolProperty(name='Export All', default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'export_all')

    def execute(self, context):
        from .core import ConfigHelper

        CONFIG = ConfigHelper(check_use=self.export_all, io_type="ALL")
        config, index_list = CONFIG.config_list, CONFIG.index_list
        # print(config)
        # with open(self.filepath, "w", encoding='utf-8') as f:
        #     json.dump(config, f, indent=4, ensure_ascii=False)

        with open(self.filepath, "w", encoding='utf-8') as f:
            f.write('version: 0.1\n')
            f.write(f'platform: {platform.system()}\n')
            f.write('software: Blender\n')
            f.write(f"addon_version: {'.'.join([str(i) for i in bl_info['version']])}\n")

            data = {
                'config': list(config.values())
            }
            import yaml
            yaml.dump(data, f, allow_unicode=True)

        self.report({"INFO"}, f'Save config to "{self.filepath}"')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(SPIO_OT_import_config)
    bpy.utils.register_class(SPIO_OT_export_config)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_config)
    bpy.utils.unregister_class(SPIO_OT_export_config)
