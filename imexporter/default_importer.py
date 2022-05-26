import bpy

importer = {
    'usd': 'wm.usd_import',
    'usdc': 'wm.usd_import',
    'usda': 'wm.usd_import',

    'ply': 'import_mesh.ply',
    'stl': 'import_mesh.stl',
    'dae': 'wm.collada_import',
    'abc': 'wm.alembic_import',
    'obj': 'import_scene.obj',
    'fbx': 'import_scene.fbx',

    'glb': 'import_scene.gltf',
    'gltf': 'import_scene.gltf',

    'x3d': 'import_scene.x3d',
    'wrl': 'import_scene.x3d',

    'svg': 'import_curve.svg',
    'dxf': 'import_scene.dxf',
    'vdb': 'object.volume_import',
    'bvh': 'import_anim.bvh',
}


def get_importer(cpp_obj_importer=True):
    im = importer.copy()
    if cpp_obj_importer and bpy.app.version >= (3, 2, 0):
        im['obj'] = 'wm.obj_import'

    return im


importer_lib = {
    'DEFAULT_DAE': {
        'bl_idname': 'wm.collada_import',
        'name': 'Collada (.dae)',
        'description': '',
        'icon': 'IMPORT',
        'number': 99,
        'ext': 'dae'
    },
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
        'bl_idname': 'import_curve.svg',
        'name': 'SVG (.svg)',
        'description': '',
        'icon': 'GP_SELECT_POINTS',
        'number': 96,
        'ext': 'svg'
    },
    'DEFAULT_PLY': {
        'bl_idname': 'import_mesh.ply',
        'name': 'Stanford (.ply)',
        'description': '',
        'icon': 'IMPORT',
        'number': 95,
        'ext': 'ply'
    },
    'DEFAULT_STL': {
        'bl_idname': 'import_mesh.stl',
        'name': 'Stl (.stl)',
        'description': '',
        'icon': 'IMPORT',
        'number': 94,
        'ext': 'stl'
    },
    'DEFAULT_FBX': {
        'bl_idname': 'import_scene.fbx',
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
        'bl_idname': 'import_scene.obj',
        'name': 'Wavefront (.obj)',
        'description': '',
        'icon': 'IMPORT',
        'number': 91,
        'ext': 'obj'
    },
    'DEFAULT_X3D': {
        'bl_idname': 'import_scene.x3d',
        'name': 'X3D (.x3d/.wrl)',
        'description': '',
        'icon': 'IMPORT',
        'number': 90,
        'ext': ['x3d', 'wrl']
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
