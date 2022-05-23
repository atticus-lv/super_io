import os.path

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty
from .ops_mark_asset import redraw_window

import bpy


class SPIO_OT_set_preview_to_selected_assets(bpy.types.Operator):
    bl_idname = "spio.set_preview_to_selected_assets"
    bl_label = "Set Preview to Selected Assets"
    bl_options = {"UNDO_GROUPED"}

    clipboard = None
    filepaths = None

    match_type: EnumProperty(name='Match Type',
                             items=[
                                 ('NAME', 'Name', ''),
                                 ('NONE', 'None', ''), ])

    suffix_type: EnumProperty(name='Type',
                              items=[
                                  ('IGNORE', 'Ignore Suffix', ''),
                                  ('ADD', 'Add Suffix', ''), ], default='IGNORE',
                              description='Match the image name with suffix removed/add to the asset name')

    suffix: StringProperty(name='Suffix',
                           description='', default='_pv')

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'match_type',expand = True)
        if self.match_type == 'NAME':
            layout.prop(self, 'suffix_type')
            layout.prop(self, 'suffix')
        else:
            layout.label(text='Selected assets will be set to the same preview',icon = 'ERROR')

    def invoke(self, context, event):
        self.clipboard = None

        from ...clipboard.clipboard import Clipboard
        from ...preferences.prefs import get_pref

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
        # from pathlib import Path
        # library_path = Path(context.preferences.filepaths.asset_libraries.get(current_library_name).path)
        # asset_fullpath = library_path / asset_file.relative_path
        # print(f"{asset_fullpath} is selected in the asset browser.")
        # print(f"It is located in a user library named '{current_library_name}'")

        if self.match_type == 'NONE':
            for obj in match_obj:
                override = context.copy()
                override['id'] = obj
                bpy.ops.ed.lib_id_load_custom_preview(override, filepath=self.filepaths[0])
        else:
            for path in self.filepaths:
                basename = os.path.basename(path)
                base, sep, ext = basename.rpartition('.')

                if self.suffix == '':
                    name = base
                else:
                    if self.suffix_type == 'IGNORE':
                        name = base[:-len(self.suffix)]
                    else:
                        name = base + self.suffix

                if name in match_names:
                    index = match_names.index(name)
                    obj = match_obj[index]
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
