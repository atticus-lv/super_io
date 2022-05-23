import bpy
import os
from subprocess import run
from ...preferences.prefs import get_pref


class SPIO_OT_batch_image_operate(bpy.types.Operator):
    bl_idname = "spio.batch_image_operate"
    bl_label = "Batch Image Operate"
    bl_description = "Convert / Crop / Resize Image from Clipboard"
    bl_options = {'INTERNAL', 'UNDO'}

    resolution: bpy.props.EnumProperty(name='Resolution', items=[
        ('128', '128', ''),
        ('256', '256', ''),
        ('512', '512', ''),
    ], default='256')

    scale: bpy.props.EnumProperty(name='Crop', items=[
        ('1', '1:1', ''),
        ('1.5', '3:2', ''),
        ('1.778', '16:9', ''),
    ], default='1')

    re_generate: bpy.props.BoolProperty(name='Regenerate', description='When there exist preview, regenerate it',
                                        default=True)
    skip_big_image: bpy.props.BoolProperty(name='Skip big image', description='Heavy image file(>20MB) will be skipped',
                                           default=False)
    suffix: bpy.props.StringProperty(name='Suffix', default='_resize')

    color_space: bpy.props.EnumProperty(name='Color Space',
                                        items=[
                                            ('Standard', 'Standard', ''),
                                            ('Filmic', 'Filmic', ''),
                                            ('Filmic Log', 'Filmic Log', ''),
                                            ('Raw', 'Raw', ''),
                                            ('False Color', 'False Color', ''),
                                        ])

    # copy_after_resize: bpy.props.BoolProperty(name='Copy after generate (Only Win)',
    #                                           description='Copy files to clipboard after generate', default=True)

    filepaths = None
    clipboard = None

    def invoke(self, context, event):
        self.filepaths = None

        from ...clipboard.clipboard import Clipboard
        self.clipboard = Clipboard()

        filepaths = self.clipboard.pull_files_from_clipboard(get_pref().force_unicode)
        if len(filepaths) == 0:
            self.report({'ERROR'}, 'No file found in clipboard!')
            return {'CANCELLED'}

        self.filepaths = filepaths
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        layout.label(text=f'{len(self.filepaths)}', icon='DUPLICATE')

        box = layout.column(align = True).box()
        box.use_property_split = True
        box.prop(self, 'resolution')
        box.prop(self, 'color_space')
        box.prop(self, 'scale')
        box.prop(self, 're_generate')
        box.prop(self, 'skip_big_image')
        box.prop(self, 'suffix')
        # box.prop(self, 'copy_after_resize')
        layout.label(text='This could take a few minutes', icon='INFO')

    def execute(self, context):
        scripts_path = os.path.join(os.path.dirname(__file__),
                                    os.path.pardir,
                                    'imexporter',
                                    'script_resize_image.py')

        for filepath in self.filepaths:
            name = os.path.basename(filepath)
            base, stp, ext = name.rpartition('.')

            out_jpg = os.path.join(os.path.dirname(filepath), base + self.suffix + '.' + 'jpg')

            if os.path.exists(out_jpg) and not self.re_generate: continue
            if os.path.getsize(filepath) / 1024 / 1024 > 20 and self.skip_big_image: continue

            try:
                cmd = [bpy.app.binary_path]
                cmd.append("--background")
                cmd.append("--factory-startup")
                cmd.append("--python")
                cmd.append(scripts_path)
                cmd.append('--')
                cmd.append(filepath)
                cmd.append(out_jpg)
                cmd.append(self.resolution)
                cmd.append(self.scale)
                cmd.append(self.color_space)
                run(cmd)
            except Exception as e:
                print(f'Resize image "{name}" failed:', e)

        # if self.copy_after_resize:
        #     self.clipboard.push_to_clipboard(self.filepaths)

        bpy.ops.wm.path_open(filepath=os.path.dirname(self.filepaths[0]))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_batch_image_operate)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_batch_image_operate)
