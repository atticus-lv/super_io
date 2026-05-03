import bpy

from .. import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    addon = bpy.context.preferences.addons.get(__folder_name__)
    if addon is not None:
        return addon.preferences
    return None
