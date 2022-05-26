default_blend_lib = {
    'Collection': 'collections',
    'Material': 'materials',
    'World': 'worlds',
    'Object': 'objects',
    'NodeTree': 'node_groups'
}


import_lib_blend = {
    'APPEND_BLEND_MATERIAL': {
        'bl_idname': 'spio.batch_import_blend',
        'name': 'Append All Materials',
        'description': '',
        'ext': 'blend',
        'icon': 'MATERIAL',
        'prop_list': {
            'action': 'APPEND',
            'sub_path': 'Material',
            'data_type': 'materials'
        },
    },
    'APPEND_BLEND_COLLECTION': {
        'bl_idname': 'spio.batch_import_blend',
        'name': 'Append All Collections',
        'description': '',
        'ext': 'blend',
        'icon': 'OUTLINER_COLLECTION',
        'prop_list': {
            'action': 'APPEND',
            'sub_path': 'Collection',
            'data_type': 'collections'
        },
    },
    'APPEND_BLEND_OBJECT': {
        'bl_idname': 'spio.batch_import_blend',
        'name': 'Append All Object',
        'description': '',
        'ext': 'blend',
        'prop_list': {
            'action': 'APPEND',
            'sub_path': 'Object',
            'data_type': 'objects'
        },
    },
    'APPEND_BLEND_WORLD': {
        'bl_idname': 'spio.batch_import_blend',
        'name': 'Append All Worlds',
        'description': '',
        'ext': 'blend',
        'prop_list': {
            'action': 'APPEND',
            'sub_path': 'World',
            'data_type': 'worlds'
        },
    },
    'APPEND_BLEND_NODETREE': {
        'bl_idname': 'spio.batch_import_blend',
        'name': 'Append All Materials',
        'description': '',
        'ext': 'blend',
        'prop_list': {
            'action': 'APPEND',
            'sub_path': 'NodeTree',
            'data_type': 'node_groups'
        },
    }
}
