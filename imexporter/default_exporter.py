import bpy.app

exporter_lib = {
    'EXPORT_DAE': {
        'name': 'Collada (.dae)',
        'bl_idname': 'export_dae',
        'description': '',
        'icon': 'EXPORT',
        'number': 199,
        'ext': 'dae',
        'prop_list': {
            'selected': True
        }
    },
    'EXPORT_ABC': {
        'name': 'Alembic (.abc)',
        'bl_idname': 'wm.alembic_export',
        'description': '',
        'icon': 'EXPORT',
        'number': 198,
        'ext': 'abc',
        'prop_list': {
            'selected': True
        }
    },
    'EXPORT_USD': {
        'name': 'USD (.usd)',
        'bl_idname': 'export_usd',
        'description': '',
        'icon': 'EXPORT',
        'number': 197,
        'ext': 'usd',
        'prop_list': {
            'selected_objects_only': True
        },
    },
    'EXPORT_USDC': {
        'name': 'USD (.usdc)',
        'bl_idname': 'wm.usd_export',
        'description': '',
        'icon': 'EXPORT',
        'number': 196,
        'ext': 'usdc',
        'prop_list': {
            'selected_objects_only': True
        },
    },
    'EXPORT_USDA': {
        'name': 'USD (.usda)',
        'bl_idname': 'wm.usd_export',
        'description': '',
        'icon': 'EXPORT',
        'number': 195,
        'ext': 'usda',
        'prop_list': {
            'selected_objects_only': True
        },
    },
    'EXPORT_PLY': {
        'name': 'Stanford (.ply)',
        'bl_idname': 'export_mesh.ply',
        'description': '',
        'icon': 'EXPORT',
        'number': 194,
        'ext': 'ply',
        'prop_list': {
            'use_selection': True
        },
    },
    'EXPORT_STL': {
        'name': 'Stl (.stl)',
        'bl_idname': 'export_mesh.stl',
        'description': '',
        'icon': 'EXPORT',
        'number': 193,
        'ext': 'stl',
        'prop_list': {
            'use_selection': True
        },
    },
    'EXPORT_FBX': {
        'name': 'Stl (.stl)',
        'bl_idname': 'export_scene.fbx',
        'description': '',
        'icon': 'EXPORT',
        'number': 192,
        'ext': 'fbx',
        'prop_list': {
            'use_selection': True
        },
    },
    'EXPORT_GLTF': {
        'name': 'glTF 2.0 (.gltf)',
        'bl_idname': 'export_scene.gltf',
        'description': '',
        'icon': 'EXPORT',
        'number': 191,
        'ext': 'gltf',
        'prop_list': {
            'use_selection': True,
            'export_format': 'GLTF_EMBEDDED'
        },
    },
    'EXPORT_OBJ': {
        'name': 'Wavefront (.obj)',
        'bl_idname': 'export_scene.obj',
        'description': '',
        'icon': 'EXPORT',
        'number': 190,
        'ext': 'obj',
        'prop_list': {
            'use_selection': True
        }
    },
    'EXPORT_SVG': {
        'name': 'Grease Pencil (.svg)',
        'bl_idname': 'wm.gpencil_export_svg',
        'description': '',
        'icon': 'EXPORT',
        'number': 189,
        'ext': 'svg'
    },
    'EXPORT_BLEND': {
        'name': 'Blend (.blend)',
        'bl_idname': 'spio.export_blend',
        'description': '',
        'icon': 'BLENDER',
        'number': 200,
        'ext': 'blend'
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
