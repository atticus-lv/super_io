import os.path

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty
from .ops_mark_asset import redraw_window


# class SPIO_OT_set_asset_thumb_from_clipboard_image(bpy.types.Operator):
#     """Generate selected asset' preview from clipboard images (match by name)"""
#     bl_label = 'Set from Clipboard Images'
#     bl_idname = 'spio.set_asset_thumb_from_clipboard_image'
#
#     match_obj = []
#     clipboard = None
#     filepaths = None
#
#     check_selected_objects: BoolProperty(name='Selected objects', default=True)
#     check_worlds: BoolProperty(name='Worlds', default=False)
#     check_materials: BoolProperty(name='Materials', default=False)
#     re_generate: bpy.props.BoolProperty(name='Regenerate', description='When there exist preview, regenerate it',
#                                         default=True)
#     suffix: StringProperty(name='Remove Suffix',
#                            description='Match the image name with suffix removed to the asset name', default='_pv')
#
#     @classmethod
#     def poll(cls, context):
#         return (
#                 len(context.selected_objects) != 0 or
#                 len(bpy.data.materials) != 0 or
#                 len(bpy.data.worlds) != 0
#         )
#
#     def invoke(self, context, event):
#         self.match_obj = []
#         self.clipboard = None
#
#         from ...clipboard.clipboard import Clipboard
#         from ...preferences import get_pref
#
#         self.clipboard = Clipboard()
#         filepaths = self.clipboard.pull_files_from_clipboard(force_unicode=get_pref().force_unicode)
#         if len(filepaths) == 0:
#             self.report({'ERROR'}, 'No file found in clipboard!')
#             return {'CANCELLED'}
#
#         self.filepaths = filepaths
#
#         return context.window_manager.invoke_props_dialog(self, width=400)
#
#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.prop(self, 'check_selected_objects')
#         layout.prop(self, 'check_worlds')
#         layout.prop(self, 'check_materials')
#         box = layout.box()
#         box.prop(self, 're_generate')
#         box.prop(self, 'suffix')
#
#         box.label(text="Heavy image file(>20MB) will be skipped", icon='INFO')
#
#     def execute(self, context):
#         if self.check_selected_objects:
#             for obj in context.selected_objects:
#                 if obj.asset_data:
#                     self.match_obj.append(obj)
#
#         if self.check_worlds:
#             for world in bpy.data.worlds:
#                 if world.asset_data:
#                     self.match_obj.append(world)
#
#         if self.check_materials:
#             for material in bpy.data.materials:
#                 if material.asset_data:
#                     self.match_obj.append(material)
#
#         match_names = [obj.name for obj in self.match_obj]
#
#         for path in self.filepaths:
#             basename = os.path.basename(path)
#             base, sep, ext = basename.rpartition('.')
#
#             if self.suffix == '':
#                 name = base
#             else:
#                 name = base[:-len(self.suffix)]
#                 print(name)
#             if name in match_names:
#                 index = match_names.index(name)
#                 obj = self.match_obj[index]
#                 # regenerate thumb
#                 if not self.re_generate and obj.preview is not None:
#                     continue
#                 # get asset data
#                 override = context.copy()
#                 override['id'] = obj
#                 bpy.ops.ed.lib_id_load_custom_preview(override, filepath=path)
#
#         redraw_window()
#
#         return {"FINISHED"}


import bpy
from pathlib import Path


class SPIO_OT_set_preview_to_selected_assets(bpy.types.Operator):
    bl_idname = "spio.set_preview_to_selected_assets"
    bl_label = "Set Preview to Selected Assets"

    clipboard = None
    filepaths = None
    re_generate: bpy.props.BoolProperty(name='Overwrite', description='When there exist preview, Overwrite it',
                                        default=True)
    suffix: StringProperty(name='Remove Suffix',
                           description='Match the image name with suffix removed to the asset name', default='_pv')

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files

    def invoke(self, context, event):
        self.clipboard = None

        from ...clipboard.clipboard import Clipboard
        from ...preferences import get_pref

        self.clipboard = Clipboard()
        filepaths = self.clipboard.pull_files_from_clipboard(force_unicode=get_pref().force_unicode)
        if len(filepaths) == 0:
            self.report({'ERROR'}, 'No file found in clipboard!')
            return {'CANCELLED'}

        self.filepaths = filepaths

        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        current_library_name = context.area.spaces.active.params.asset_library_ref
        match_obj = [asset_file.local_id for asset_file in context.selected_asset_files if
                     current_library_name == "LOCAL"]
        match_names = [obj.name for obj in match_obj]

        # else:
        # library_path = Path(context.preferences.filepaths.asset_libraries.get(current_library_name).path)
        #     asset_fullpath = library_path / asset_file.relative_path
        #     print(f"{asset_fullpath} is selected in the asset browser.")
        #     print(f"It is located in a user library named '{current_library_name}'")

        for path in self.filepaths:
            basename = os.path.basename(path)
            base, sep, ext = basename.rpartition('.')

            if self.suffix == '':
                name = base
            else:
                name = base[:-len(self.suffix)]
                print(name)
            if name in match_names:
                index = match_names.index(name)
                obj = match_obj[index]
                # regenerate thumb
                if not self.re_generate and obj.preview is not None:
                    continue
                # get asset data
                override = context.copy()
                override['id'] = obj
                bpy.ops.ed.lib_id_load_custom_preview(override, filepath=path)

        redraw_window()

        return {"FINISHED"}


def register():
    # bpy.utils.register_class(SPIO_OT_set_asset_thumb_from_clipboard_image)
    bpy.utils.register_class(SPIO_OT_set_preview_to_selected_assets)


def unregister():
    # bpy.utils.unregister_class(SPIO_OT_set_asset_thumb_from_clipboard_image)
    bpy.utils.unregister_class(SPIO_OT_set_preview_to_selected_assets)
