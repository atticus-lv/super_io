importer_addon = {
    'ADDONS_BLEND_MATERIAL': 'spio.load_and_assign_material',
    'ADDONS_BLEND_WORLD': 'spio.load_and_assign_world',
    'ADDONS_INSTALL_ADDON': 'spio.import_addon',
    'ADDONS_IMPORT_IES': 'spio.import_ies',
    'ADDONS_IMPORT_PBR_ZIP': 'spio.import_pbr_zip',
}

# v1

addon_lib = {
    'ADDONS_BLEND_MATERIAL': {
        'bl_idname': 'spio.load_and_assign_material',
        'name': 'Append and Assign material',
        'description': 'Import material from a single file and assign it to active object',
        'icon': 'MATERIAL',
        'number': 101
    },
    'ADDONS_BLEND_WORLD': {
        'bl_idname': 'spio.load_and_assign_world',
        'name': 'Append and Assign world',
        'description': 'Import world from a single file and set it as context world',
        'icon': 'WORLD',
        'number': 102
    },
    'ADDONS_INSTALL_ADDON': {
        'bl_idname': 'spio.import_addon',
        'name': 'Install Addon (.py/.zip)',
        'description': 'Import and Install extra_addon',
        'icon': 'COMMUNITY',
        'number': 103
    },
    'ADDONS_IMPORT_IES': {
        'bl_idname': 'spio.import_ies',
        'name': 'Import IES (.ies)',
        'description': 'Import IES file as light',
        'icon': 'LIGHT_SPOT',
        'number': 104
    },
    'ADDONS_IMPORT_PBR_ZIP': {
        'bl_idname': 'spio.import_ies',
        'name': 'Import IES (.ies)',
        'description': 'Import IES file as light',
        'icon': 'MATERIAL',
        'number': 105
    },
}
