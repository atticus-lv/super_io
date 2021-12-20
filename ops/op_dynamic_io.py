import bpy
import os
import sys
import time

from bpy.props import (EnumProperty,
                       CollectionProperty,
                       StringProperty,
                       IntProperty,
                       BoolProperty)

from .core import get_pref, MeasureTime


class IO_Base(bpy.types.Operator):
    """IO template"""

    # dependant class
    #################
    dep_classes = []  # for easier manage, helpful for batch register and un register

    # data
    #################
    clipboard = None  # clipboard data
    file_list = []  # store clipboard urls for importing
    CONFIGS = None  # config list from user preference

    # state
    ###############
    use_custom_config = False  # if there is more then one config that advance user define
    config_list_index: IntProperty()  # index for reading pref config list

    # Utils
    ###########
    def restore(self):
        self.file_list.clear()
        self.clipboard = None
        self.ext = None
        self.use_custom_config = False

    def report_time(self, start_time):
        if get_pref().report_time: self.report({"INFO"},
                                               f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')

    # Import Method
    def import_blend_default(self, context):
        """Import with default popup"""
        pass

    def import_default(self, context):
        """Import with blender's default setting"""
        pass

    # Import Method (Popup)
    ##############
    def import_custom_dynamic(self, context):
        pass

    # Export Method (Popup)
    ##############
    def export_custom_dynamic(self, context):
        pass


class DynamicImport:
    # define exec
    def execute(self, context):
        # use pre-define index to call config
        ITEM = self.ITEM

        op_callable, ops_args, op_context = ITEM.get_operator_and_args()

        if op_callable:
            with MeasureTime() as start_time:
                for file_path in self.file_list:
                    if file_path in self.match_file_op_dict: continue
                    ops_args['filepath'] = file_path
                    try:
                        if op_context:
                            op_callable(op_context, **ops_args)
                        else:
                            op_callable(**ops_args)
                    except Exception as e:
                        self.report({"ERROR"}, str(e))

                if get_pref().report_time: self.report({"INFO"},
                                                       f'{self.bl_label} Cost {round(time.time() - start_time, 5)} s')
        else:
            self.report({"ERROR"}, f'{op_callable} Error!!!')

        return {"FINISHED"}


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
            # set dict for checking overwrite obj time
            src_file = dict()
            for file in os.listdir(temp_dir):
                src_file[file] = os.path.getmtime(os.path.join(temp_dir, file))

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

                    if sys.platform == "win32":
                        from ..clipboard.windows import PowerShellClipboard as Clipboard
                    elif sys.platform == "darwin":
                        from ..clipboard.darwin.mac import MacClipboard as Clipboard

                    new_files = [file for file in os.listdir(temp_dir)]

                    extra_files = [os.path.join(temp_dir, file) for file in new_files if
                                   file not in src_file or src_file.get(file) != os.path.getmtime(
                                       os.path.join(temp_dir, file))]

                    clipboard = Clipboard()
                    clipboard.push_to_clipboard(paths=extra_files)

                if get_pref().post_open_dir:
                    import subprocess
                    if sys.platform == 'darwin':
                        subprocess.check_call(['open', '--', temp_dir])
                    elif sys.platform == 'win32':
                        subprocess.check_call(['explorer', temp_dir])

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
