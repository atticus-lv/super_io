import bpy
from bpy.props import BoolProperty


class SPIO_OT_pop_editor(bpy.types.Operator):
    """Popup shader editor window"""
    bl_idname = "spio.pop_editor"
    bl_label = "Pop Editor"

    area_type: bpy.props.StringProperty(name='Area Type', default='TEXT_EDITOR')
    editor_text: bpy.props.StringProperty(name='Editor Text', default='')

    def execute(self, context):
        # Modify scene settings
        window = context.scene.render

        ORx = window.resolution_x
        ORy = window.resolution_y
        Oscale = window.resolution_percentage

        # RX = context.preferences.addons[__package__].preferences.RX
        # RY = context.preferences.addons[__package__].preferences.RY

        window.resolution_x = 1200
        window.resolution_y = 800
        window.resolution_percentage = 100

        # Call image editor window
        bpy.ops.render.view_show('INVOKE_AREA')
        bpy.ops.screen.region_flip('INVOKE_AREA')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        # Change area type
        area.type = self.area_type
        bpy.context.space_data.show_region_ui = False
        if self.editor_text != '':
            bpy.context.space_data.text = bpy.data.texts[self.editor_text]
            bpy.ops.text.move(type='FILE_TOP')

        window.resolution_x = ORx
        window.resolution_y = ORy
        window.resolution_percentage = Oscale

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_pop_editor)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_pop_editor)
