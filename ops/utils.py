import bpy
from .. import __folder_name__
from bpy.props import CollectionProperty

import time


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


class MeasureTime():
    def __enter__(self):
        return time.time()

    def __exit__(self, type, value, traceback):
        pass


def is_float(s) -> bool:
    s = str(s)
    if s.count('.') == 1:
        left, right = s.split('.')  # [1,1]#-s.2
        if left.isdigit() and right.isdigit():
            return True
        elif left.startswith('-') and left.count('-') == 1 \
                and left[1:].isdigit() and right.isdigit():
            return True

    return False


def convert_value(value):
    if value.isdigit():
        return int(value)
    elif is_float(value):
        return float(value)
    elif value in {'True', 'False'}:
        return eval(value)
    else:
        return value


class ConfigItemHelper():
    def __init__(self, item):
        self.item = item
        for key in item.__annotations__.keys():
            value = getattr(item, key)
            if key != 'prop_list':
                self.__setattr__(key, value)
            # prop list
            ops_config = dict()
            if len(item.prop_list) != 0:
                for prop_index, prop_item in enumerate(item.prop_list):
                    prop, value = prop_item.name, prop_item.value
                    # skip if the prop is not filled
                    if prop == '' or value == '': continue
                    ops_config[prop] = convert_value(value)
            self.__setattr__('prop_list', ops_config)


class ConfigHelper():
    def __init__(self, check_use=False, filter=None):
        pref_config = get_pref().config_list

        config_list = dict()
        index_list = []

        for config_list_index, item in enumerate(pref_config):
            # config dict
            config = dict()
            # get define property
            for key in item.__annotations__.keys():
                value = getattr(item, key)
                if key != 'prop_list':
                    config[key] = value
                # prop list
                ops_config = dict()
                if len(item.prop_list) != 0:
                    for prop_index, prop_item in enumerate(item.prop_list):
                        prop, value = prop_item.name, prop_item.value
                        # skip if the prop is not filled
                        if prop == '' or value == '': continue
                        ops_config[prop] = convert_value(value)
                config['prop_list'] = ops_config

            # check config dict
            if True in (config.get('name') == '',
                        config.get('operator_type') == 'CUSTOM' and config.get('bl_idname') == '',
                        config.get('extension') == '',
                        filter and config.get('extension') != filter,
                        check_use and config.get('use_config') is False,
                        ): continue

            index_list.append(config_list_index)
            config_list[item.name] = config

        self.config_list = config_list
        self.index_list = index_list

    def get_prop_list_from_index(self, index):
        if index > len(self.config_list) - 1: return None

        config_item = self.config_list[index]
        return config_item.get('prop_list')

    def is_empty(self):
        return len(self.config_list) == 0

    def is_only_one_config(self):
        return len(self.config_list) == 1

    def is_more_than_one_config(self):
        return len(self.config_list) > 1
