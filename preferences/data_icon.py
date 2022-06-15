import bpy
import os

from pathlib import Path
from ..ui.t3dn_bip import previews

G_PV_COLL = {}
G_ICON_ID = {}


def register_icon():
    # global G_PV_COLL, G_ICON_ID

    icon_dir = Path(__file__).parent.parent.joinpath('ui', 'icons')
    mats_icon = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith('.bip'):
            mats_icon.append(icon_dir.joinpath(file))
    # 注册
    pcoll = previews.new()

    for icon_path in mats_icon:
        pcoll.load(icon_path.name[:-4], str(icon_path), 'IMAGE')
        G_ICON_ID[icon_path.name[:-4]] = pcoll.get(icon_path.name[:-4]).icon_id

    G_PV_COLL['spio_icon'] = pcoll


def unregister_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    for pcoll in G_PV_COLL.values():
        previews.remove(pcoll)
        G_PV_COLL.clear()

    G_ICON_ID.clear()


def get_color_tag_icon(index):
    if bpy.app.version < (2, 93, 0):
        return 'COLORSET_13_VEC' if index == 0 else f'COLORSET_0{index}_VEC'
    else:
        return f'COLLECTION_COLOR_0{index}' if index != 0 else 'OUTLINER_COLLECTION'


def register():
    register_icon()


def unregister():
    unregister_icon()
