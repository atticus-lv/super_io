from . import data_icon, data_config_prop, data_keymap, data_config_filter_panel, prefs

classes = (
    data_icon, data_config_prop, data_config_filter_panel, data_keymap, prefs
)


def register():
    data_icon.register()
    data_config_prop.register()
    data_config_filter_panel.register()
    data_keymap.register()
    prefs.register()


def unregister():
    prefs.unregister()
    data_config_prop.unregister()
    data_config_filter_panel.unregister()
    data_keymap.unregister()
    data_icon.unregister()
