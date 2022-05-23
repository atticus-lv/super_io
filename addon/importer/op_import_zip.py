import bpy
import os
import zipfile

from bpy.props import StringProperty
from ...preferences.prefs import get_pref
from ...ops.op_image_io import get_dir


class SPIO_OT_import_pbr_zip(bpy.types.Operator):
    bl_idname = 'spio.import_pbr_zip'
    bl_label = 'Import Zips as PBR Materials'

    filepath: StringProperty()  # list of filepath, join with$$

    def execute(self, context):
        if bpy.data.filepath != '':
            extract_dir = os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), 'textures')
        else:
            extract_dir = get_dir()

        for filepath in self.filepath.split('$$'):
            dir_name = os.path.basename(filepath).split('.')[0]  # extract folder
            # name
            extract = os.path.join(extract_dir, dir_name)
            if not os.path.exists(extract):
                os.makedirs(extract)

            if not os.path.isfile(filepath):
                self.report({'ERROR'}, f'{filepath} is not a zip file')
                return {'CANCELLED'}

            # extract zip file
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract)

            # if contains a folder, move to that dir
            if len(os.listdir(extract)) == 1:
                file_name = os.listdir(extract)[0]
                p = os.path.join(extract, file_name)
                if os.path.isdir(p):
                    extract = p
            # build pbr material from extracted textures
            bpy.ops.spio.create_principled_set_up_material(directory=extract + '/', use_context_space=False,
                                                           mark_asset=False)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SPIO_OT_import_pbr_zip)

def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_pbr_zip)
