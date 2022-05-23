from . import data_icon, data_config_prop, data_keymap, data_config_filter_panel, prefs

classes = (
    data_icon, data_config_prop, data_config_filter_panel, data_keymap, prefs
)


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in reversed(classes):
        cls.unregister()
