import bpy
from ..ops.core import get_pref
from ..preferences import SPIO_Preference
from ..ops.ops_super_import import import_icon
from ..ops.ops_super_export import export_icon


class SidebarSetup:
    bl_category = "SPIO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(cls, context):
        return get_pref().use_N_panel


class SPIO_PT_PrefPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "LEFT"
        pref = get_pref()

        row = layout
        row = row.row(align=True)
        row.prop(pref, 'ui', expand=True, emboss=False)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        if pref.ui == 'SETTINGS':
            SPIO_Preference.draw_settings(pref, context, layout)
        elif pref.ui == 'CONFIG':
            SPIO_Preference.draw_config(pref, context, layout)
        elif pref.ui == 'KEYMAP':
            SPIO_Preference.draw_keymap(pref, context, layout)
        elif pref.ui == 'URL':
            SPIO_Preference.draw_url(pref, context, layout)


class SPIO_PT_PrefPanel_283(SPIO_PT_PrefPanel):
    bl_label = ' '
    bl_options = {'DEFAULT_CLOSED'}


class SPIO_PT_PrefPanel_300(SPIO_PT_PrefPanel):
    bl_options = {'HEADER_LAYOUT_EXPAND','DEFAULT_CLOSED'}


class SPIO_PT_ImportPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Super IO'

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.separator()
        row.operator("wm.super_import", icon_value=import_icon.get_image_icon_id())
        row.operator("wm.super_export", icon_value=export_icon.get_image_icon_id())
        row.separator()


class SPIO_PT_InstallAddon(SidebarSetup, bpy.types.Panel):
    bl_label = 'Install Addon'

    @classmethod
    def poll(self, context):
        return context.window_manager.spio_cache_addons != ''

    def draw(self, context):
        layout = self.layout
        if context.window_manager.spio_cache_addons != '':
            for name in context.window_manager.spio_cache_addons.split('$$$'):
                if name == '': continue
                op = layout.operator('spio.enable_addon', text=f'Enable {name}')
                op.module = name
                op.remove_cache = False

        op = layout.operator('spio.enable_addon', text='Clear Cache')
        op.module = name
        op.remove_cache = True


class SPIO_PT_AssetHelper(SidebarSetup, bpy.types.Panel):
    bl_label = 'Asset Helper'

    @classmethod
    def poll(self, context):
        return get_pref().experimental and bpy.app.version >= (3, 0, 0)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.15
        row.operator('spio.mark_object_asset', text='Mark Selected Objects As Asset', icon='ASSET_MANAGER')

        row = layout.row()
        row.scale_y = 1.15
        row.operator('spio.clear_object_asset', text='Clear Selected Asset', icon='X')


class SPIO_PT_ListFilterPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_category = ''
    bl_label = "Filter Type"
    bl_idname = "SPIO_PT_ListFilterPanel"

    def draw(self, context):
        """UI code for the filtering/sorting/search area."""
        filter = context.window_manager.spio_filter
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(filter, 'show_import')
        layout.prop(filter, 'show_export')

        col = layout.column(align=True)
        col.prop(filter, 'filter_type', icon='FILTER', expand=True)

        layout.prop(filter, "reverse")


def register():
    if bpy.app.version < (3, 0, 0):
        bpy.utils.register_class(SPIO_PT_PrefPanel_283)
    else:
        bpy.utils.register_class(SPIO_PT_PrefPanel_300)
    bpy.utils.register_class(SPIO_PT_ImportPanel)
    bpy.utils.register_class(SPIO_PT_ListFilterPanel)
    bpy.utils.register_class(SPIO_PT_InstallAddon)
    bpy.utils.register_class(SPIO_PT_AssetHelper)


def unregister():
    if bpy.app.version < (3, 0, 0):
        bpy.utils.unregister_class(SPIO_PT_PrefPanel_283)
    else:
        bpy.utils.unregister_class(SPIO_PT_PrefPanel_300)
    bpy.utils.unregister_class(SPIO_PT_ImportPanel)
    bpy.utils.unregister_class(SPIO_PT_ListFilterPanel)
    bpy.utils.unregister_class(SPIO_PT_InstallAddon)
    bpy.utils.unregister_class(SPIO_PT_AssetHelper)
