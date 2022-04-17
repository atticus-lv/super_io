import bpy

importer = {
    'usd': 'wm.usd_import',
    'usdc': 'wm.usd_import',
    'usda': 'wm.usd_import',

    'ply': 'import_mesh.ply',
    'stl': 'import_mesh.stl',
    'dae': 'wm.collada_import',
    'abc': 'wm.alembic_import',
    'obj': 'import_scene.obj' if bpy.app.version < (3, 2, 0) else 'wm.obj_import',
    'fbx': 'import_scene.fbx',

    'glb': 'import_scene.gltf',
    'gltf': 'import_scene.gltf',

    'x3d': 'import_scene.x3d',
    'wrl': 'import_scene.x3d',

    'svg': 'import_curve.svg',
    'dxf': 'import_scene.dxf',
}
