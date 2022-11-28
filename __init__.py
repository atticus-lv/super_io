bl_info = {
    "name": "Super IO (SPIO)",
    "author": "Atticus",
    "blender": (2, 83, 0),
    "version": (1, 4, 7),
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "https://atticus-lv.gitee.io/super_io/#/",
    "tracker_url": "https://github.com/atticus-lv/super_io/issues",
    "description": "Copy paste to import and export Model/Images (Inspired by Binit's ImagePaste)",
    'warning': "Support Windows/MacOS (no copy multiple files to clipboard in mac)",
    "location": "3DView > F3 > Super Import('Ctrl Shift V') / Super Export('Ctrl Shift C')",
}

import importlib
import sys
import os
from itertools import groupby

# get folder name
__folder_name__ = __name__
__dict__ = {}

from . import translation, ui, ops, addon, preferences

classes = (
    preferences,
    ops,
    addon,
    ui,
    translation
)


def prepare():
    from addon_utils import enable
    addons = [
        'io_import_images_as_planes',
        'io_import_dxf',
        'io_scene_obj',  # 3.1 and heigher obj io
        'io_scene_fbx',
        'io_scene_gltf2',
        'io_curve_svg',
        'io_mesh_stl',
        'io_mesh_ply',
        'io_anim_bvh',
        # 'node_wrangler', # use to set up pbr textures

    ]
    for addon in addons:
        try:
            enable(addon)
        except ModuleNotFoundError:
            pass


def register():
    for cls in classes:
        try:
            cls.register()
        except Exception as e:
            print(e)

    prepare()


def unregister():
    for cls in classes:
        try:
            cls.unregister()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    register()
