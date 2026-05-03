__folder_name__ = __name__

from . import translation, ui, ops, addon, preferences

classes = (
    preferences,
    ops,
    addon,
    ui,
    translation
)


def register():
    for cls in classes:
        try:
            cls.register()
        except Exception as e:
            print(e)


def unregister():
    for cls in reversed(classes):
        try:
            cls.unregister()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    register()
