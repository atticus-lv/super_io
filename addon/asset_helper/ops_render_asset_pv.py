import bpy
import os
from ...preferences.prefs import get_pref
from ...ui.t3dn_bip import previews

# Image items
####################

__tempPreview__ = {}  # store in global, delete in unregister

# image_extensions = ('.png', '.jpg', '.jpeg')
image_extensions = ('.bip', '.png')


def check_extension(input_string: str, extensions: set) -> bool:
    for ex in extensions:
        if input_string.endswith(ex): return True


def clear_preview_cache():
    for preview in __tempPreview__.values():
        previews.remove(preview)
    __tempPreview__.clear()


def run_cmd(script_filepath, *args):
    from subprocess import run
    cmd = bpy.app.binary_path
    arg = [
        "--background",
        "--factory-startup",
        "--python",
        script_filepath,
        "--",
    ]

    arg += args
    arg.insert(0, cmd)

    run(arg)


def enum_thumbnails_from_dir(directory, context):
    enum_items = []
    if context is None: return enum_items

    # store
    image_preview = __tempPreview__["spio_asset_thumbnails"]

    if directory == image_preview.img_dir:
        return image_preview.img

    if directory and os.path.exists(directory):
        image_names = []
        for fn in os.listdir(directory):
            if check_extension(fn.lower(), image_extensions):
                # check that a bip file exists
                name = os.path.splitext(fn)[0]
                if name + '.bip' in image_names: continue
                if name + '.png' in image_names: image_names.remove(name + '.png')

                image_names.append(fn)

        for i, name in enumerate(image_names):
            filepath = os.path.join(directory, name)

            icon = image_preview.get(name)
            if not icon:
                thumbnail = image_preview.load(name, filepath, 'IMAGE')
            else:
                thumbnail = image_preview[name]
            enum_items.append((name, name, "", thumbnail.icon_id, i))  # item: sign,display,description,icon,index

    image_preview.img = enum_items
    image_preview.img_dir = directory

    return image_preview.img


def enum_world_render_preset(self, context):
    dir = os.path.join(os.path.dirname(__file__), "hdr_scene")
    return enum_thumbnails_from_dir(dir, context)


def enum_mat_render_preset(self, context):
    dir = os.path.join(os.path.dirname(__file__), "mat_scene")
    return enum_thumbnails_from_dir(dir, context)


class render_asset_preview:
    bl_description = "Select local assets and save file"
    bl_options = {'INTERNAL', 'UNDO'}

    render_type = 'WORLD'  # WORLD, MAT

    # scene
    resolution: bpy.props.EnumProperty(name='Resolution', items=[
        ('128', '128', ''),
        ('256', '256', ''),
        ('512', '512', ''),
    ], default='256')
    samples: bpy.props.EnumProperty(name='Samples', items=[
        ('8', '8', ''),
        ('16', '16', ''),
        ('32', '32', ''),
        ('64', '64', ''),
        ('128', '128', ''), ], default='32')
    denoise: bpy.props.BoolProperty(name='Denoise', default=False)

    overwrite: bpy.props.BoolProperty(name='Overwrite',
                                      description='Overwrite existing files while rendering',
                                      default=True)
    suffix: bpy.props.StringProperty(name='Suffix',
                                     default='_pv')

    filepaths = None
    clipboard = None
    match_obj = None

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files and bpy.data.filepath != ''

    def invoke(self, context, event):
        d = {'WORLD': 'World', 'MATERIAL': 'Material'}

        match_obj = self.get_match_obj(context)
        self.match_obj = [obj.name for obj in match_obj if isinstance(obj, getattr(bpy.types, d[self.render_type]))]

        if len(match_obj) == 0:
            self.report({'ERROR'}, 'Select local assets!')
            return {'CANCELLED'}

        elif bpy.data.is_dirty:
            self.report({'ERROR'}, 'File have been change, save it first!')

            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=250)

    def get_match_obj(self, context):
        current_library_name = context.area.spaces.active.params.asset_library_ref
        match_obj = [asset_file.local_id for asset_file in context.selected_asset_files if
                     current_library_name == "LOCAL"]
        return match_obj

    def draw_settings(self, context, layout):
        layout.label(text=f'{len(self.match_obj)} {self.render_type.title()} to render',
                     icon=self.render_type)

        box = layout.box()
        box.use_property_split = True
        subbox = box.row()
        subbox.alignment = 'RIGHT'
        subbox.label(text='Style')
        subbox.template_icon_view(self, "scene", scale=6.5, scale_popup=4, show_labels=False)
        subbox.separator(factor=2)

        if hasattr(self, 'displacement'):
            box.prop(self, 'displacement')

        box = layout.box()
        col = box.column(align=True)
        col.use_property_split = True
        col.prop(self, 'resolution')
        col.prop(self, 'samples')
        col.prop(self, 'denoise')

        box = layout.box()
        col = box.column(align=True)
        col.use_property_split = True
        col.prop(self, 'overwrite')
        col.prop(self, 'suffix')

        layout.label(text='This could take a few minutes', icon='INFO')


# render world asset preview
class SPIO_OI_render_world_asset_preview(render_asset_preview, bpy.types.Operator):
    bl_idname = "spio.render_world_asset_preview"
    bl_label = "Render World Asset Preview"

    render_type = 'WORLD'
    scene: bpy.props.EnumProperty(name='Scene', items=enum_world_render_preset)

    def draw(self, context):
        layout = self.layout

        self.draw_settings(context, layout)

    def execute(self, context):
        # WORLD, SOURCEPATH, BLENDEPATH, SIZE, OUTPATH = argv
        scripts_path = os.path.join(os.path.dirname(__file__), 'script_render_world_asset_pv.py')
        blend_path = os.path.join(os.path.dirname(__file__), 'hdr_scene', self.scene[:-4] + '.blend')

        for world in self.match_obj:
            out_png = os.path.join(
                os.path.join(os.path.dirname(bpy.data.filepath), 'asset_previews', world + self.suffix + '.' + 'png'))
            if os.path.exists(out_png) and not self.overwrite: continue
            try:
                args = {
                    'WORLD': world,
                    'SOURCEPATH': bpy.data.filepath,
                    'BLENDPATH': blend_path,
                    'OUTPATH': out_png,
                    'SIZE': self.resolution,
                    'SAMPLES': self.samples,
                    'DENOISE': '1' if self.denoise else '0',
                }
                run_cmd(scripts_path, *args.values())

            except Exception as e:
                print(f'Render image "{world}" failed:', e)

        bpy.ops.wm.path_open(filepath=os.path.join(os.path.dirname(bpy.data.filepath), 'asset_previews'))

        self.report({'INFO'}, f'Finished')
        return {'FINISHED'}


# render material asset preview
class SPIO_OI_render_material_asset_preview(render_asset_preview, bpy.types.Operator):
    bl_idname = "spio.render_material_asset_preview"
    bl_label = "Render Material Asset Preview"

    render_type = 'MATERIAL'
    scene: bpy.props.EnumProperty(name='Scene', items=enum_mat_render_preset)
    displacement: bpy.props.BoolProperty(name='Displacement', default=False)

    def draw(self, context):
        layout = self.layout

        self.draw_settings(context, layout)

    def execute(self, context):
        scripts_path = os.path.join(os.path.dirname(__file__), 'script_render_material_asset_pv.py')
        blend_path = os.path.join(os.path.dirname(__file__), 'mat_scene', self.scene[:-4] + '.blend')

        for material in self.match_obj:
            out_png = os.path.join(
                os.path.join(os.path.dirname(bpy.data.filepath), 'asset_previews',
                             material + self.suffix + '.' + 'png'))
            if os.path.exists(out_png) and not self.overwrite: continue
            try:
                args = {
                    'MAT': material,
                    'SOURCEPATH': bpy.data.filepath,
                    'BLENDPATH': blend_path,
                    'OUTPATH': out_png,
                    'SIZE': self.resolution,
                    'SAMPLES': '64',
                    'DENOISE': '1',
                    'DISPLACE': '1' if self.displacement else '0',
                }
                run_cmd(scripts_path, *args.values())

            except Exception as e:
                print(f'Render image "{material}" failed:', e)

        bpy.ops.wm.path_open(filepath=os.path.join(os.path.dirname(bpy.data.filepath), 'asset_previews'))

        self.report({'INFO'}, f'Finished')
        return {'FINISHED'}


from ...ui.ui_panel import get_pref
from ...preferences.data_icon import G_ICON_ID


class SPIO_MT_asset_browser_menu(bpy.types.Menu):
    bl_label = "Asset Helper"
    bl_idname = 'SPIO_MT_asset_browser_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('wm.super_import', icon_value=G_ICON_ID['import'])
        layout.operator('wm.super_export', icon_value=G_ICON_ID['export'])

        layout.separator()
        layout.operator('spio.batch_image_operate', icon='RENDERLAYERS')
        layout.separator()
        layout.operator('spio.mark_helper', icon='ASSET_MANAGER')


def asset_browser(self, context):
    layout = self.layout
    if get_pref().asset_helper:
        layout.menu('SPIO_MT_asset_browser_menu')


def register():
    img_preview = previews.new(max_size=(512, 512))
    img_preview.img_dir = ""
    img_preview.img = ()
    __tempPreview__["spio_asset_thumbnails"] = img_preview

    # bpy.utils.register_class(SPIO_OT_render_hdri_preview)
    bpy.utils.register_class(SPIO_OI_render_world_asset_preview)
    bpy.utils.register_class(SPIO_OI_render_material_asset_preview)

    if bpy.app.version >= (3, 0, 0):
        bpy.utils.register_class(SPIO_MT_asset_browser_menu)
        bpy.types.ASSETBROWSER_MT_editor_menus.append(asset_browser)


def unregister():
    if bpy.app.version >= (3, 0, 0):
        bpy.utils.unregister_class(SPIO_MT_asset_browser_menu)
        bpy.types.ASSETBROWSER_MT_editor_menus.remove(asset_browser)

    # bpy.utils.unregister_class(SPIO_OT_render_hdri_preview)
    bpy.utils.unregister_class(SPIO_OI_render_world_asset_preview)
    bpy.utils.unregister_class(SPIO_OI_render_material_asset_preview)

    clear_preview_cache()

