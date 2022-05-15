import bpy.app

exporter_lib = {
    'EXPORT_DAE': {
        'name': 'Collada (.dae)',
        'bl_idname': 'export_dae',
        'icon': 'EXPORT',
        'number': 199
    },
    'EXPORT_ABC': {
        'name': 'Alembic (.abc)',
        'bl_idname': 'wm.alembic_export',
        'icon': 'IMPORT',
        'number': 198
    },
    'EXPORT_USD': {
        'name': 'USD (.usd)',
        'bl_idname': 'export_usd',
        'icon': 'IMPORT',
        'number': 197
    },
    'EXPORT_USDC': {
        'name': 'USD (.usdc)',
        'bl_idname': 'wm.usd_export',
        'icon': 'IMPORT',
        'number': 196
    },
    'EXPORT_USDA': {
        'name': 'USD (.usda)',
        'bl_idname': 'wm.usd_export',
        'icon': 'IMPORT',
        'number': 195
    },
    'EXPORT_PLY': {
        'name': 'Stanford (.ply)',
        'bl_idname': 'export_mesh.ply',
        'icon': 'IMPORT',
        'number': 194
    },
    'EXPORT_STL': {
        'name': 'Stl (.stl)',
        'bl_idname': 'export_mesh.stl',
        'icon': 'IMPORT',
        'number': 193
    },
}

exporter_min = {
    'blend': 'spio.export_blend',
    'stl': 'export_mesh.stl',
    'obj': 'export_scene.obj',
    'fbx': 'export_scene.fbx',
}

exporter_extend = {
    'abc': 'wm.alembic_export',
    'usdc': 'wm.usd_export',
    'gltf': 'export_scene.gltf',
    'ply': 'export_mesh.ply',
    'svg': 'wm.gpencil_export_svg',
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
    'svg': {

    }

}


def get_exporter(cpp_obj_exporter=True, extend=False):
    m = exporter_min.copy()
    if cpp_obj_exporter and bpy.app.version >= (3, 1, 0):
        m['obj'] = 'wm.obj_export'
    if extend:
        m.update(exporter_extend)

    return m


def get_exporter_ops_props(cpp_obj_exporter=True):
    props = exporter_ops_props.copy()
    if cpp_obj_exporter and bpy.app.version >= (3, 1, 0):
        props['obj'] = {'export_selected_objects': True}
    else:
        props['obj'] = {'use_selection': True}

    return props
