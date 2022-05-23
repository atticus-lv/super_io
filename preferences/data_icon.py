import bpy

from ..ui.icon_utils import RSN_Preview

import_icon = RSN_Preview(image='import.bip', name='import_icon')
export_icon = RSN_Preview(image='export.bip', name='import_icon')


def get_color_tag_icon(index):
    if bpy.app.version < (2, 93, 0):
        return 'COLORSET_13_VEC' if index == 0 else f'COLORSET_0{index}_VEC'
    else:
        return f'COLLECTION_COLOR_0{index}' if index != 0 else 'OUTLINER_COLLECTION'

def register():
    import_icon.register()
    export_icon.register()


def unregister():
    import_icon.unregister()
    export_icon.unregister()
