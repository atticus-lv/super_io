import bpy
from ..ops.utils import get_pref
from ..preferences import SPIO_Preference
from ..ops.ops_super_import import import_icon


class SidebarSetup:
    bl_category = "SPIO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {'DRAW_BOX'}


class SPIO_PT_PrefPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pref = get_pref()

        row =layout
        row = row.row(align=True)
        row.prop(pref, 'ui', expand=True, text='', emboss=False)

        row.separator(factor=2)
        row.operator('spio.config_import', icon='IMPORT', text='')
        row.operator('spio.config_export', icon='EXPORT', text='')

        row.separator()
        row.operator('wm.save_userpref')

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        if pref.ui == 'SETTINGS':
            SPIO_Preference.draw_settings(pref, context, layout)
        else:
            SPIO_Preference.draw_config(pref, context, layout)

class SPIO_PT_ImportPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Super Import'

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.separator()
        row.operator("view3d.spio_import", icon_value=import_icon.get_image_icon_id())
        row.separator()

def register():
    bpy.utils.register_class(SPIO_PT_PrefPanel)
    bpy.utils.register_class(SPIO_PT_ImportPanel)


def unregister():
    bpy.utils.unregister_class(SPIO_PT_PrefPanel)
    bpy.utils.unregister_class(SPIO_PT_ImportPanel)
