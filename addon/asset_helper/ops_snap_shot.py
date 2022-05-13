import os.path

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty
from .ops_mark_asset import redraw_window


# code from https://github.com/johnnygizmo/asset_snapshot/blob/main/__init__.py

class SPIO_OT_asset_snap_shot(bpy.types.Operator):
    """Snapshot Active Object"""
    bl_label = 'Snapshot from Active and Set Preview'
    bl_idname = 'spio.asset_snap_shot'

    def snapshot(self, context, ob):
        import random
        import os

        scene = context.scene
        # Save some basic settings
        hold_x = context.scene.render.resolution_x
        hold_y = context.scene.render.resolution_y
        hold_filepath = context.scene.render.filepath

        # Find objects that are hidden in viewport and hide them in render
        tempHidden = []
        for o in bpy.data.objects:
            if o.hide_get() == True:
                o.hide_render = True
                tempHidden.append(o)

        # Change Settings
        context.scene.render.resolution_y = int(scene.spio_snapshot_resolution)
        context.scene.render.resolution_x = int(scene.spio_snapshot_resolution)

        switchback = False
        if scene.spio_snapshot_view == 'CAMERA':
            if not scene.camera:
                bpy.ops.object.camera_add()
                context.view_layer.objects.active = ob  # switch back to origin active

        if bpy.ops.view3d.camera_to_view.poll():
            bpy.ops.view3d.camera_to_view()
            switchback = True

        # Ensure outputfile is set to png (temporarily, at least)
        previousFileFormat = scene.render.image_settings.file_format
        if scene.render.image_settings.file_format != 'PNG':
            scene.render.image_settings.file_format = 'PNG'

        filename = str(random.randint(0, 100000000000)) + ".png"
        filepath = str(os.path.abspath(os.path.join(os.sep, 'tmp', filename)))
        bpy.context.scene.render.filepath = filepath

        # Render File, Mark Asset and Set Image
        if scene.spio_snapshot_render_settings == 'RENDER':
            bpy.ops.render.render(write_still=True)
        else:
            bpy.ops.render.opengl(write_still=True)

        ob.asset_mark()
        override = bpy.context.copy()
        override['id'] = ob
        bpy.ops.ed.lib_id_load_custom_preview(override, filepath=filepath)

        # Unhide the objects hidden for the render
        for o in tempHidden:
            o.hide_render = False
        # Reset output file format
        scene.render.image_settings.file_format = previousFileFormat

        # Cleanup
        os.unlink(filepath)
        context.scene.render.resolution_y = hold_y
        context.scene.render.resolution_x = hold_x
        context.scene.render.filepath = hold_filepath
        if switchback:
            bpy.ops.view3d.view_camera()

    def execute(self, context):
        self.snapshot(context, context.active_object)

        redraw_window()

        return {"FINISHED"}




def register():
    bpy.utils.register_class(SPIO_OT_asset_snap_shot)

    bpy.types.Scene.spio_snapshot_view = EnumProperty(
        items=[
            ('VIEWPORT', 'Viewport', ''),
            ('CAMERA', 'Scene Camera', ''),
        ],
        name="Camera",
        description="Where to take the snapshot from",
        default='VIEWPORT'
    )

    bpy.types.Scene.spio_snapshot_render_settings = EnumProperty(
        items=[
            ('VIEWPORT', 'Viewport Shading', ''),
            ('RENDER', 'Render', ''),
        ],
        name="Type",
        default='VIEWPORT',
    )

    bpy.types.Scene.spio_snapshot_resolution = EnumProperty(
        items=[
            ('64', '64', ''),
            ('128', '128', ''),
            ('256', '256', ''),
            ('512', '512', ''),
            ('1024', '1024', ''),
        ],
        name="Resolution",
        description="Resolution to render the preview",
        default='256'
    )


def unregister():
    bpy.utils.unregister_class(SPIO_OT_asset_snap_shot)

    del bpy.types.Scene.spio_snapshot_view
    del bpy.types.Scene.spio_snapshot_render_settings
    del bpy.types.Scene.spio_snapshot_resolution
