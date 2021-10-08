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


def get_config(pref_config: CollectionProperty, check_use=False, filter=None, return_index=False):
    """
    :return:{
        name[str]:{
        'extension':extension[str],
        'bl_idname':bl_idname[str],
        'prop_list':**args[dict],
        },
        ...
    }
    """
    config_list = dict()
    index_list = []
    for config_list_index, item in enumerate(pref_config):

        if True in (item.name == '',
                    item.bl_idname == '',
                    item.extension == ''): continue
        if check_use and item.use_config is False: continue

        if filter:
            if item.extension != filter: continue

        ops_config = dict()
        config = {'extension': item.extension,
                  'description': item.description,
                  'bl_idname': item.bl_idname,
                  'prop_list': ops_config}

        index_list.append(config_list_index)

        if len(item.prop_list) != 0:
            for prop_index, prop_item in enumerate(item.prop_list):
                prop = prop_item.name
                value = prop_item.value

                if prop == '' or value == '': continue

                # change string to value
                if value.isdigit():
                    ops_config[prop] = int(value)
                elif is_float(value):
                    ops_config[prop] = float(value)
                elif value in {'True', 'False'}:
                    ops_config[prop] = eval(value)
                else:
                    ops_config[prop] = value

        config_list[item.name] = config

    return config_list if not return_index else config_list, index_list
