import bpy
import os
import sys

from bpy.props import StringProperty, BoolProperty, EnumProperty

from .core import get_pref, PostProcess


class ModeCopyDefault:
    @classmethod
    def poll(_cls, context):
        if sys.platform in {"darwin", "win32"}:
            return (
                    context.area.type == "VIEW_3D"
                    and context.active_object is not None
                    and context.active_object.mode == 'OBJECT'
                    and len(context.selected_objects) != 0
            )


class SPIO_OT_export_model(ModeCopyDefault, bpy.types.Operator):
    """Export Selected objects to file and copy to clipboard\nAlt to export every object to a single file"""
    bl_idname = 'spio.export_model'
    bl_label = 'Copy Model'

    extension: StringProperty()
    batch_mode: BoolProperty(default=False)

    def get_temp_dir(self):
        ori_dir = bpy.context.preferences.filepaths.temporary_directory
        temp_dir = ori_dir
        if ori_dir == '':
            # win temp file
            temp_dir = os.path.join(os.path.expanduser('~'), 'spio_temp')
            if not "spio_temp" in os.listdir(os.path.expanduser('~')):
                os.makedirs(temp_dir)

        return temp_dir

    def export_batch(self, context, op_callable, op_args, target_dir):
        paths = []

        src_active = context.active_object
        selected_objects = context.selected_objects.copy()

        for obj in selected_objects:
            filepath = os.path.join(target_dir, obj.name + f'.{self.extension}')
            paths.append(filepath)

            context.view_layer.objects.active = obj
            obj.select_set(True)

            op_args.update({'filepath': filepath})
            op_callable(**op_args)
            obj.select_set(False)

        context.view_layer.objects.active = src_active

        return paths

    def export_single(self, context, op_callable, op_args, target_dir):
        paths = []
        filepath = os.path.join(target_dir, context.active_object.name + f'.{self.extension}')
        paths.append(filepath)

        op_args.update({'filepath': filepath})
        op_callable(**op_args)

        return paths

    def invoke(self, context, event):
        self.batch_mode = True if event.alt else False
        return self.execute(context)

    def execute(self, context):

        from ..imexporter.default_exporter import get_exporter, get_exporter_ops_props
        # get exporter by preferences
        default_exporter = get_exporter(cpp_obj_exporter=get_pref().cpp_obj_exporter,
                                        extend=get_pref().extend_export_menu)
        exporter_ops_props = get_exporter_ops_props(cpp_obj_exporter=get_pref().cpp_obj_exporter)

        if self.extension not in default_exporter: return {"CANCELLED"}

        temp_dir = self.get_temp_dir()
        # set dict for checking overwrite obj time
        src_file = dict()
        for file in os.listdir(temp_dir):
            src_file[file] = os.path.getmtime(os.path.join(temp_dir, file))

        bl_idname = default_exporter.get(self.extension)
        op_callable = getattr(getattr(bpy.ops, bl_idname.split('.')[0]), bl_idname.split('.')[1])

        op_args = exporter_ops_props.get(self.extension)

        if self.batch_mode:
            paths = self.export_batch(context, op_callable, op_args, temp_dir)
            self.report({'INFO'},
                        f'{len(paths)} {self.extension} files has been copied to Clipboard')

        else:
            paths = self.export_single(context, op_callable, op_args, temp_dir)
            self.report({'INFO'}, f'{context.active_object.name}.{self.extension} has been copied to Clipboard')

        # Pref
        POST = PostProcess()
        POST.copy_to_clipboard(paths=PostProcess.get_update_files(src_file, temp_dir), op=self)
        POST.open_dir(temp_dir)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_OT_export_model)


def unregister():
    bpy.utils.unregister_class(SPIO_OT_export_model)
