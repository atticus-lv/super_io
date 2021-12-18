import bpy
import os
import sys

from .core import get_pref, MeasureTime

if sys.platform == "win32":
    from ..clipboard.windows import PowerShellClipboard as Clipboard
elif sys.platform == "darwin":
    from ..clipboard.darwin.mac import MacClipboard as Clipboard


class DynamicExport:
    def get_temp_dir(self):
        temp_dir = self.ITEM.temporary_directory
        if temp_dir == '':
            temp_dir = bpy.path.abspath(bpy.context.preferences.filepaths.temporary_directory)
            if temp_dir == '':
                # win temp file
                temp_dir = os.path.join(os.getenv('APPDATA'), os.path.pardir, 'Local', 'Temp')
        else:
            temp_dir = bpy.path.abspath(temp_dir)
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

        return temp_dir

    def get_extra_paths(self, dir):
        return [file for file in os.listdir(dir)]

    def export_single(self, context, op_callable, op_args):
        paths = []
        temp_dir = self.get_temp_dir()
        filepath = os.path.join(temp_dir, context.active_object.name + f'.{self.extension}').replace('\\', '/')
        paths.append(filepath)

        op_args.update({'filepath': filepath})
        op_callable(**op_args)

        return paths

    def export_batch(self, context, op_callable, op_args):
        paths = []
        temp_dir = self.get_temp_dir()

        src_active = context.active_object
        selected_objects = context.selected_objects.copy()

        for obj in selected_objects:
            filepath = os.path.join(temp_dir, obj.name + f'.{self.extension}').replace('\\', '/')
            paths.append(filepath)

            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = obj
            obj.select_set(True)

            op_args.update({'filepath': filepath})
            op_callable(**op_args)

        context.view_layer.objects.active = src_active

        return paths

    def invoke(self, context, event):
        self.batch_mode = True if event.alt else False
        return self.execute(context)

    def execute(self, context):
        # use pre-define index to call config
        ITEM = self.ITEM

        op_callable, op_args, op_context = ITEM.get_operator_and_args()

        if op_callable:

            temp_dir = self.get_temp_dir()
            src_file = self.get_extra_paths(temp_dir)

            with MeasureTime() as start_time:
                if self.batch_mode:
                    paths = self.export_batch(context, op_callable, op_args)
                    self.report({'INFO'},
                                f'{len(paths)} {self.extension} files has been copied to Clipboard')

                else:
                    paths = self.export_single(context, op_callable, op_args)
                    self.report({'INFO'},
                                f'{context.active_object.name}.{self.extension} has been copied to Clipboard')

                # push
                if get_pref().post_push_to_clipboard:
                    new_files = self.get_extra_paths(temp_dir)

                    extra_files = [os.path.join(temp_dir, file) for file in new_files if
                                   file not in src_file]

                    clipboard = Clipboard()
                    clipboard.push_to_clipboard(paths=extra_files)

                if get_pref().post_open_dir:
                    import subprocess
                    if sys.platform == 'darwin':
                        subprocess.check_call(['open', '--', temp_dir])
                    elif sys.platform == 'win32':
                        subprocess.check_call(['explorer', temp_dir])

                if get_pref().report_time: self.report({"INFO"},
                                                       f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        else:
            self.report({"ERROR"}, f'{op_callable} Error!!!')

        return {"FINISHED"}
