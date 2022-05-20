import bpy
import os
import zipfile

from bpy.props import StringProperty, BoolProperty, EnumProperty


class SPIO_OT_import_addon(bpy.types.Operator):
    bl_idname = 'spio.import_addon'
    bl_label = 'Import Addon'

    filepath: StringProperty()  # list of filepath, join with$$

    def execute(self, context):
        # bpy.ops.screen.userpref_show()
        bpy.ops.preferences.addon_install(overwrite=True, target='DEFAULT', filepath=self.filepath,
                                          filter_folder=True, filter_python=False, filter_glob="*.py;*.zip")

        if self.filepath.endswith('.py'):
            module = os.path.split(self.filepath)[1][:-3]  # remove .py
        else:
            zip = zipfile.ZipFile(self.filepath)
            module = zip.namelist()[0].split('/')[0]  # get the dir name that blender use to register in the preference

        cache_addons = context.window_manager.spio_cache_addons.split('$$$')

        if module not in cache_addons:
            cache_addons.append(module)
            context.window_manager.spio_cache_addons = '$$$'.join(cache_addons)
            # redraw to show cache panel
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

        def draw_addon_to_install(self, context):
            layout = self.layout
            layout.operator_context = 'INVOKE_DEFAULT'
            op = layout.operator('preferences.addon_enable', icon='CHECKBOX_DEHLT', text=module)
            op.module = module

        context.window_manager.popup_menu(draw_addon_to_install, title='Enable Add-on')
        return {'FINISHED'}


class SPIO_OT_enable_addon(bpy.types.Operator):
    bl_idname = 'spio.enable_addon'
    bl_label = 'Enable Addon'
    bl_options = {'UNDO_GROUPED'}

    module: StringProperty()
    remove_cache: BoolProperty()

    def execute(self, context):
        from addon_utils import enable

        try:
            if not self.remove_cache:
                enable(self.module)
            # update cache
            cache_addons = context.window_manager.spio_cache_addons.split('$$$')
            if self.module in cache_addons:
                cache_addons.remove(self.module)
                context.window_manager.spio_cache_addons = '$$$'.join(cache_addons)

        except Exception as e:
            self.report({"ERROR"}, str(e))

        return {'FINISHED'}


def register():
    bpy.types.WindowManager.spio_cache_addons = StringProperty()

    bpy.utils.register_class(SPIO_OT_import_addon)
    bpy.utils.register_class(SPIO_OT_enable_addon)


def unregister():
    del bpy.types.WindowManager.spio_cache_addons

    bpy.utils.unregister_class(SPIO_OT_import_addon)
    bpy.utils.unregister_class(SPIO_OT_enable_addon)
