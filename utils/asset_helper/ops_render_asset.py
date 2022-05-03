import bpy
import os
from subprocess import run
from ...preferences import get_pref


class SPIO_OT_render_hdri_preview(bpy.types.Operator):
    bl_idname = "spio.render_hdri_preview"
    bl_label = "Render HDRI Preview from Clipboard"
    bl_description = "Render HDRI Preview"
    bl_options = {'INTERNAL', 'UNDO'}

    resolution: bpy.props.EnumProperty(name='Resolution', items=[
        ('128', '128', ''),
        ('256', '256', ''),
        ('512', '512', ''),
    ], default='256')

    scene: bpy.props.EnumProperty(name='Scene', items=[
        ('hdr_sphere.blend', 'Reflection Ball', ''),
        ('hdri_plane.blend', 'Plane with Balls', ''), ],
                                  default='hdri_plane.blend')

    re_generate: bpy.props.BoolProperty(name='Regenerate', description='When there exist preview, regenerate it',
                                        default=True)
    # copy_after_resize: bpy.props.BoolProperty(name='Copy after generate (Only Win)',
    #                                           description='Copy files to clipboard after generate', default=True)
    suffix: bpy.props.StringProperty(name='Suffix', default='_pv')

    filepaths = None
    clipboard = None

    def invoke(self, context, event):
        self.filepaths = None

        from ...clipboard.clipboard import Clipboard
        self.clipboard = Clipboard()

        filepaths = self.clipboard.pull_files_from_clipboard(get_pref().force_unicode)
        if len(filepaths) == 0:
            self.report({'ERROR'}, 'No file found in clipboard!')
            return {'CANCELLED'}

        self.filepaths = filepaths
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        row = layout.split(factor=0.3)

        row.label(text=f'{len(self.filepaths)} files', icon='DUPLICATE')
        row.label(text='Need a few minutes')

        box = layout.box()
        box.use_property_split = True
        box.prop(self, 'scene')
        box.prop(self, 'resolution')
        box.prop(self, 're_generate')
        box.prop(self, 'suffix')
        box.prop(self, 'copy_after_resize')

    def execute(self, context):
        scripts_path = os.path.join(os.path.dirname(__file__), 'script_render_pv.py')
        blend_path = os.path.join(os.path.dirname(__file__), 'render_scene', self.scene)

        for filepath in self.filepaths:
            name = os.path.basename(filepath)
            base, stp, ext = name.rpartition('.')

            out_png = os.path.join(os.path.dirname(filepath), base + self.suffix + '.' + 'jpg')

            if os.path.exists(out_png) and not self.re_generate: continue
            try:
                cmd = [bpy.app.binary_path]
                cmd.append("--background")
                cmd.append("--factory-startup")
                cmd.append("--python")
                cmd.append(scripts_path)
                cmd.append('--')
                cmd.append(filepath)
                cmd.append(blend_path)
                cmd.append(self.resolution)
                cmd.append(out_png)
                run(cmd)
            except Exception as e:
                print(f'Resize image "{name}" failed:', e)

        # if self.copy_after_resize:
        #     self.clipboard.push_to_clipboard(self.filepaths)

        return {'FINISHED'}


class SPIO_OI_render_world_asset_preview(bpy.types.Operator):
    bl_idname = "spio.render_world_asset_preview"
    bl_label = "Render World Asset Preview"
    bl_description = "Render World Asset Preview"
    bl_options = {'INTERNAL', 'UNDO'}

    resolution: bpy.props.EnumProperty(name='Resolution', items=[
        ('128', '128', ''),
        ('256', '256', ''),
        ('512', '512', ''),
    ], default='256')

    scene: bpy.props.EnumProperty(name='Scene', items=[
        ('hdr_sphere.blend', 'Reflection Ball', ''),
        ('hdri_plane.blend', 'Plane with Balls', ''), ],
                                  default='hdri_plane.blend')

    overwrite: bpy.props.BoolProperty(name='Overwrite',
                                      default=True)
    suffix: bpy.props.StringProperty(name='Suffix', default='_pv')

    filepaths = None
    clipboard = None
    match_worlds = None

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files and bpy.data.filepath != ''

    def invoke(self, context, event):
        current_library_name = context.area.spaces.active.params.asset_library_ref
        match_obj = [asset_file.local_id for asset_file in context.selected_asset_files if
                     current_library_name == "LOCAL"]
        match_names = [obj.name for obj in match_obj if isinstance(obj, bpy.types.World)]
        self.match_worlds = match_names
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        row = layout.split(factor=0.3)

        row.label(text=f'{len(self.match_worlds)} worlds', icon='WORLD')
        row.label(text='Need a few minutes')

        box = layout.box()
        box.use_property_split = True
        box.prop(self, 'scene')
        box.prop(self, 'resolution')
        box.prop(self, 'overwrite')
        box.prop(self, 'suffix')

    def execute(self, context):
        # WORLD, SOURCEPATH, BLENDEPATH, SIZE, OUTPATH = argv
        scripts_path = os.path.join(os.path.dirname(__file__), 'script_render_world_asset_pv.py')
        blend_path = os.path.join(os.path.dirname(__file__), 'render_scene', self.scene)

        for world in self.match_worlds:
            out_png = os.path.join(
                os.path.join(os.path.dirname(bpy.data.filepath), 'asset_previews', world + self.suffix + '.' + 'png'))
            if os.path.exists(out_png) and not self.overwrite: continue
            try:
                cmd = [bpy.app.binary_path]
                cmd.append("--background")
                cmd.append("--factory-startup")
                cmd.append("--python")
                cmd.append(scripts_path)
                cmd.append('--')
                cmd.append(world)  # world
                cmd.append(bpy.data.filepath)  # current file
                cmd.append(blend_path)  # render scene file
                cmd.append(self.resolution)
                cmd.append(out_png)
                run(cmd)
            except Exception as e:
                print(f'Render image "{world}" failed:', e)

        return {'FINISHED'}


def register():
    # bpy.utils.register_class(SPIO_OT_render_hdri_preview)
    bpy.utils.register_class(SPIO_OI_render_world_asset_preview)


def unregister():
    # bpy.utils.unregister_class(SPIO_OT_render_hdri_preview)
    bpy.utils.unregister_class(SPIO_OI_render_world_asset_preview)
