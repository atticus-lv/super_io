bl_info = {
    "name": "Super IO (SPIO)",
    "author": "Atticus",
    "blender": (2, 83, 0),
    "version": (1, 4, 5, 1),
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

addon_dir = os.path.dirname(__file__)

# get all .py file dir
py_paths = [os.path.join(root, f) for root, dirs, files in os.walk(addon_dir) for f in files if
            f.endswith('.py') and f != '__init__.py']

for path in py_paths:
    name = os.path.basename(path)[:-3]
    correct_path = path.replace('\\', '/')
    # split dir with folder name
    dir_list = [list(g) for k, g in groupby(correct_path.split('/'), lambda x: x == __folder_name__) if
                not k]
    # combine dir and make dict like this: 'name:folder.name'
    if 'third_party_addons' not in dir_list[-1] or 'clipboard' not in dir_list[-1]:
        r_name_raw = __folder_name__ + '.' + '.'.join(dir_list[-1])
        __dict__[name] = r_name_raw[:-3]

# auto reload
for name in __dict__.values():
    if name in sys.modules:
        importlib.reload(sys.modules[name])
    else:
        globals()[name] = importlib.import_module(name)
        setattr(globals()[name], 'modules', __dict__)


def prepare():
    from addon_utils import enable
    addons = [
        'io_import_images_as_planes',
        'io_import_dxf',
        'io_import_obj',  # 3.0 and lower obj io
        'io_scene_obj',  # 3.1 and heigher obj io
        'io_scene_fbx',
        'io_scene_gltf2',
        'io_curve_svg',
        'io_mesh_stl',
        'io_mesh_ply',
        # 'node_wrangler', # use to set up pbr textures

    ]
    for addon in addons:
        try:
            enable(addon)
        except ModuleNotFoundError:
            pass


def register():
    for name in __dict__.values():
        if name in sys.modules and hasattr(sys.modules[name], 'register'):
            try:
                sys.modules[name].register()
            except ValueError:  # open template file may cause this problem
                pass

    prepare()


def unregister():
    for name in __dict__.values():
        if name in sys.modules and hasattr(sys.modules[name], 'unregister'):
            try:
                sys.modules[name].unregister()
            except Exception as e:
                print(e)


if __name__ == '__main__':
    register()
