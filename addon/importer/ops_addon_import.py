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

        return {'FINISHED'}


class SPIO_OT_enable_addon(bpy.types.Operator):
    bl_idname = 'spio.enable_addon'
    bl_label = 'Enable Addon'

    module: StringProperty()
    remove_cache: BoolProperty()

    def execute(self, context):
        try:
            if not self.remove_cache:
                bpy.ops.preferences.addon_enable("INVOKE_DEFAULT", module=self.module)
            # update cache
            cache_addons = context.window_manager.spio_cache_addons.split('$$$')
            if self.module in cache_addons:
                cache_addons.remove(self.module)
                context.window_manager.spio_cache_addons = '$$$'.join(cache_addons)

        except Exception as e:
            self.report({"ERROR"}, str(e))

        return {'FINISHED'}


def draw_addon_to_install(self, context):
    layout = self.layout
    layout.popover(panel="SPIO_PT_InstallAddon", text='Addon to install:', icon='COLLAPSEMENU')


def pop_up_addon_list(self, context):
    if context.window_manager.spio_is_pop_up_addon is False:
        context.window_manager.popup_menu(draw_addon_to_install, title='Enable Addon')
        context.window_manager.spio_is_pop_up_addon = True

    if context.window_manager.spio_cache_addons == '':
        context.window_manager.spio_cache_addons = False


def register():
    bpy.types.WindowManager.spio_cache_addons = StringProperty(update=pop_up_addon_list)
    bpy.types.WindowManager.spio_is_pop_up_addon = BoolProperty(default=False)

    bpy.utils.register_class(SPIO_OT_import_addon)
    bpy.utils.register_class(SPIO_OT_enable_addon)


def unregister():
    del bpy.types.WindowManager.spio_cache_addons
    del bpy.types.WindowManager.spio_is_pop_up_addon

    bpy.utils.unregister_class(SPIO_OT_import_addon)
    bpy.utils.unregister_class(SPIO_OT_enable_addon)
