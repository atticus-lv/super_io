import bpy
from .. import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


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


def get_config(check_use=False) -> dict:
    """
    :return:{
        extension[str]:{
        'bl_idname':bl_idname[str],
        **args
        }
    }
    """
    pref = get_pref()
    config = dict()
    for extension_list_index, item in enumerate(pref.extension_list):
        if item.name == '' or item.bl_idname == '': continue
        if check_use and item.use is False: continue
        
        ops_config = {'bl_idname': item.bl_idname}

        for prop_index, prop_item in enumerate(item.prop_list):
            prop = prop_item.name
            value = prop_item.value

            if prop == '' or value == '': continue

            if value.isdigit():
                ops_config[prop] = int(value)
            elif is_float(value):
                ops_config[prop] = float(value)
            elif value in {'True', 'False'}:
                ops_config[prop] = eval(value)
            else:
                ops_config[prop] = value

        config[item.name] = ops_config

    return config
