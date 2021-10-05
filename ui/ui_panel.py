import bpy
from ..ops.utils import get_pref
from ..preferences import SPIO_Preference


class SidebarSetup:
    bl_category = "SPIO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {'DRAW_BOX'}


class SPIO_PT_UnitPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pref = get_pref()

        row = layout.split(factor=0.5,align = True)
        row.label(text='Super IO')
        row = row.row(align=1)
        row.prop(pref, 'ui', expand=True, text='', emboss=False)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        if pref.ui == 'SETTINGS':
            SPIO_Preference.draw_settings(pref, context, layout)
        else:
            SPIO_Preference.draw_config(pref, context, layout)


def register():
    bpy.utils.register_class(SPIO_PT_UnitPanel)


def unregister():
    bpy.utils.unregister_class(SPIO_PT_UnitPanel)
