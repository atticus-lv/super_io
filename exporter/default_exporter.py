default_exporter = {
    # 'usd': 'wm.usd_import',
    'usdc': 'wm.usd_export',
    # 'usda': 'wm.usd_import',
    #
    'ply': 'export_mesh.ply',
    'stl': 'export_mesh.stl',
    'dae': 'wm.collada_export',
    'abc': 'wm.alembic_export',
    'obj': 'export_scene.obj',
    'fbx': 'export_scene.fbx',
    #
    # 'glb': 'export_scene.gltf',
    'gltf': 'export_scene.gltf',
    #
    # 'x3d': 'import_scene.x3d',
    # 'wrl': 'import_scene.x3d',
    #
    # 'svg': 'import_curve.svg',
    'blend': 'spio.export_blend',
}

exporter_ops_props = {
    'obj': {
        'use_selection': True
    },
    'fbx': {
        'use_selection': True
    },
    'stl': {
        'use_selection': True
    },
    'gltf': {
        'use_selection': True,
        'export_format': 'GLTF_EMBEDDED'

    },
    'ply': {
        'use_selection': True
    },
    'dae': {
        'selected': True
    },
    'abc': {
        'selected': True
    },
    'usdc': {
        'selected_objects_only': True
    },
    'blend': {
    },

}
