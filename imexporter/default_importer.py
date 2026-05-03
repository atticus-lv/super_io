import bpy

importer = {
    'usd': 'wm.usd_import',
    'usdc': 'wm.usd_import',
    'usda': 'wm.usd_import',

    'ply': 'wm.ply_import',
    'stl': 'wm.stl_import',
    'abc': 'wm.alembic_import',
    'obj': 'wm.obj_import',
    'fbx': 'wm.fbx_import',

    'glb': 'import_scene.gltf',
    'gltf': 'import_scene.gltf',

    'svg': 'wm.grease_pencil_import_svg',
    'vdb': 'object.volume_import',
    'bvh': 'import_anim.bvh',
}


def get_importer(cpp_obj_importer=True):
    im = importer.copy()
    im['obj'] = 'wm.obj_import'

    return im


importer_lib = {
    'DEFAULT_ABC': {
        'bl_idname': 'wm.alembic_import',
        'name': 'Alembic (.abc)',
        'description': '',
        'icon': 'IMPORT',
        'number': 98,
        'ext': 'abc'
    },
    'DEFAULT_USD': {
        'bl_idname': 'wm.usd_import',
        'name': 'USD (.usd/.usda/.usdc)',
        'description': '',
        'icon': 'IMPORT',
        'number': 97,
        'ext': ['usd', 'usda', 'usdc']
    },
    'DEFAULT_SVG': {
        'bl_idname': 'wm.grease_pencil_import_svg',
        'name': 'SVG (.svg)',
        'description': '',
        'icon': 'GP_SELECT_POINTS',
        'number': 96,
        'ext': 'svg'
    },
    'DEFAULT_PLY': {
        'bl_idname': 'wm.ply_import',
        'name': 'Stanford (.ply)',
        'description': '',
        'icon': 'IMPORT',
        'number': 95,
        'ext': 'ply'
    },
    'DEFAULT_STL': {
        'bl_idname': 'wm.stl_import',
        'name': 'Stl (.stl)',
        'description': '',
        'icon': 'IMPORT',
        'number': 94,
        'ext': 'stl'
    },
    'DEFAULT_FBX': {
        'bl_idname': 'wm.fbx_import',
        'name': 'FBX (.fbx)',
        'description': '',
        'icon': 'IMPORT',
        'number': 93,
        'ext': 'fbx'
    },
    'DEFAULT_GLTF': {
        'bl_idname': 'import_scene.gltf',
        'name': 'glTF 2.0 (.gltf/.glb)',
        'description': '',
        'icon': 'IMPORT',
        'number': 92,
        'ext': ['gltf', 'glb']
    },
    'DEFAULT_OBJ': {
        'bl_idname': 'wm.obj_import',
        'name': 'Wavefront (.obj)',
        'description': '',
        'icon': 'IMPORT',
        'number': 91,
        'ext': 'obj'
    },
    'OpenVDB': {
        'bl_idname': 'object.volume_import',
        'name': 'OpenVDB (.vdb)',
        'description': '',
        'icon': 'VOLUME_DATA',
        'number': 89,
        'ext': 'vdb'
    },
    'MotionCapture': {
        'bl_idname': 'import_anim.bvh',
        'name': 'Motion Capture (.bvh)',
        'description': '',
        'icon': 'VOLUME_DATA',
        'number': 88,
        'ext': 'bvh'
    }
}
