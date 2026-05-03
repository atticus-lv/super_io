import bpy
import os
import bpy.utils.previews

from pathlib import Path

G_PV_COLL = {}
G_ICON_ID = {}


def register_icon():
    # global G_PV_COLL, G_ICON_ID

    icon_dir = Path(__file__).parent.parent.joinpath('ui', 'icons')
    mats_icon = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith('.png'):
            mats_icon.append(icon_dir.joinpath(file))

    pcoll = bpy.utils.previews.new()

    for icon_path in mats_icon:
        icon_name = icon_path.stem
        pcoll.load(icon_name, str(icon_path), 'IMAGE')
        G_ICON_ID[icon_name] = pcoll.get(icon_name).icon_id

    G_PV_COLL['spio_icon'] = pcoll


def unregister_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    for pcoll in G_PV_COLL.values():
        bpy.utils.previews.remove(pcoll)

    G_PV_COLL.clear()
    G_ICON_ID.clear()


def get_color_tag_icon(index):
    return f'COLLECTION_COLOR_0{index}' if index != 0 else 'OUTLINER_COLLECTION'


def register():
    register_icon()


def unregister():
    unregister_icon()
