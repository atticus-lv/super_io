import os
import yaml
import json
import re
from pathlib import Path
from enum import Enum

import bpy


class FilterRule(Enum):
    """Defines for filter rules"""
    NONE = 'NONE'
    STARTSWITH = 'STARTSWITH'
    ENDSWITH = 'ENDSWITH'
    IN = 'IN'
    REGEX = 'REGEX'


class ConfigDefines(Enum):
    """Defines for config"""
    BL_IDNAME = 'bl_idname'
    FILE_TYPES = 'file_types'
    ICON = 'icon'
    PRE_SCRIPT = 'pre_script'
    POST_SCRIPT = 'post_script'
    ARGS = 'args'
    CONTEXT = 'context'


class Loader(yaml.Loader):
    """Custom YAML loader that supports !include statements."""

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r', encoding='utf-8') as fr:
            return yaml.load(fr, Loader)


Loader.add_constructor('!include', Loader.include)


class SPIO_Config:
    """Custom Yaml Config Loader"""

    @staticmethod
    def get() -> dict:
        """Read imexporter from yaml file and return a dict

        Returns:
            dict[category:str, list[dict]]
        example:
            {
            'Import': [
                'Collada (.dae)": {
                    'bl_idname': 'import_dae',
                    'file_types:': {'dae'},
                    ...
                    },
                ...
                ],
            'Export': [
                {},
                ...
                ],
            ...
            }
        """

        # version = bpy.app.version
        # if version >= (4,0,0):
        FILENAME = '_config.yaml'
        p = Path(__file__).parent.joinpath('4.0')
        file = p.joinpath(FILENAME)

        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=Loader)

        return data

    @staticmethod
    def get_json() -> str:
        """Json format version"""
        data = SPIO_Config.get()
        catalog_item_json = json.dumps(data, indent=4, allow_nan=True)
        # print(catalog_item_json)
        return catalog_item_json


class ConfigParser():

    def __init__(self):
        self.data = SPIO_Config.get()

    def get_catalog(self) -> list:
        """Return the names of catalog"""
        return list(self.data.keys())

    @staticmethod
    def get_op_by_idname(bl_idname):
        """parse bl_idname to get the operator function"""
        return getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

    def filter_configItem_by_file_types(self, catalog: str, file_types: str):
        """Return the config item that match the file_types"""
        assert catalog in self.get_catalog(), f'Catalog {catalog} not found.'

        file_types = ConfigDefines.FILE_TYPES.value
        catalog_items = self.data[catalog]

        for item in catalog_items:
            if file_types not in item.keys():
                continue
            if file_types in item[file_types]:
                yield item

    def filter_filepaths_by_rule(self, filepaths: list[Path], match_rule: FilterRule, match_value: str):
        assert match_rule in FilterRule, f'Filter rule {match_rule} not found.'

        if match_rule == FilterRule.NONE:
            return filepaths
        elif match_rule == FilterRule.STARTSWITH:
            return [file for file in filepaths if file.stem.startswith(match_value)]
        elif match_rule == FilterRule.ENDSWITH:
            return [file for file in filepaths if file.stem.startswith(match_value)]
        elif match_rule == FilterRule.IN:
            return [file for file in filepaths if match_value in file.stem]
        elif match_rule == FilterRule.REGEX:
            return [file for file in filepaths if re.search(match_value, file.stem)]

    def get_op_and_args(self, name: str, catalog: str):
        assert catalog in self.get_catalog(), f'Catalog {catalog} not found.'
        assert name in self.data[catalog], f'Item {name} not found in catalog {catalog}.'

        idname = ConfigDefines.BL_IDNAME.value
        args = ConfigDefines.ARGS.value
        context = ConfigDefines.CONTEXT.value

        item = self.data[catalog][name]
        assert (bl_idname := item.get(idname), None), f'bl_idname not found in item {name} of catalog {catalog}.'

        op_func = self.get_op_by_idname(bl_idname)
        op_args = item.get(args, {})
        op_context = item.get(context, None)

        return op_func, op_args, op_context
