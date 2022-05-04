import bpy
import os
from subprocess import run
from ...preferences import get_pref

from ...ui.t3dn_bip import previews

# Image items
####################

__tempPreview__ = {}  # store in global, delete in unregister

image_extensions = ('.png', '.jpg', '.jpeg')


# image_extensions = ('.bip')

def check_extension(input_string: str, extensions: set) -> bool:
    for ex in extensions:
        if input_string.endswith(ex): return True


def clear_preview_cache():
    for preview in __tempPreview__.values():
        previews.remove(preview)
    __tempPreview__.clear()


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
    dir = os.path.join(os.path.dirname(__file__), "render_scene")
    return enum_thumbnails_from_dir(dir, context)


class SPIO_OI_render_world_asset_preview(bpy.types.Operator):
    bl_idname = "spio.render_world_asset_preview"
    bl_label = "Render World Asset Preview"
    bl_description = "Save your file first and select the local assets"
    bl_options = {'INTERNAL', 'UNDO'}

    resolution: bpy.props.EnumProperty(name='Resolution', items=[
        ('128', '128', ''),
        ('256', '256', ''),
        ('512', '512', ''),
    ], default='256')

    scene: bpy.props.EnumProperty(name='Scene', items=enum_world_render_preset)

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
        subbox = box.row()
        subbox.separator(factor=10)
        subbox.template_icon_view(self, "scene", scale=6, scale_popup=5, show_labels=False)
        subbox.separator(factor=10)
        box.prop(self, 'resolution')
        box.prop(self, 'overwrite')
        box.prop(self, 'suffix')

    def execute(self, context):
        # WORLD, SOURCEPATH, BLENDEPATH, SIZE, OUTPATH = argv
        scripts_path = os.path.join(os.path.dirname(__file__), 'script_render_world_asset_pv.py')
        blend_path = os.path.join(os.path.dirname(__file__), 'render_scene', self.scene[:-4] + '.blend')

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

        self.report({'INFO'}, f'Finished')
        return {'FINISHED'}


from ...ui.ui_panel import import_icon, export_icon, get_pref


class SPIO_MT_asset_browser_menu(bpy.types.Menu):
    bl_label = "Asset Helper"
    bl_idname = 'SPIO_MT_asset_browser_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('wm.super_import', icon_value=import_icon.get_image_icon_id())
        layout.operator('wm.super_export', icon_value=export_icon.get_image_icon_id())


def asset_browser(self, context):
    layout = self.layout
    if get_pref().asset_helper:
        layout.menu(SPIO_MT_asset_browser_menu.bl_idname)


def register():
    img_preview = previews.new(max_size=(512, 512))
    img_preview.img_dir = ""
    img_preview.img = ()
    __tempPreview__["spio_asset_thumbnails"] = img_preview

    # bpy.utils.register_class(SPIO_OT_render_hdri_preview)
    bpy.utils.register_class(SPIO_OI_render_world_asset_preview)
    if bpy.app.version > (3, 0, 0):
        bpy.utils.register_class(SPIO_MT_asset_browser_menu)
        bpy.types.ASSETBROWSER_MT_editor_menus.append(asset_browser)


def unregister():
    # bpy.utils.unregister_class(SPIO_OT_render_hdri_preview)
    bpy.utils.unregister_class(SPIO_OI_render_world_asset_preview)
    if bpy.app.version > (3, 0, 0):
        bpy.utils.unregister_class(SPIO_MT_asset_browser_menu)
        bpy.types.ASSETBROWSER_MT_editor_menus.remove(asset_browser)

    clear_preview_cache()
