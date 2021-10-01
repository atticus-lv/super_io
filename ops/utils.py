import bpy
from .. import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


def get_config():
    pref = get_pref()
    config = dict()
    for extension_list_index, item in enumerate(pref.extension_list):
        if item.name == '' or item.bl_idname == '': continue

        ops_config = {'bl_idname': item.bl_idname}

        for prop_index, prop_item in enumerate(item.prop_list):
            prop = prop_item.name
            value = prop_item.value

            if prop == '' or value == '': continue

            if value in {'0', '1'}:
                ops_config[prop] = int(value)
            elif value.isdigit():
                ops_config[prop] = float(value)
            elif value in {'True', 'False'}:
                ops_config[prop] = eval(value)
            elif value in {'0', '1'}:
                ops_config[prop] = int(value)
            else:
                ops_config[prop] = value

        config[item.name] = ops_config

    return config
