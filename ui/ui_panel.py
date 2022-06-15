import bpy
from ..ops.core import get_pref
from ..preferences.prefs import SPIO_Preference
from ..preferences.data_icon import G_ICON_ID


class SidebarSetup:
    bl_category = "SPIO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(cls, context):
        return True


class SPIO_PT_PrefPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    def draw_header(self, context):
        layout = self.layout
        layout.alignment = "LEFT"
        pref = get_pref()

        row = layout
        row = row.row(align=True)
        row.prop(pref, 'ui', expand=True, emboss=False)
        row.separator()
        row.menu('SPIO_MT_ConfigIOMenu', text='', icon='FILE_TICK')
        row.separator(factor=2)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        if pref.ui == 'SETTINGS':
            SPIO_Preference.draw_settings(pref, context, layout)
        elif pref.ui == 'CONFIG':
            SPIO_Preference.draw_config(pref, context, layout)


class SPIO_PT_PrefPanel_283(SPIO_PT_PrefPanel):
    bl_label = ' '
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return super().poll(context) and bpy.app.version < (3, 0, 0)


class SPIO_PT_PrefPanel_300(SPIO_PT_PrefPanel):
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return super().poll(context) and not bpy.app.version < (3, 0, 0)


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
        row.operator("wm.super_import", icon_value=G_ICON_ID['import'])
        row.operator("wm.super_export", icon_value=G_ICON_ID['export'])
        row.separator()


class SPIO_PT_AssetHelper(SidebarSetup, bpy.types.Panel):
    bl_label = 'Asset Helper'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return get_pref().asset_helper and bpy.app.version >= (3, 0, 0)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        subbox = layout.box()
        subbox.label(text='Active Asset Preview', icon='IMAGE_DATA')
        row = subbox.box().row()
        row.alignment = 'LEFT'
        row.label(text='Active Object')
        row.label(text=context.object.name if context.object else 'No Active Object',
                  icon='OBJECT_DATA' if context.object else 'ERROR')

        col = subbox.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene, 'spio_snapshot_resolution', slider=True)
        col.prop(context.scene, 'spio_snapshot_view', slider=True)
        col.prop(context.scene, 'spio_snapshot_render_settings', slider=True)
        subbox.operator('spio.asset_snap_shot', icon='RENDER_STILL')

        # box.operator('spio.render_hdri_preview', icon='WORLD')
        # box.operator('spio.set_asset_thumb_from_clipboard_image', icon='IMPORT')


panels = (
    SPIO_PT_PrefPanel_283,
    SPIO_PT_PrefPanel_300,
    SPIO_PT_ImportPanel,
    SPIO_PT_AssetHelper,
)


def register():
    if bpy.app.version < (3, 0, 0):
        bpy.utils.register_class(SPIO_PT_PrefPanel_283)
    else:
        bpy.utils.register_class(SPIO_PT_PrefPanel_300)

    bpy.utils.register_class(SPIO_PT_ImportPanel)
    bpy.utils.register_class(SPIO_PT_AssetHelper)


def unregister():
    if bpy.app.version < (3, 0, 0):
        bpy.utils.unregister_class(SPIO_PT_PrefPanel_283)
    else:
        bpy.utils.unregister_class(SPIO_PT_PrefPanel_300)

    bpy.utils.unregister_class(SPIO_PT_ImportPanel)
    bpy.utils.unregister_class(SPIO_PT_AssetHelper)

