import bpy
from ..ops.utils import get_pref
from ..preferences import SPIO_Preference
from ..ops.ops_super_import import import_icon


class SidebarSetup:
    bl_category = "SPIO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(cls, context):
        return get_pref().use_N_panel


class SPIO_PT_PrefPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Settings'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pref = get_pref()

        row = layout
        row = row.row(align=True)
        row.prop(pref, 'ui', expand=True, text='', emboss=False)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        if pref.ui == 'SETTINGS':
            SPIO_Preference.draw_settings(pref, context, layout)
            layout.operator('wm.save_userpref')
        elif pref.ui == 'CONFIG':
            SPIO_Preference.draw_config(pref, context, layout)
        elif pref.ui == 'KEYMAP':
            SPIO_Preference.draw_keymap(pref, context, layout)


class SPIO_PT_ImportPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Super Import'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.separator()
        row.operator("wm.super_import", icon_value=import_icon.get_image_icon_id())
        row.separator()


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

        col = layout.column(align=True)
        col.prop(filter, 'filter_type', icon='FILTER', expand=True)

        layout.prop(filter, "reverse")


def register():
    bpy.utils.register_class(SPIO_PT_PrefPanel)
    bpy.utils.register_class(SPIO_PT_ImportPanel)
    bpy.utils.register_class(SPIO_PT_ListFilterPanel)


def unregister():
    bpy.utils.unregister_class(SPIO_PT_PrefPanel)
    bpy.utils.unregister_class(SPIO_PT_ImportPanel)
    bpy.utils.unregister_class(SPIO_PT_ListFilterPanel)
